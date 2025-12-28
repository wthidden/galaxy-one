/**
 * CommandHistory - Manage command history with arrow key navigation
 */
class CommandHistory {
    constructor(maxSize = 100) {
        this.maxSize = maxSize;
        this.history = [];
        this.position = -1;
        this.storage = new HistoryStorage('starweb_command_history');
        this.load();
    }

    /**
     * Add a command to history
     */
    add(command) {
        // Don't add empty commands
        if (!command || command.trim().length === 0) {
            return;
        }

        // Don't add duplicates of the last command
        if (this.history.length > 0 && this.history[this.history.length - 1] === command) {
            this.position = -1;
            return;
        }

        this.history.push(command);

        // Trim to max size
        if (this.history.length > this.maxSize) {
            this.history.shift();
        }

        this.position = -1;
        this.save();
    }

    /**
     * Navigate history (arrow up/down)
     *
     * @param {string} direction - 'up' or 'down'
     * @returns {string|null} - Command from history or null
     */
    navigate(direction) {
        if (this.history.length === 0) {
            return null;
        }

        if (direction === 'up') {
            // Go backwards in history
            if (this.position === -1) {
                this.position = this.history.length - 1;
            } else if (this.position > 0) {
                this.position--;
            }
        } else if (direction === 'down') {
            // Go forwards in history
            if (this.position === -1) {
                return null;
            }

            if (this.position < this.history.length - 1) {
                this.position++;
            } else {
                this.position = -1;
                return null;
            }
        }

        return this.position === -1 ? null : this.history[this.position];
    }

    /**
     * Get recent commands
     */
    getRecent(count = 10) {
        return this.history.slice(-count);
    }

    /**
     * Clear all history
     */
    clear() {
        this.history = [];
        this.position = -1;
        this.save();
    }

    /**
     * Reset navigation position
     */
    reset() {
        this.position = -1;
    }

    /**
     * Save history to storage
     */
    save() {
        this.storage.save(this.history);
    }

    /**
     * Load history from storage
     */
    load() {
        const loaded = this.storage.load();
        if (loaded && Array.isArray(loaded)) {
            this.history = loaded.slice(-this.maxSize);
        }
    }
}
