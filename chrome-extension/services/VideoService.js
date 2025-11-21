/**
 * Video Service
 * Handles video information fetching with caching and retry logic
 * Modern ES2022+ with private fields and AbortController
 */

import { CONFIG, AppError, ERROR_CODES } from '../config.js';
import { retry, memoize } from '../utils.js';

export class VideoService {
    // Private fields
    #cache = new Map();
    #abortControllers = new Map();

    /**
     * Fetch video information from YouTube
     * @param {string} videoId - YouTube video ID
     * @param {Object} options - Fetch options
     * @returns {Promise<Object>} Video information
     */
    async fetchVideoInfo(videoId, { useCache = true, signal } = {}) {
        // Check cache
        if (useCache && this.#cache.has(videoId)) {
            return this.#cache.get(videoId);
        }

        // Create abort controller if not provided
        const controller = signal ? null : new AbortController();
        const fetchSignal = signal ?? controller?.signal;

        if (controller) {
            this.#abortControllers.set(videoId, controller);
        }

        try {
            const videoInfo = await retry(async () => {
                const oEmbedUrl = this.#buildOEmbedUrl(videoId);

                const response = await fetch(oEmbedUrl, {
                    signal: fetchSignal,
                    headers: {
                        'Accept': 'application/json',
                    },
                });

                if (!response.ok) {
                    if (response.status === 404) {
                        throw new AppError(
                            'Video not found',
                            ERROR_CODES.VIDEO_NOT_FOUND
                        );
                    }
                    throw new AppError(
                        `Failed to fetch video info: ${response.statusText}`,
                        ERROR_CODES.NETWORK_ERROR
                    );
                }

                return await response.json();
            });

            const processedInfo = this.#processVideoInfo(videoId, videoInfo);

            // Cache the result
            this.#cache.set(videoId, processedInfo);

            return processedInfo;
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new AppError('Request cancelled', ERROR_CODES.NETWORK_ERROR, error);
            }
            throw error;
        } finally {
            if (controller) {
                this.#abortControllers.delete(videoId);
            }
        }
    }

    /**
     * Build oEmbed URL for video
     * @private
     * @param {string} videoId - Video ID
     * @returns {string} oEmbed URL
     */
    #buildOEmbedUrl(videoId) {
        const videoUrl = `https://www.youtube.com/watch?v=${videoId}`;
        return `${CONFIG.YOUTUBE.OEMBED_URL}?url=${encodeURIComponent(videoUrl)}&format=json`;
    }

    /**
     * Process video info from API response
     * @private
     * @param {string} videoId - Video ID
     * @param {Object} data - API response data
     * @returns {Object} Processed video info
     */
    #processVideoInfo(videoId, data) {
        return Object.freeze({
            id: videoId,
            title: data.title ?? 'Unknown Title',
            author: data.author_name ?? 'Unknown Author',
            thumbnail: data.thumbnail_url ?? this.#getFallbackThumbnail(videoId),
            thumbnailHigh: `${CONFIG.YOUTUBE.THUMBNAIL_BASE}/${videoId}/maxresdefault.jpg`,
            width: data.width,
            height: data.height,
        });
    }

    /**
     * Get fallback thumbnail URL
     * @private
     * @param {string} videoId - Video ID
     * @returns {string} Thumbnail URL
     */
    #getFallbackThumbnail(videoId) {
        return `${CONFIG.YOUTUBE.THUMBNAIL_BASE}/${videoId}/hqdefault.jpg`;
    }

    /**
     * Cancel ongoing fetch for video
     * @param {string} videoId - Video ID
     */
    cancelFetch(videoId) {
        const controller = this.#abortControllers.get(videoId);
        if (controller) {
            controller.abort();
            this.#abortControllers.delete(videoId);
        }
    }

    /**
     * Clear video cache
     * @param {string} [videoId] - Specific video ID, or all if not provided
     */
    clearCache(videoId) {
        if (videoId) {
            this.#cache.delete(videoId);
        } else {
            this.#cache.clear();
        }
    }

    /**
     * Prefetch video information
     * @param {string} videoId - Video ID
     * @returns {Promise<void>}
     */
    async prefetch(videoId) {
        try {
            await this.fetchVideoInfo(videoId);
        } catch (error) {
            // Silently fail prefetch
            console.warn('Prefetch failed:', error);
        }
    }
}

// Export singleton instance
export const videoService = new VideoService();
