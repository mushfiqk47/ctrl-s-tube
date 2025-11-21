/**
 * Background Service Worker - Ctrl+S Tube Extension
 * Handles extension lifecycle, context menus, and message routing
 * 
 * @module background
 * @author Ctrl+S Tube Team
 * @version 2.0.0
 */

import { CONFIG, AppError, ERROR_CODES } from './config.js';
import { isValidYouTubeUrl, extractVideoId } from './utils.js';

/**
 * Message action types
 * @enum {string}
 */
const MessageActions = Object.freeze({
    OPEN_POPUP: 'openPopup',
    GET_VIDEO_INFO: 'getVideoInfo',
    DOWNLOAD_VIDEO: 'downloadVideo',
});

/**
 * Context menu IDs
 * @enum {string}
 */
const ContextMenuIds = Object.freeze({
    DOWNLOAD_VIDEO: 'download-video',
});

/**
 * Initialize extension on install/update
 */
chrome.runtime.onInstalled.addListener(async (details) => {
    console.log(`Ctrl+S Tube extension ${details.reason}`);

    try {
        await setupContextMenus();

        if (details.reason === 'install') {
            // Set default settings on first install
            await chrome.storage.sync.set({
                downloadFolder: CONFIG.DOWNLOAD.DEFAULT_FOLDER,
            });
        }
    } catch (error) {
        console.error('Installation error:', error);
    }
});

/**
 * Set up context menus
 */
async function setupContextMenus() {
    // Remove existing menus first
    await chrome.contextMenus.removeAll();

    // Create download context menu for YouTube pages
    chrome.contextMenus.create({
        id: ContextMenuIds.DOWNLOAD_VIDEO,
        title: 'Download with Ctrl+S Tube',
        contexts: ['page', 'link'],
        documentUrlPatterns: [
            'https://www.youtube.com/watch*',
            'https://www.youtube.com/shorts/*',
            'https://m.youtube.com/watch*',
        ],
    });
}

/**
 * Handle context menu clicks
 */
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === ContextMenuIds.DOWNLOAD_VIDEO) {
        // Open extension popup
        chrome.action.openPopup().catch((error) => {
            console.error('Failed to open popup:', error);
        });
    }
});

/**
 * Handle messages from content scripts and popup
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    // Validate message structure
    if (!request || typeof request.action !== 'string') {
        sendResponse({
            success: false,
            error: 'Invalid message format'
        });
        return false;
    }

    // Security: Validate sender for sensitive actions
    if (!sender.tab && request.action !== MessageActions.OPEN_POPUP) {
        console.warn('Message from unknown sender:', sender);
    }

    // Route message to appropriate handler
    switch (request.action) {
        case MessageActions.OPEN_POPUP:
            handleOpenPopup(sendResponse);
            return false; // Synchronous response

        case MessageActions.GET_VIDEO_INFO:
            handleVideoInfoRequest(request.videoId)
                .then(sendResponse)
                .catch((error) => sendResponse({
                    success: false,
                    error: error.message
                }));
            return true; // Asynchronous response

        case MessageActions.DOWNLOAD_VIDEO:
            handleDownloadRequest(request)
                .then(sendResponse)
                .catch((error) => sendResponse({
                    success: false,
                    error: error.message
                }));
            return true; // Asynchronous response

        default:
            console.warn('Unknown message action:', request.action);
            sendResponse({
                success: false,
                error: 'Unknown action'
            });
            return false;
    }
});

/**
 * Handle open popup request
 * @param {Function} sendResponse - Response callback
 */
function handleOpenPopup(sendResponse) {
    chrome.action.openPopup()
        .then(() => sendResponse({ success: true }))
        .catch((error) => sendResponse({
            success: false,
            error: error.message
        }));
}

/**
 * Handle video info request using YouTube oEmbed API
 * @param {string} videoId - YouTube video ID
 * @returns {Promise<Object>} Video information
 */
async function handleVideoInfoRequest(videoId) {
    // Validate input
    if (!videoId || typeof videoId !== 'string') {
        throw new AppError(
            'Invalid video ID',
            ERROR_CODES.VALIDATION_ERROR,
            { videoId }
        );
    }

    try {
        // Use oEmbed API for video information
        const oEmbedUrl = new URL('https://www.youtube.com/oembed');
        oEmbedUrl.searchParams.set('url', `https://www.youtube.com/watch?v=${videoId}`);
        oEmbedUrl.searchParams.set('format', 'json');

        const controller = new AbortController();
        const timeoutId = setTimeout(
            () => controller.abort(),
            CONFIG.API.TIMEOUT
        );

        try {
            const response = await fetch(oEmbedUrl.toString(), {
                signal: controller.signal,
            });

            if (!response.ok) {
                throw new AppError(
                    'Failed to fetch video information',
                    ERROR_CODES.API_ERROR,
                    { status: response.status, statusText: response.statusText }
                );
            }

            const data = await response.json();

            return {
                success: true,
                data: {
                    id: videoId,
                    title: data.title,
                    author: data.author_name,
                    thumbnail: data.thumbnail_url,
                    thumbnailHigh: `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`,
                },
            };
        } finally {
            clearTimeout(timeoutId);
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            throw new AppError(
                'Request timeout',
                ERROR_CODES.TIMEOUT_ERROR
            );
        }

        throw error instanceof AppError
            ? error
            : new AppError(
                error.message,
                ERROR_CODES.API_ERROR,
                { originalError: error }
            );
    }
}

/**
 * Handle download request
 * @param {Object} request - Download request data
 * @returns {Promise<Object>} Download status
 * 
 * @note This requires a backend service to process YouTube downloads.
 * Options:
 * 1. Local backend server running yt-dlp
 * 2. Chrome Native Messaging to communicate with local Python app
 * 3. Third-party API service (ensure it complies with YouTube ToS)
 */
async function handleDownloadRequest(request) {
    // Validate request
    if (!request.videoId || !request.quality) {
        throw new AppError(
            'Invalid download request',
            ERROR_CODES.VALIDATION_ERROR,
            { request }
        );
    }

    // Backend integration would go here
    // For now, return a helpful error message
    throw new AppError(
        'Download functionality requires backend service',
        ERROR_CODES.NOT_IMPLEMENTED,
        {
            message: 'Please set up a backend service using yt-dlp or similar tool',
            documentation: 'See README.md for setup instructions'
        }
    );
}

/**
 * Handle storage changes and broadcast to all extension contexts
 */
chrome.storage.onChanged.addListener((changes, namespace) => {
    for (const [key, { oldValue, newValue }] of Object.entries(changes)) {
        console.log(
            `Storage key "${key}" in "${namespace}" changed:`,
            { oldValue, newValue }
        );

        // Broadcast setting changes to all tabs if needed
        if (namespace === 'sync' && key === 'downloadFolder') {
            chrome.runtime.sendMessage({
                action: 'settingsUpdated',
                key,
                value: newValue,
            }).catch(() => {
                // Ignore errors if popup is closed
            });
        }
    }
});

/**
 * Error boundary for uncaught errors
 */
self.addEventListener('error', (event) => {
    console.error('Uncaught error in service worker:', event.error);
    event.preventDefault();
});

/**
 * Error boundary for unhandled promise rejections
 */
self.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection in service worker:', event.reason);
    event.preventDefault();
});
