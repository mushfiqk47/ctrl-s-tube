/**
 * Content Script - Ctrl+S Tube Extension
 * Injects download button on YouTube pages and monitors URL changes
 * 
 * @module content
 * @author Ctrl+S Tube Team
 * @version 2.0.0
 */

import { isValidYouTubeUrl, extractVideoId } from './utils.js';

/**
 * YouTube Page Integration
 * Handles button injection and cleanup with proper resource management
 */
class YouTubePageIntegration {
    // Private fields
    #currentUrl = '';
    #currentVideoId = null;
    #downloadButton = null;
    #observer = null;
    #intersectionObserver = null;
    #abortController = null;
    #isInjecting = false;

    /**
     * Initialize the integration
     */
    constructor() {
        this.#currentUrl = window.location.href;
        this.#abortController = new AbortController();
        this.#init();
    }

    /**
     * Initialize page monitoring and button injection
     * @private
     */
    async #init() {
        try {
            // Initial button injection
            await this.#checkAndInjectButton();

            // Set up URL change monitoring
            this.#setupUrlMonitoring();

            // Set up visibility monitoring for performance
            this.#setupVisibilityMonitoring();

            // Handle cleanup on page unload
            this.#setupCleanup();
        } catch (error) {
            console.error('YouTube integration initialization error:', error);
        }
    }

    /**
     * Set up URL monitoring using MutationObserver
     * @private
     */
    #setupUrlMonitoring() {
        // Use MutationObserver to detect URL changes in SPA
        this.#observer = new MutationObserver(() => {
            if (window.location.href !== this.#currentUrl) {
                this.#currentUrl = window.location.href;
                this.#handleUrlChange();
            }
        });

        // Observe only necessary changes to minimize overhead
        this.#observer.observe(document.body, {
            childList: true,
            subtree: false, // Don't observe ALL descendants
        });
    }

    /**
     * Set up visibility monitoring using Intersection Observer
     * Pause/resume monitoring when tab is not visible
     * @private
     */
    #setupVisibilityMonitoring() {
        document.addEventListener(
            'visibilitychange',
            () => {
                if (document.hidden) {
                    // Tab is hidden, pause expensive operations
                    this.#observer?.disconnect();
                } else {
                    // Tab is visible again, resume
                    this.#setupUrlMonitoring();
                    this.#checkAndInjectButton();
                }
            },
            { signal: this.#abortController.signal }
        );
    }

    /**
     * Set up cleanup on page unload
     * @private
     */
    #setupCleanup() {
        window.addEventListener(
            'beforeunload',
            () => this.#cleanup(),
            { signal: this.#abortController.signal }
        );
    }

    /**
     * Handle URL changes
     * @private
     */
    async #handleUrlChange() {
        // Extract video ID from new URL
        const videoId = isValidYouTubeUrl(this.#currentUrl)
            ? extractVideoId(this.#currentUrl)
            : null;

        // Only re-inject if video ID changed
        if (videoId !== this.#currentVideoId) {
            this.#currentVideoId = videoId;

            // Remove existing button
            this.#removeButton();

            // Inject new button with delay for DOM stability
            if (videoId) {
                setTimeout(() => this.#checkAndInjectButton(), 1000);
            }
        }
    }

    /**
     * Check if we should inject and inject the button
     * @private
     */
    async #checkAndInjectButton() {
        // Prevent multiple simultaneous injections
        if (this.#isInjecting) return;

        this.#isInjecting = true;

        try {
            // Only inject on valid YouTube video pages
            if (!isValidYouTubeUrl(this.#currentUrl)) return;

            const videoId = extractVideoId(this.#currentUrl);
            if (!videoId) return;

            this.#currentVideoId = videoId;

            // Wait for target container with timeout
            const targetContainer = await this.#waitForElement(
                '#above-the-fold #top-level-buttons-computed',
                5000 // 5 second timeout
            );

            if (targetContainer && !this.#downloadButton) {
                this.#injectDownloadButton(targetContainer);
            }
        } catch (error) {
            console.warn('Button injection skipped:', error.message);
        } finally {
            this.#isInjecting = false;
        }
    }

    /**
     * Wait for an element to appear in the DOM
     * @private
     * @param {string} selector - CSS selector
     * @param {number} timeout - Timeout in milliseconds
     * @returns {Promise<HTMLElement|null>}
     */
    async #waitForElement(selector, timeout = 5000) {
        // Check if element already exists
        const existing = document.querySelector(selector);
        if (existing) return existing;

        return new Promise((resolve, reject) => {
            const observer = new MutationObserver((mutations, obs) => {
                const element = document.querySelector(selector);
                if (element) {
                    obs.disconnect();
                    clearTimeout(timeoutId);
                    resolve(element);
                }
            });

            // Set timeout
            const timeoutId = setTimeout(() => {
                observer.disconnect();
                reject(new Error(`Element ${selector} not found within ${timeout}ms`));
            }, timeout);

            // Start observing
            observer.observe(document.body, {
                childList: true,
                subtree: true,
            });
        });
    }

    /**
     * Inject download button into the page
     * @private
     * @param {HTMLElement} container - Target container element
     */
    #injectDownloadButton(container) {
        // Create button element
        this.#downloadButton = document.createElement('button');
        this.#downloadButton.id = 'ctrl-s-tube-download-btn';
        this.#downloadButton.className = 'yt-spec-button-shape-next yt-spec-button-shape-next--tonal yt-spec-button-shape-next--mono yt-spec-button-shape-next--size-m';
        this.#downloadButton.setAttribute('aria-label', 'Download with Ctrl+S Tube');
        this.#downloadButton.setAttribute('title', 'Download with Ctrl+S Tube');

        // Button content
        this.#downloadButton.innerHTML = `
            <div class="yt-spec-button-shape-next__button-text-content">
                <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor" style="margin-right: 8px;">
                    <path d="M19 12v7H5v-7H3v7c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-7h-2zm-6 .67l2.59-2.58L17 11.5l-5 5-5-5 1.41-1.41L11 12.67V3h2z"/>
                </svg>
                <span>Download</span>
            </div>
        `;

        // Add click handler with AbortController
        this.#downloadButton.addEventListener(
            'click',
            () => this.#handleDownloadClick(),
            { signal: this.#abortController.signal }
        );

        // Add custom styles
        this.#addCustomStyles();

        // Insert button into container
        container.insertBefore(this.#downloadButton, container.firstChild);

        console.log('Ctrl+S Tube: Download button injected');
    }

    /**
     * Add custom styles for the download button
     * @private
     */
    #addCustomStyles() {
        // Check if styles already exist
        if (document.getElementById('ctrl-s-tube-styles')) return;

        const styleSheet = document.createElement('style');
        styleSheet.id = 'ctrl-s-tube-styles';
        styleSheet.textContent = `
            #ctrl-s-tube-download-btn {
                margin-right: 8px;
                cursor: pointer;
                transition: all 0.2s ease;
            }

            #ctrl-s-tube-download-btn:hover {
                transform: translateY(-2px);
            }

            #ctrl-s-tube-download-btn svg {
                display: inline-block;
                vertical-align: middle;
            }

            #ctrl-s-tube-download-btn span {
                font-weight: 500;
            }
        `;

        document.head.appendChild(styleSheet);
    }

    /**
     * Remove download button
     * @private
     */
    #removeButton() {
        if (this.#downloadButton) {
            this.#downloadButton.remove();
            this.#downloadButton = null;
        }
    }

    /**
     * Handle download button click
     * @private
     */
    #handleDownloadClick() {
        // Send message to background script to open popup
        chrome.runtime.sendMessage(
            { action: 'openPopup' },
            (response) => {
                if (chrome.runtime.lastError) {
                    console.error('Failed to open popup:', chrome.runtime.lastError);
                } else {
                    console.log('Popup opened successfully');
                }
            }
        );
    }

    /**
     * Clean up resources
     * @private
     */
    #cleanup() {
        // Disconnect observers
        this.#observer?.disconnect();
        this.#observer = null;

        this.#intersectionObserver?.disconnect();
        this.#intersectionObserver = null;

        // Abort all event listeners
        this.#abortController?.abort();
        this.#abortController = null;

        // Remove button
        this.#removeButton();

        console.log('Ctrl+S Tube: Cleanup completed');
    }

    /**
     * Destroy instance and clean up
     */
    destroy() {
        this.#cleanup();
    }
}

// Initialize integration
let integration = null;

try {
    integration = new YouTubePageIntegration();
} catch (error) {
    console.error('Failed to initialize Ctrl+S Tube integration:', error);
}

// Export for cleanup if needed
window.__ctrlSTubeIntegration = integration;
