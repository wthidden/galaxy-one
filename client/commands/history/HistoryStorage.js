/**
 * HistoryStorage - LocalStorage persistence for command history
 */
class HistoryStorage {
    constructor(key) {
        this.key = key;
    }

    /**
     * Save history to LocalStorage
     */
    save(data) {
        try {
            localStorage.setItem(this.key, JSON.stringify(data));
        } catch (e) {
            console.error('Failed to save command history:', e);
        }
    }

    /**
     * Load history from LocalStorage
     */
    load() {
        try {
            const data = localStorage.getItem(this.key);
            return data ? JSON.parse(data) : null;
        } catch (e) {
            console.error('Failed to load command history:', e);
            return null;
        }
    }

    /**
     * Clear history from LocalStorage
     */
    clear() {
        try {
            localStorage.removeItem(this.key);
        } catch (e) {
            console.error('Failed to clear command history:', e);
        }
    }
}
