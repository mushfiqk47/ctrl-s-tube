/**
 * History Service
 * Optimized history management using Map for O(1) lookups
 * Modern ES2022+ with private fields
 */

import { CONFIG, AppError, ERROR_CODES } from '../config.js';
import { storageService } from './StorageService.js';
import { generateId } from '../utils.js';

export class HistoryService {
    // Private fields - using Map for O(1) lookups
    #historyMap = new Map();
    #historyArray = [];
    #maxItems = CONFIG.DOWNLOAD.MAX_HISTORY_ITEMS;

    /**
     * Initialize history from storage
     * @returns {Promise<void>}
     */
    async init() {
        try {
            const history = await storageService.get(
                CONFIG.STORAGE.DOWNLOAD_HISTORY,
                []
            );

            // Convert to Map for O(1) lookups
            this.#historyArray = history;
            this.#historyMap.clear();

            for (const item of history) {
                this.#historyMap.set(item.id, item);
            }
        } catch (error) {
            console.error('Failed to load history:', error);
            this.#historyArray = [];
            this.#historyMap.clear();
        }
    }

    /**
     * Add item to history
     * @param {Object} item - History item
     * @returns {Promise<void>}
     */
    async addItem(item) {
        const historyItem = {
            id: item.id ?? generateId(),
            filename: item.filename,
            folder: item.folder,
            timestamp: item.timestamp ?? Date.now(),
            status: item.status ?? 'downloading',
            downloadId: item.downloadId,
        };

        // Add to map and array (prepend for most recent first)
        this.#historyMap.set(historyItem.id, historyItem);
        this.#historyArray.unshift(historyItem);

        // Trim to max items
        if (this.#historyArray.length > this.#maxItems) {
            const removed = this.#historyArray.splice(this.#maxItems);
            for (const item of removed) {
                this.#historyMap.delete(item.id);
            }
        }

        await this.#persist();
    }

    /**
     * Update history item status
     * @param {string} id - Item ID
     * @param {string} status - New status
     * @returns {Promise<boolean>} Whether item was found and updated
     */
    async updateItemStatus(id, status) {
        const item = this.#historyMap.get(id);

        if (!item) {
            return false;
        }

        item.status = status;
        await this.#persist();
        return true;
    }

    /**
     * Get item by ID - O(1) lookup
     * @param {string} id - Item ID
     * @returns {Object|null} History item
     */
    getItem(id) {
        return this.#historyMap.get(id) ?? null;
    }

    /**
     * Get all history items
     * @param {number} [limit] - Maximum number of items to return
     * @returns {Array<Object>} History items
     */
    getAll(limit) {
        if (limit) {
            return this.#historyArray.slice(0, limit);
        }
        return [...this.#historyArray];
    }

    /**
     * Get recent history items
     * @param {number} count - Number of items to return
     * @returns {Array<Object>} Recent history items
     */
    getRecent(count = 10) {
        return this.#historyArray.slice(0, count);
    }

    /**
     * Clear all history
     * @returns {Promise<void>}
     */
    async clear() {
        this.#historyArray = [];
        this.#historyMap.clear();
        await this.#persist();
    }

    /**
     * Remove specific item
     * @param {string} id - Item ID
     * @returns {Promise<boolean>} Whether item was found and removed
     */
    async removeItem(id) {
        const item = this.#historyMap.get(id);

        if (!item) {
            return false;
        }

        this.#historyMap.delete(id);
        const index = this.#historyArray.findIndex((i) => i.id === id);
        if (index !== -1) {
            this.#historyArray.splice(index, 1);
        }

        await this.#persist();
        return true;
    }

    /**
     * Get history count
     * @returns {number} Number of items in history
     */
    get count() {
        return this.#historyArray.length;
    }

    /**
     * Check if history is empty
     * @returns {boolean} Whether history is empty
     */
    get isEmpty() {
        return this.#historyArray.length === 0;
    }

    /**
     * Persist history to storage
     * @private
     * @returns {Promise<void>}
     */
    async #persist() {
        try {
            await storageService.set(
                CONFIG.STORAGE.DOWNLOAD_HISTORY,
                this.#historyArray
            );
        } catch (error) {
            console.error('Failed to persist history:', error);
            throw new AppError(
                'Failed to save download history',
                ERROR_CODES.STORAGE_ERROR,
                error
            );
        }
    }

    /**
     * Find items by status
     * @param {string} status - Status to filter by
     * @returns {Array<Object>} Matching items
     */
    findByStatus(status) {
        return this.#historyArray.filter((item) => item.status === status);
    }

    /**
     * Get download by Chrome download ID
     * @param {number} downloadId - Chrome download ID
     * @returns {Object|null} History item
     */
    getByDownloadId(downloadId) {
        return this.#historyArray.find((item) => item.downloadId === downloadId) ?? null;
    }
}

// Export singleton instance
export const historyService = new HistoryService();
