/**
 * Utility Functions
 * Modern ES2022+ with proper security and performance patterns
 */

import { CONFIG, AppError, ERROR_CODES } from './config.js';

/**
 * Debounce function with modern AbortController support
 * @param {Function} fn - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} Debounced function
 */
export function debounce(fn, delay = CONFIG.UI.DEBOUNCE_DELAY_MS) {
    let timeoutId = null;

    const debounced = function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(this, args), delay);
    };

    debounced.cancel = () => clearTimeout(timeoutId);

    return debounced;
}

/**
 * Sanitize string for use in filenames
 * @param {string} str - String to sanitize
 * @param {number} maxLength - Maximum length
 * @returns {string} Sanitized string
 */
export function sanitizeFilename(str, maxLength = CONFIG.VALIDATION.MAX_FILENAME_LENGTH) {
    if (!str || typeof str !== 'string') return 'download';

    return str
        .replace(CONFIG.VALIDATION.INVALID_FILENAME_CHARS, '')
        .replace(/\s+/g, '_')
        .substring(0, maxLength)
        .trim() || 'download';
}

/**
 * Sanitize HTML to prevent XSS using DOMPurify-style approach
 * @param {string} html - HTML string to sanitize
 * @returns {string} Sanitized HTML
 */
export function sanitizeHTML(html) {
    if (!html || typeof html !== 'string') return '';

    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
}

/**
 * Create text node safely (prevents XSS)
 * @param {string} text - Text content
 * @returns {Text} Text node
 */
export function createTextNode(text) {
    return document.createTextNode(text ?? '');
}

/**
 * Validate YouTube URL with modern regex
 * @param {string} url - URL to validate
 * @returns {boolean} Whether URL is valid
 */
export function isValidYouTubeUrl(url) {
    if (!url || typeof url !== 'string' || url.length > CONFIG.VALIDATION.MAX_URL_LENGTH) {
        return false;
    }

    try {
        const urlObj = new URL(url);
        const { hostname, pathname, searchParams } = urlObj;

        // Check hostname
        if (!CONFIG.YOUTUBE.HOSTNAMES.includes(hostname)) {
            return false;
        }

        // youtube.com/watch?v=ID
        if (hostname.includes('youtube.com')) {
            return pathname === CONFIG.YOUTUBE.WATCH_PATH && searchParams.has('v');
        }

        // youtu.be/ID
        if (hostname === 'youtu.be') {
            return pathname.length > 1;
        }

        return false;
    } catch {
        return false;
    }
}

/**
 * Extract video ID from YouTube URL
 * @param {string} url - YouTube URL
 * @returns {string|null} Video ID or null
 */
export function extractVideoId(url) {
    if (!isValidYouTubeUrl(url)) {
        return null;
    }

    try {
        const urlObj = new URL(url);

        // youtube.com/watch?v=ID
        if (urlObj.hostname.includes('youtube.com')) {
            return urlObj.searchParams.get('v');
        }

        // youtu.be/ID
        if (urlObj.hostname === 'youtu.be') {
            return urlObj.pathname.slice(1).split('?')[0];
        }
    } catch {
        return null;
    }

    return null;
}

/**
 * Format time ago with modern Intl API fallback
 * @param {number} timestamp - Timestamp in milliseconds
 * @returns {string} Formatted time ago string
 */
export function formatTimeAgo(timestamp) {
    const seconds = Math.floor((Date.now() - timestamp) / 1_000);

    if (seconds < 60) return 'Just now';
    if (seconds < 3_600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86_400) return `${Math.floor(seconds / 3_600)}h ago`;
    if (seconds < 604_800) return `${Math.floor(seconds / 86_400)}d ago`;

    // Use Intl.RelativeTimeFormat for longer periods
    try {
        const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
        const days = Math.floor(seconds / 86_400);

        if (days < 30) return rtf.format(-days, 'day');
        if (days < 365) return rtf.format(-Math.floor(days / 30), 'month');
        return rtf.format(-Math.floor(days / 365), 'year');
    } catch {
        return `${Math.floor(seconds / 86_400)}d ago`;
    }
}

/**
 * Memoization with WeakMap for object keys
 * @param {Function} fn - Function to memoize
 * @returns {Function} Memoized function
 */
export function memoize(fn) {
    const cache = new Map();

    return function (...args) {
        const key = JSON.stringify(args);

        if (cache.has(key)) {
            return cache.get(key);
        }

        const result = fn.apply(this, args);
        cache.set(key, result);

        return result;
    };
}

/**
 * Retry function with exponential backoff
 * @param {Function} fn - Async function to retry
 * @param {number} maxAttempts - Maximum retry attempts
 * @param {number} baseDelay - Base delay in milliseconds
 * @returns {Promise<any>} Result of function
 */
export async function retry(
    fn,
    maxAttempts = CONFIG.BACKEND.RETRY_ATTEMPTS,
    baseDelay = CONFIG.BACKEND.RETRY_DELAY_MS
) {
    let lastError;

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error;

            if (attempt < maxAttempts - 1) {
                // Exponential backoff: delay * 2^attempt
                const delay = baseDelay * Math.pow(2, attempt);
                await sleep(delay);
            }
        }
    }

    throw lastError;
}

/**
 * Sleep utility using Promise
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise<void>}
 */
export function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Generate unique ID
 * @returns {string} Unique ID
 */
export function generateId() {
    return `${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Safe JSON parse with fallback
 * @param {string} json - JSON string
 * @param {any} fallback - Fallback value
 * @returns {any} Parsed value or fallback
 */
export function safeJSONParse(json, fallback = null) {
    try {
        return JSON.parse(json);
    } catch {
        return fallback;
    }
}

/**
 * Create DocumentFragment for efficient DOM manipulation
 * @param {Array<HTMLElement>} elements - Elements to add
 * @returns {DocumentFragment}
 */
export function createFragment(elements) {
    const fragment = document.createDocumentFragment();
    elements.forEach((el) => fragment.appendChild(el));
    return fragment;
}

/**
 * Query selector with type safety
 * @param {string} selector - CSS selector
 * @param {Document|Element} context - Context to query
 * @returns {Element|null}
 */
export function $(selector, context = document) {
    return context.querySelector(selector);
}

/**
 * Query selector all with type safety
 * @param {string} selector - CSS selector
 * @param {Document|Element} context - Context to query
 * @returns {Array<Element>}
 */
export function $$(selector, context = document) {
    return Array.from(context.querySelectorAll(selector));
}

/**
 * Toggle class with optional force parameter
 * @param {Element} element - Element to toggle class on
 * @param {string} className - Class name
 * @param {boolean} [force] - Force add or remove
 */
export function toggleClass(element, className, force) {
    element?.classList.toggle(className, force);
}

/**
 * Add multiple event listeners with cleanup
 * @param {Element} element - Element to add listeners to
 * @param {Object} events - Event name to handler map
 * @returns {Function} Cleanup function
 */
export function addEventListeners(element, events) {
    const entries = Object.entries(events);

    entries.forEach(([event, handler]) => {
        element.addEventListener(event, handler);
    });

    // Return cleanup function
    return () => {
        entries.forEach(([event, handler]) => {
            element.removeEventListener(event, handler);
        });
    };
}
