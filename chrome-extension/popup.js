/**
 * Popup Application - Ctrl+S Tube
 * Production-grade Chrome Extension with modern ES2022+ patterns
 * 
 * @module popup
 * @author Ctrl+S Tube Team
 * @version 2.0.0
 */

import { CONFIG, AppError, ERROR_CODES } from './config.js';
import {
    debounce,
    sanitizeFilename,
    sanitizeHTML,
    createTextNode,
    isValidYouTubeUrl,
    extractVideoId,
    formatTimeAgo,
    generateId,
    createFragment,
    $,
    $$,
    toggleClass,
    addEventListeners,
} from './utils.js';
import { storageService } from './services/StorageService.js';
import { videoService } from './services/VideoService.js';
import { downloadService } from './services/DownloadService.js';
import { historyService } from './services/HistoryService.js';

/**
 * Main Application Class
 * Uses modern ES2022+ private fields and SOLID principles
 */
class YouTubeDownloaderApp {
    // Private fields for encapsulation
    #elements = {};
    #state = {
        currentVideoId: null,
        currentVideoInfo: null,
        downloadType: 'video',
        downloadFolder: CONFIG.DOWNLOAD.DEFAULT_FOLDER,
        isDownloading: false,
    };
    #cleanupFunctions = [];
    #activeFileId = null;

    /**
     * Initialize the application
     */
    async init() {
        try {
            // Initialize elements
            this.#initElements();

            // Initialize services
            await this.#initServices();

            // Attach event listeners
            this.#attachEventListeners();

            // Load initial data
            await this.#loadInitialData();

            // Check current tab for YouTube video
            await this.#checkCurrentTab();
        } catch (error) {
            console.error('Initialization error:', error);
            this.#showStatus('Failed to initialize application', 'error');
        }
    }

    /**
     * Initialize DOM elements with null checks
     * @private
     */
    #initElements() {
        const elements = {
            // Input elements
            urlInput: $('#url-input'),
            fetchBtn: $('#fetch-btn'),

            // Video info elements
            videoInfo: $('#video-info'),
            thumbnail: $('#thumbnail'),
            videoTitle: $('#video-title'),
            videoAuthor: $('#video-author'),

            // Options elements
            optionsSection: $('#options-section'),
            toggleBtns: $$('.toggle-btn'),
            qualitySelect: $('#quality-select'),

            // Download elements
            downloadBtn: $('#download-btn'),

            // Progress elements
            progressSection: $('#progress-section'),
            progressText: $('#progress-text'),
            progressPercent: $('#progress-percent'),
            progressFill: $('#progress-fill'),

            // Status message
            statusMessage: $('#status-message'),

            // Settings elements
            settingsBtn: $('#settings-btn'),
            settingsPanel: $('#settings-panel'),
            closeSettingsBtn: $('#close-settings'),
            saveSettingsBtn: $('#save-settings'),
            downloadFolderInput: $('#download-folder'),

            // History elements
            historyList: $('#history-list'),
            clearHistoryBtn: $('#clear-history-btn'),
        };

        // Validate all elements exist
        for (const [key, element] of Object.entries(elements)) {
            if (!element && !Array.isArray(element)) {
                console.warn(`Element not found: ${key}`);
            }
        }

        this.#elements = elements;
    }

    /**
     * Initialize services
     * @private
     */
    async #initServices() {
        try {
            await historyService.init();
        } catch (error) {
            console.error('Service initialization error:', error);
        }
    }

    /**
     * Attach event listeners with proper cleanup tracking
     * @private
     */
    #attachEventListeners() {
        const {
            urlInput,
            fetchBtn,
            toggleBtns,
            qualitySelect,
            downloadBtn,
            settingsBtn,
            closeSettingsBtn,
            saveSettingsBtn,
            clearHistoryBtn,
        } = this.#elements;

        // URL input with debouncing
        const debouncedValidation = debounce(() => this.#validateUrlInput(), 300);
        const cleanup1 = addEventListeners(urlInput, {
            input: debouncedValidation,
            keypress: (e) => {
                if (e.key === 'Enter') this.#handleFetch();
            },
        });
        this.#cleanupFunctions.push(cleanup1);

        // Fetch button
        fetchBtn?.addEventListener('click', () => this.#handleFetch());

        // Type toggle buttons
        toggleBtns.forEach((btn) => {
            btn.addEventListener('click', () => this.#handleTypeToggle(btn));
        });

        // Quality select
        qualitySelect?.addEventListener('change', () => this.#updateDownloadButton());

        // Download button
        downloadBtn?.addEventListener('click', () => this.#handleDownload());

        // Settings
        settingsBtn?.addEventListener('click', () => this.#toggleSettings());
        closeSettingsBtn?.addEventListener('click', () => this.#toggleSettings());
        saveSettingsBtn?.addEventListener('click', () => this.#saveSettings());

        // History
        clearHistoryBtn?.addEventListener('click', () => this.#clearHistory());
    }

    /**
     * Load initial data
     * @private
     */
    async #loadInitialData() {
        await Promise.allSettled([
            this.#loadSettings(),
            this.#displayHistory(),
        ]);
    }

    /**
     * Validate URL input
     * @private
     */
    #validateUrlInput() {
        const url = this.#elements.urlInput?.value?.trim();

        if (!url) return;

        if (isValidYouTubeUrl(url)) {
            this.#elements.urlInput.classList.remove('error');
            this.#elements.urlInput.classList.add('valid');
        } else {
            this.#elements.urlInput.classList.remove('valid');
            this.#elements.urlInput.classList.add('error');
        }
    }

    /**
     * Toggle settings panel
     * @private
     */
    #toggleSettings() {
        toggleClass(this.#elements.settingsPanel, 'hidden');
    }

    /**
     * Load settings from storage
     * @private
     */
    async #loadSettings() {
        try {
            const folder = await storageService.getDownloadFolder();
            this.#state.downloadFolder = folder;

            if (this.#elements.downloadFolderInput) {
                this.#elements.downloadFolderInput.value = folder;
            }
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    }

    /**
     * Save settings to storage
     * @private
     */
    async #saveSettings() {
        const folder = this.#elements.downloadFolderInput?.value?.trim() || CONFIG.DOWNLOAD.DEFAULT_FOLDER;
        const sanitized = sanitizeFilename(folder);

        try {
            await storageService.setDownloadFolder(sanitized);
            this.#state.downloadFolder = sanitized;
            this.#showStatus(`Settings saved! Folder: Downloads/${sanitized}`, 'success');
            this.#toggleSettings();
        } catch (error) {
            this.#showStatus('Failed to save settings', 'error');
            console.error('Save settings error:', error);
        }
    }

    /**
     * Display download history using DocumentFragment for performance
     * @private
     */
    async #displayHistory() {
        const { historyList } = this.#elements;
        if (!historyList) return;

        // Clear existing content
        historyList.innerHTML = '';

        if (historyService.isEmpty) {
            historyList.appendChild(this.#createEmptyState());
            return;
        }

        // Get recent items and use DocumentFragment for efficient DOM manipulation
        const items = historyService.getRecent(10);
        const fragment = createFragment(items.map((item) => this.#createHistoryItem(item)));

        historyList.appendChild(fragment);
    }

    /**
     * Create empty state element
     * @private
     * @returns {HTMLElement}
     */
    #createEmptyState() {
        const div = document.createElement('div');
        div.className = 'empty-state';

        // Use textContent to prevent XSS
        const svg = this.#createElement('svg', {
            width: '48',
            height: '48',
            viewBox: '0 0 48 48',
            fill: 'none',
        });
        svg.innerHTML = `
            <path d="M24 44c11.046 0 20-8.954 20-20S35.046 4 24 4 4 12.954 4 24s8.954 20 20 20z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M24 12v12l8 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        `;

        const p = document.createElement('p');
        p.appendChild(createTextNode('No downloads yet'));

        div.appendChild(svg);
        div.appendChild(p);

        return div;
    }

    /**
     * Create history item element
     * @private
     * @param {Object} item - History item
     * @returns {HTMLElement}
     */
    #createHistoryItem(item) {
        const div = document.createElement('div');
        div.className = 'history-item';
        div.dataset.id = item.id;

        const header = document.createElement('div');
        header.className = 'history-item-header';

        const filename = document.createElement('div');
        filename.className = 'history-filename';
        filename.appendChild(createTextNode(item.filename));

        const status = document.createElement('div');
        status.className = `history-status ${item.status}`;
        status.appendChild(createTextNode(item.status));

        header.appendChild(filename);
        header.appendChild(status);

        const details = document.createElement('div');
        details.className = 'history-details';

        const location = document.createElement('div');
        location.className = 'history-location';
        location.innerHTML = `
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M10 5v4a1 1 0 01-1 1H3a1 1 0 01-1-1V5m8 0V3a1 1 0 00-1-1H3a1 1 0 00-1 1v2m8 0H2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
        `;
        const locationSpan = document.createElement('span');
        locationSpan.appendChild(createTextNode(`Downloads/${item.folder}`));
        location.appendChild(locationSpan);

        const time = document.createElement('div');
        time.className = 'history-time';
        time.appendChild(createTextNode(formatTimeAgo(item.timestamp)));

        details.appendChild(location);
        details.appendChild(time);

        div.appendChild(header);
        div.appendChild(details);

        return div;
    }

    /**
     * Clear history with confirmation
     * @private
     */
    async #clearHistory() {
        if (!confirm('Clear all download history?')) return;

        try {
            await historyService.clear();
            await this.#displayHistory();
            this.#showStatus('History cleared', 'success');
        } catch (error) {
            console.error('Clear history error:', error);
            this.#showStatus('Failed to clear history', 'error');
        }
    }

    /**
     * Check current tab for YouTube video
     * @private
     */
    async #checkCurrentTab() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

            if (tab?.url && isValidYouTubeUrl(tab.url)) {
                this.#elements.urlInput.value = tab.url;
                this.#showStatus('YouTube video detected', 'success');
            }
        } catch (error) {
            console.warn('Check current tab error:', error);
        }
    }

    /**
     * Handle fetch button click
     * @private
     */
    async #handleFetch() {
        const url = this.#elements.urlInput?.value?.trim();

        if (!url) {
            this.#showStatus('Please enter a YouTube URL', 'error');
            return;
        }

        if (!isValidYouTubeUrl(url)) {
            this.#showStatus('Invalid YouTube URL', 'error');
            return;
        }

        this.#setFetchLoading(true);

        try {
            const videoId = extractVideoId(url);

            if (!videoId) {
                throw new AppError('Invalid video ID', ERROR_CODES.INVALID_URL);
            }

            this.#state.currentVideoId = videoId;

            // Fetch video info
            const videoInfo = await videoService.fetchVideoInfo(videoId);
            this.#state.currentVideoInfo = videoInfo;

            this.#displayVideoInfo(videoInfo);
            this.#showOptions();
            this.#updateDownloadButton();

            this.#showStatus('Video information loaded', 'success');
        } catch (error) {
            console.error('Fetch error:', error);
            const message = error instanceof AppError
                ? error.message
                : 'Failed to fetch video information';
            this.#showStatus(message, 'error');
        } finally {
            this.#setFetchLoading(false);
        }
    }

    /**
     * Display video information
     * @private
     * @param {Object} info - Video info
     */
    #displayVideoInfo(info) {
        const { thumbnail, videoTitle, videoAuthor, videoInfo } = this.#elements;

        if (thumbnail) {
            thumbnail.src = info.thumbnailHigh;
            thumbnail.alt = info.title;
            thumbnail.loading = 'lazy';
        }

        if (videoTitle) {
            videoTitle.textContent = '';
            videoTitle.appendChild(createTextNode(info.title));
        }

        if (videoAuthor) {
            videoAuthor.textContent = '';
            videoAuthor.appendChild(createTextNode(info.author));
        }

        toggleClass(videoInfo, 'hidden', false);
    }

    /**
     * Show download options
     * @private
     */
    #showOptions() {
        toggleClass(this.#elements.optionsSection, 'hidden', false);
        toggleClass(this.#elements.downloadBtn, 'hidden', false);
    }

    /**
     * Handle type toggle (video/audio)
     * @private
     * @param {HTMLElement} clickedBtn - Clicked button
     */
    #handleTypeToggle(clickedBtn) {
        const type = clickedBtn?.dataset?.type;
        if (!type) return;

        // Update active state
        this.#elements.toggleBtns.forEach((btn) =>
            toggleClass(btn, 'active', btn === clickedBtn)
        );

        this.#state.downloadType = type;
        this.#updateQualityOptions(type);
        this.#updateDownloadButton();
    }

    /**
     * Update quality options based on type
     * @private
     * @param {string} type - Download type (video/audio)
     */
    #updateQualityOptions(type) {
        const select = this.#elements.qualitySelect;
        if (!select) return;

        select.innerHTML = '';

        const qualities = type === 'video'
            ? CONFIG.QUALITY.VIDEO
            : CONFIG.QUALITY.AUDIO;

        // Use DocumentFragment for efficient DOM manipulation
        const fragment = createFragment(
            qualities.map(({ value, label }) => {
                const option = document.createElement('option');
                option.value = value;
                option.appendChild(createTextNode(label));
                return option;
            })
        );

        select.appendChild(fragment);
    }

    /**
     * Update download button state
     * @private
     */
    #updateDownloadButton() {
        const { downloadBtn, qualitySelect } = this.#elements;

        if (downloadBtn) {
            downloadBtn.disabled = !(
                this.#state.currentVideoId &&
                qualitySelect?.value &&
                !this.#state.isDownloading
            );
        }
    }

    /**
     * Handle download button click
     * @private
     */
    async #handleDownload() {
        if (!this.#state.currentVideoId) {
            this.#showStatus('No video selected', 'error');
            return;
        }

        if (this.#state.isDownloading) {
            this.#showStatus('Download already in progress', 'error');
            return;
        }

        const quality = this.#elements.qualitySelect?.value;
        const type = this.#state.downloadType;

        this.#state.isDownloading = true;
        this.#elements.downloadBtn.disabled = true;

        try {
            this.#showProgress('Preparing download...', 0);

            // Request download from backend
            const fileId = await downloadService.requestDownload({
                videoId: this.#state.currentVideoId,
                quality,
                type,
            });

            this.#activeFileId = fileId;

            // Monitor progress using async generator
            for await (const progress of downloadService.monitorProgress(fileId)) {
                const message = progress.message ?? 'Downloading...';
                const percent = progress.percent ?? 0;

                this.#showProgress(message, percent);

                if (progress.status === 'error') {
                    throw new AppError(
                        progress.message ?? 'Download failed',
                        ERROR_CODES.DOWNLOAD_FAILED
                    );
                }
            }

            // Download file using Chrome API
            const filename = this.#generateFilename();
            const downloadId = await downloadService.downloadFile(
                fileId,
                filename,
                this.#state.downloadFolder
            );

            // Add to history
            await historyService.addItem({
                id: generateId(),
                filename,
                folder: this.#state.downloadFolder,
                timestamp: Date.now(),
                status: 'downloading',
                downloadId,
            });

            // Monitor Chrome download
            await this.#monitorChromeDownload(downloadId);

            this.#showStatus('Download completed!', 'success');
            await this.#displayHistory();
        } catch (error) {
            console.error(' Download error:', error);
            const message = error instanceof AppError
                ? error.message
                : 'Download failed. Please try again.';
            this.#showStatus(message, 'error');
        } finally {
            this.#hideProgress();
            this.#state.isDownloading = false;
            this.#activeFileId = null;
            this.#updateDownloadButton();
        }
    }

    /**
     * Generate filename from video info
     * @private
     * @returns {string} Sanitized filename
     */
    #generateFilename() {
        const title = this.#state.currentVideoInfo?.title ?? 'youtube_download';
        const sanitized = sanitizeFilename(title);
        const extension = this.#state.downloadType === 'video'
            ? CONFIG.DOWNLOAD.VIDEO_EXTENSION
            : CONFIG.DOWNLOAD.AUDIO_EXTENSION;

        return `${sanitized}.${extension}`;
    }

    /**
     * Monitor Chrome download progress
     * @private
     * @param {number} downloadId - Chrome download ID
     */
    async #monitorChromeDownload(downloadId) {
        try {
            await downloadService.monitorChromeDownload(downloadId);

            // Update history
            const historyItem = historyService.getByDownloadId(downloadId);
            if (historyItem) {
                await historyService.updateItemStatus(historyItem.id, 'complete');
                await this.#displayHistory();
            }
        } catch (error) {
            // Update history with failed status
            const historyItem = historyService.getByDownloadId(downloadId);
            if (historyItem) {
                await historyService.updateItemStatus(historyItem.id, 'failed');
                await this.#displayHistory();
            }
            throw error;
        }
    }

    /**
     * Show progress indicator
     * @private
     * @param {string} text - Progress text
     * @param {number} percent - Progress percentage
     */
    #showProgress(text, percent) {
        const { progressSection, progressText, progressPercent, progressFill } = this.#elements;

        toggleClass(progressSection, 'hidden', false);

        if (progressText) {
            progressText.textContent = '';
            progressText.appendChild(createTextNode(text));
        }

        if (progressPercent) {
            progressPercent.textContent = '';
            progressPercent.appendChild(createTextNode(`${Math.round(percent)}%`));
        }

        if (progressFill) {
            progressFill.style.width = `${percent}%`;
        }
    }

    /**
     * Hide progress indicator
     * @private
     */
    #hideProgress() {
        toggleClass(this.#elements.progressSection, 'hidden', true);
    }

    /**
     * Show status message
     * @private
     * @param {string} message - Status message
     * @param {string} type - Message type (success/error)
     */
    #showStatus(message, type = 'success') {
        const { statusMessage } = this.#elements;
        if (!statusMessage) return;

        statusMessage.textContent = '';
        statusMessage.appendChild(createTextNode(message));
        statusMessage.className = `status-message ${type}`;
        toggleClass(statusMessage, 'hidden', false);

        setTimeout(() => {
            toggleClass(statusMessage, 'hidden', true);
        }, CONFIG.UI.STATUS_MESSAGE_DURATION_MS);
    }

    /**
     * Set fetch button loading state
     * @private
     * @param {boolean} loading - Whether loading
     */
    #setFetchLoading(loading) {
        const { fetchBtn } = this.#elements;
        if (!fetchBtn) return;

        fetchBtn.disabled = loading;

        const span = fetchBtn.querySelector('span');
        const svg = fetchBtn.querySelector('svg');

        if (span) {
            span.textContent = '';
            span.appendChild(createTextNode(loading ? 'Fetching...' : 'Fetch'));
        }

        toggleClass(svg, 'spinning', loading);
    }

    /**
     * Helper to create element with attributes
     * @private
     * @param {string} tag - Tag name
     * @param {Object} attrs - Attributes
     * @returns {HTMLElement}
     */
    #createElement(tag, attrs = {}) {
        const el = document.createElement(tag);
        Object.entries(attrs).forEach(([key, value]) => {
            el.setAttribute(key, value);
        });
        return el;
    }

    /**
     * Cleanup method to remove event listeners
     */
    destroy() {
        this.#cleanupFunctions.forEach((cleanup) => cleanup());
        downloadService.cleanup();
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', async () => {
        const app = new YouTubeDownloaderApp();
        await app.init();

        // Store app instance for debugging
        window.__app = app;
    });
} else {
    (async () => {
        const app = new YouTubeDownloaderApp();
        await app.init();
        window.__app = app;
    })();
}
