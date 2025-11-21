/**
 * Storage Service
 * Abstracted storage layer with error handling and validation
 * Modern ES2022+ with private fields
 */

import { CONFIG, AppError, ERROR_CODES } from '../config.js';

export class StorageService {
    // Private fields
    #cache = new Map();

    /**
     * Get item from storage with caching
     * @param {string} key - Storage key
     * @param {any} defaultValue - Default value if not found
     * @param {boolean} useSync - Use sync storage instead of local
     * @returns {Promise<any>} Stored value
     */
    async get(key, defaultValue = null, useSync = false) {
        // Check cache first
        if (this.#cache.has(key)) {
            return this.#cache.get(key);
        }

        try {
            const storage = useSync ? chrome.storage.sync : chrome.storage.local;
            const result = await storage.get([key]);
            const value = result[key] ?? defaultValue;

            // Cache the result
            this.#cache.set(key, value);

            return value;
        } catch (error) {
            console.error(`Storage get error for key "${key}":`, error);
            throw new AppError(
                `Failed to retrieve ${key} from storage`,
                ERROR_CODES.STORAGE_ERROR,
                error
            );
        }
    }

    /**
     * Set item in storage with validation
     * @param {string} key - Storage key
     * @param {any} value - Value to store
     * @param {boolean} useSync - Use sync storage instead of local
     * @returns {Promise<void>}
     */
    async set(key, value, useSync = false) {
        try {
            const storage = useSync ? chrome.storage.sync : chrome.storage.local;
            await storage.set({ [key]: value });

            // Update cache
            this.#cache.set(key, value);
        } catch (error) {
            console.error(`Storage set error for key "${key}":`, error);
            throw new AppError(
                `Failed to save ${key} to storage`,
                ERROR_CODES.STORAGE_ERROR,
                error
            );
        }
    }

    /**
     * Remove item from storage
     * @param {string} key - Storage key
     * @param {boolean} useSync - Use sync storage instead of local
     * @returns {Promise<void>}
     */
    async remove(key, useSync = false) {
        try {
            const storage = useSync ? chrome.storage.sync : chrome.storage.local;
            await storage.remove(key);

            // Remove from cache
            this.#cache.delete(key);
        } catch (error) {
            console.error(`Storage remove error for key "${key}":`, error);
            throw new AppError(
                `Failed to remove ${key} from storage`,
                ERROR_CODES.STORAGE_ERROR,
                error
            );
        }
    }

    /**
     * Clear all storage
     * @param {boolean} useSync - Use sync storage instead of local
     * @returns {Promise<void>}
     */
    async clear(useSync = false) {
        try {
            const storage = useSync ? chrome.storage.sync : chrome.storage.local;
            await storage.clear();

            // Clear cache
            this.#cache.clear();
        } catch (error) {
            console.error('Storage clear error:', error);
            throw new AppError(
                'Failed to clear storage',
                ERROR_CODES.STORAGE_ERROR,
                error
            );
        }
    }

    /**
     * Get download folder setting
     * @returns {Promise<string>} Download folder name
     */
    async getDownloadFolder() {
        return this.get(
            CONFIG.STORAGE.DOWNLOAD_FOLDER,
            CONFIG.DOWNLOAD.DEFAULT_FOLDER,
            true // Use sync storage for settings
        );
    }

    /**
     * Set download folder setting
     * @param {string} folder - Folder name
     * @returns {Promise<void>}
     */
    async setDownloadFolder(folder) {
        return this.set(
            CONFIG.STORAGE.DOWNLOAD_FOLDER,
            folder,
            true // Use sync storage for settings
        );
    }

    /**
     * Invalidate cache for specific key or all
     * @param {string} [key] - Key to invalidate, or all if not provided
     */
    invalidateCache(key) {
        if (key) {
            this.#cache.delete(key);
        } else {
            this.#cache.clear();
        }
    }
}

// Export singleton instance
export const storageService = new StorageService();
