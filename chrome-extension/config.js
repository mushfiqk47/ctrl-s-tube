/**
 * Centralized Configuration
 * Modern ES2022+ with frozen objects and validation
 */

export const CONFIG = Object.freeze({
    // Backend configuration
    BACKEND: Object.freeze({
        // TODO: After deploying to Render, replace this with your production URL
        PRODUCTION_URL: 'https://ctrl-s-tube-backend.onrender.com', // Update this after deployment!
        LOCAL_URL: 'http://localhost:5000',
        DEFAULT_URL: 'http://localhost:5000', // Will auto-detect in DownloadService
        TIMEOUT_MS: 30_000,
        RETRY_ATTEMPTS: 3,
        RETRY_DELAY_MS: 1_000,
    }),

    // API endpoints
    ENDPOINTS: Object.freeze({
        HEALTH: '/health',
        DOWNLOAD: '/download',
        PROGRESS: '/progress',
        FILE: '/file',
    }),

    // Storage keys
    STORAGE: Object.freeze({
        DOWNLOAD_FOLDER: 'downloadFolder',
        DOWNLOAD_HISTORY: 'downloadHistory',
        USER_PREFERENCES: 'userPreferences',
    }),

    // Download options
    DOWNLOAD: Object.freeze({
        DEFAULT_FOLDER: 'YouTube',
        MAX_HISTORY_ITEMS: 50,
        VIDEO_FORMATS: Object.freeze(['mkv', 'mp4', 'webm']),
        AUDIO_FORMATS: Object.freeze(['m4a', 'mp3', 'opus']),
        VIDEO_EXTENSION: 'mkv',
        AUDIO_EXTENSION: 'm4a',
    }),

    // Quality options
    QUALITY: Object.freeze({
        VIDEO: Object.freeze([
            { value: 'highest', label: 'Highest Available' },
            { value: '2160', label: '2160p (4K)' },
            { value: '1440', label: '1440p (2K)' },
            { value: '1080', label: '1080p (Full HD)' },
            { value: '720', label: '720p (HD)' },
            { value: '480', label: '480p (SD)' },
            { value: '360', label: '360p' },
        ]),
        AUDIO: Object.freeze([
            { value: 'best', label: 'Best Quality (320kbps)' },
            { value: '256', label: 'High Quality (256kbps)' },
            { value: '192', label: 'Medium Quality (192kbps)' },
            { value: '128', label: 'Standard Quality (128kbps)' },
        ]),
    }),

    // YouTube URL patterns
    YOUTUBE: Object.freeze({
        HOSTNAMES: Object.freeze(['www.youtube.com', 'youtube.com', 'youtu.be', 'm.youtube.com']),
        WATCH_PATH: '/watch',
        OEMBED_URL: 'https://www.youtube.com/oembed',
        THUMBNAIL_BASE: 'https://img.youtube.com/vi',
    }),

    // UI Configuration
    UI: Object.freeze({
        DEBOUNCE_DELAY_MS: 300,
        STATUS_MESSAGE_DURATION_MS: 5_000,
        PROGRESS_POLL_INTERVAL_MS: 500,
        ANIMATION_DURATION_MS: 200,
    }),

    // Validation
    VALIDATION: Object.freeze({
        MAX_FILENAME_LENGTH: 100,
        INVALID_FILENAME_CHARS: /[<>:"/\\|?*]/g,
        MAX_URL_LENGTH: 2_048,
    }),
});

/**
 * Environment detection
 */
export const ENV = Object.freeze({
    isDevelopment: !('update_url' in chrome.runtime.getManifest()),
    extensionId: chrome.runtime.id,
    version: chrome.runtime.getManifest().version,
});

/**
 * Error codes for structured error handling
 */
export const ERROR_CODES = Object.freeze({
    BACKEND_UNAVAILABLE: 'ERR_BACKEND_UNAVAILABLE',
    INVALID_URL: 'ERR_INVALID_URL',
    NETWORK_ERROR: 'ERR_NETWORK',
    DOWNLOAD_FAILED: 'ERR_DOWNLOAD_FAILED',
    VIDEO_NOT_FOUND: 'ERR_VIDEO_NOT_FOUND',
    STORAGE_ERROR: 'ERR_STORAGE',
    VALIDATION_ERROR: 'ERR_VALIDATION',
    TIMEOUT: 'ERR_TIMEOUT',
    UNKNOWN: 'ERR_UNKNOWN',
});

/**
 * Custom error class with error codes
 */
export class AppError extends Error {
    /**
     * @param {string} message - Error message
     * @param {string} code - Error code from ERROR_CODES
     * @param {Error} [cause] - Original error
     */
    constructor(message, code = ERROR_CODES.UNKNOWN, cause = null) {
        super(message, cause ? { cause } : undefined);
        this.name = 'AppError';
        this.code = code;
        this.timestamp = Date.now();
    }
}
