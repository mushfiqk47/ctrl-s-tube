/**
 * Download Service
 * Manages downloads with proper cleanup and progress tracking
 * Modern ES2022+ with private fields and async generators
 */

import { CONFIG, AppError, ERROR_CODES } from '../config.js';
import { retry, sleep } from '../utils.js';

export class DownloadService {
    // Private fields
    #activeDownloads = new Map();
    #progressListeners = new Map();
    #backendUrl = CONFIG.BACKEND.DEFAULT_URL;
    #urlTested = false;

    constructor() {
        // Auto-detect best backend URL on first use
        this.#detectBackendUrl();
    }

    /**
     * Auto-detect which backend URL to use
     * Tries local first, falls back to production
     */
    async #detectBackendUrl() {
        // Try local first
        const localHealthy = await this.#testUrl(CONFIG.BACKEND.LOCAL_URL);
        if (localHealthy) {
            this.#backendUrl = CONFIG.BACKEND.LOCAL_URL;
            console.log('Using local backend:', this.#backendUrl);
            return;
        }

        // Fall back to production
        const prodHealthy = await this.#testUrl(CONFIG.BACKEND.PRODUCTION_URL);
        if (prodHealthy) {
            this.#backendUrl = CONFIG.BACKEND.PRODUCTION_URL;
            console.log('Using production backend:', this.#backendUrl);
            return;
        }

        // Neither works, keep default
        console.warn('No backend available, using default:', this.#backendUrl);
    }

    /**
     * Test if a URL is healthy
     * @param {string} url - URL to test
     * @returns {Promise<boolean>}
     */
    async #testUrl(url) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3_000); // Quick 3s timeout

            const response = await fetch(
                `${url}${CONFIG.ENDPOINTS.HEALTH}`,
                { signal: controller.signal }
            );

            clearTimeout(timeoutId);
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    /**
     * Check if backend is available
     * @returns {Promise<boolean>} Whether backend is available
     */
    async checkBackendHealth() {
        if (!this.#urlTested) {
            await this.#detectBackendUrl();
            this.#urlTested = true;
        }

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5_000);

            const response = await fetch(
                `${this.#backendUrl}${CONFIG.ENDPOINTS.HEALTH}`,
                { signal: controller.signal }
            );

            clearTimeout(timeoutId);
            return response.ok;
        } catch (error) {
            console.warn('Backend health check failed:', error);
            return false;
        }
    }

    /**
     * Request download from backend
     * @param {Object} options - Download options
     * @returns {Promise<string>} File ID
     */
    async requestDownload({ videoId, quality, type }) {
        // Check backend health first
        const isHealthy = await this.checkBackendHealth();
        if (!isHealthy) {
            throw new AppError(
                'Backend service is not running. Please run start_backend.bat',
                ERROR_CODES.BACKEND_UNAVAILABLE
            );
        }

        try {
            const response = await retry(async () => {
                const result = await fetch(
                    `${this.#backendUrl}${CONFIG.ENDPOINTS.DOWNLOAD}`,
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            url: `https://www.youtube.com/watch?v=${videoId}`,
                            quality,
                            type,
                        }),
                    }
                );

                if (!result.ok) {
                    const errorData = await result.json().catch(() => ({}));
                    throw new AppError(
                        errorData.error ?? 'Download request failed',
                        ERROR_CODES.DOWNLOAD_FAILED
                    );
                }

                return result;
            });

            const data = await response.json();

            if (!data.file_id) {
                throw new AppError(
                    'Invalid response from backend',
                    ERROR_CODES.DOWNLOAD_FAILED
                );
            }

            return data.file_id;
        } catch (error) {
            console.error('Download request error:', error);
            throw error;
        }
    }

    /**
     * Monitor download progress using async generator
     * @param {string} fileId - File ID from backend
     * @yields {Object} Progress updates
     */
    async *monitorProgress(fileId) {
        const controller = new AbortController();
        this.#activeDownloads.set(fileId, controller);

        try {
            while (true) {
                const response = await fetch(
                    `${this.#backendUrl}${CONFIG.ENDPOINTS.PROGRESS}/${fileId}`,
                    { signal: controller.signal }
                );

                if (!response.ok) {
                    throw new AppError(
                        'Failed to fetch progress',
                        ERROR_CODES.NETWORK_ERROR
                    );
                }

                const progress = await response.json();
                yield progress;

                // Check if complete or error
                if (progress.status === 'complete' || progress.status === 'error') {
                    break;
                }

                // Wait before next poll
                await sleep(CONFIG.UI.PROGRESS_POLL_INTERVAL_MS);
            }
        } finally {
            this.#activeDownloads.delete(fileId);
        }
    }

    /**
     * Download file using Chrome API
     * @param {string} fileId - File ID from backend
     * @param {string} filename - Filename to save as
     * @param {string} folder - Folder to save in
     * @returns {Promise<number>} Download ID
     */
    async downloadFile(fileId, filename, folder) {
        return new Promise((resolve, reject) => {
            const url = `${this.#backendUrl}${CONFIG.ENDPOINTS.FILE}/${fileId}`;
            const fullPath = folder ? `${folder}/${filename}` : filename;

            chrome.downloads.download(
                {
                    url,
                    filename: fullPath,
                    saveAs: false,
                },
                (downloadId) => {
                    if (chrome.runtime.lastError) {
                        reject(
                            new AppError(
                                chrome.runtime.lastError.message,
                                ERROR_CODES.DOWNLOAD_FAILED,
                                chrome.runtime.lastError
                            )
                        );
                    } else {
                        resolve(downloadId);
                    }
                }
            );
        });
    }

    /**
     * Monitor Chrome download progress
     * @param {number} downloadId - Chrome download ID
     * @returns {Promise<void>}
     */
    async monitorChromeDownload(downloadId) {
        return new Promise((resolve, reject) => {
            const listener = (delta) => {
                if (delta.id !== downloadId) return;

                if (delta.state?.current === 'complete') {
                    chrome.downloads.onChanged.removeListener(listener);
                    resolve();
                } else if (delta.state?.current === 'interrupted') {
                    chrome.downloads.onChanged.removeListener(listener);
                    reject(
                        new AppError(
                            'Download interrupted',
                            ERROR_CODES.DOWNLOAD_FAILED
                        )
                    );
                }
            };

            chrome.downloads.onChanged.addListener(listener);

            // Store listener for cleanup
            this.#progressListeners.set(downloadId, listener);
        });
    }

    /**
     * Cancel active download
     * @param {string} fileId - File ID
     */
    cancelDownload(fileId) {
        const controller = this.#activeDownloads.get(fileId);
        if (controller) {
            controller.abort();
            this.#activeDownloads.delete(fileId);
        }
    }

    /**
     * Cleanup listeners and abort controllers
     */
    cleanup() {
        // Abort all active downloads
        for (const controller of this.#activeDownloads.values()) {
            controller.abort();
        }
        this.#activeDownloads.clear();

        // Remove all progress listeners
        for (const [downloadId, listener] of this.#progressListeners) {
            chrome.downloads.onChanged.removeListener(listener);
        }
        this.#progressListeners.clear();
    }

    /**
     * Get download URL for file
     * @param {string} fileId - File ID
     * @returns {string} Download URL
     */
    getDownloadUrl(fileId) {
        return `${this.#backendUrl}${CONFIG.ENDPOINTS.FILE}/${fileId}`;
    }
}

// Export singleton instance
export const downloadService = new DownloadService();
