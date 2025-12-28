/**
 * GameState - Central state management for client
 *
 * Manages game state, applies updates/deltas, notifies listeners
 */
class GameState {
    constructor() {
        this.state = null;
        this.myPlayerName = null;
        this.listeners = new Map();
        this.history = [];
        this.maxHistory = 50;
    }

    /**
     * Apply a full state update from server
     */
    applyFullUpdate(state) {
        const isFirstUpdate = !this.state;

        // Convert fleets array to object for easier lookup
        if (state.fleets && Array.isArray(state.fleets)) {
            const fleetsObj = {};
            state.fleets.forEach(fleet => {
                fleetsObj[fleet.id] = fleet;
            });
            state.fleets = fleetsObj;
        }

        // Convert players array to object if needed
        if (state.players && Array.isArray(state.players)) {
            const playersObj = {};
            state.players.forEach(player => {
                playersObj[player.name] = player;
            });
            state.players = playersObj;
        }

        this.state = state;

        if (state.player_name) {
            this.myPlayerName = state.player_name;
        }

        // Store in history
        this._addToHistory({
            type: 'full',
            turn: state.game_turn,
            state: JSON.parse(JSON.stringify(state))
        });

        this._notifyListeners('full-update', { state, isFirstUpdate });
    }

    /**
     * Apply a delta update from server
     */
    applyDelta(delta) {
        if (!this.state) {
            console.warn('Cannot apply delta without initial state');
            return;
        }

        // Apply top-level changes
        if ('score' in delta) this.state.score = delta.score;
        if ('game_turn' in delta) this.state.game_turn = delta.game_turn;
        if ('players_ready' in delta) this.state.players_ready = delta.players_ready;
        if ('total_players' in delta) this.state.total_players = delta.total_players;
        if ('time_remaining' in delta) this.state.time_remaining = delta.time_remaining;
        if ('orders' in delta) this.state.orders = delta.orders;

        // Apply players list changes
        if (delta.players) {
            if (Array.isArray(delta.players)) {
                const playersObj = {};
                delta.players.forEach(player => {
                    playersObj[player.name] = player;
                });
                this.state.players = playersObj;
            } else {
                this.state.players = delta.players;
            }
        }

        // Apply world changes
        if (delta.worlds) {
            for (const worldId in delta.worlds) {
                this.state.worlds[worldId] = delta.worlds[worldId];
            }
        }

        // Remove worlds
        if (delta.removed_worlds) {
            delta.removed_worlds.forEach(worldId => {
                delete this.state.worlds[worldId];
            });
        }

        // Apply fleet changes
        if (delta.fleets) {
            delta.fleets.forEach(fleetData => {
                this.state.fleets[fleetData.id] = fleetData;
            });
        }

        // Remove fleets
        if (delta.removed_fleets) {
            delta.removed_fleets.forEach(fleetId => {
                delete this.state.fleets[fleetId];
            });
        }

        this._notifyListeners('delta-update', { delta });
    }

    /**
     * Apply timer tick
     */
    applyTimerTick(data) {
        if (!this.state) return;

        this.state.time_remaining = data.time_remaining;
        this.state.players_ready = data.players_ready;
        this.state.total_players = data.total_players;

        this._notifyListeners('timer-tick', data);
    }

    /**
     * Get current state
     */
    getState() {
        return this.state;
    }

    /**
     * Get specific world
     */
    getWorld(worldId) {
        return this.state?.worlds?.[worldId];
    }

    /**
     * Get specific fleet
     */
    getFleet(fleetId) {
        return this.state?.fleets?.[fleetId];
    }

    /**
     * Get my player name
     */
    getMyPlayerName() {
        return this.myPlayerName;
    }

    /**
     * Get my worlds
     */
    getMyWorlds() {
        if (!this.state || !this.myPlayerName) return [];
        return Object.values(this.state.worlds || {}).filter(
            w => w.owner === this.myPlayerName
        );
    }

    /**
     * Get my fleets
     */
    getMyFleets() {
        if (!this.state || !this.myPlayerName) return [];
        return Object.values(this.state.fleets || {}).filter(
            f => f.owner === this.myPlayerName
        );
    }

    /**
     * Subscribe to state changes
     */
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    /**
     * Unsubscribe from state changes
     */
    off(event, callback) {
        if (!this.listeners.has(event)) return;
        const callbacks = this.listeners.get(event);
        const index = callbacks.indexOf(callback);
        if (index >= 0) {
            callbacks.splice(index, 1);
        }
    }

    /**
     * Get state history
     */
    getHistory(limit = 10) {
        return this.history.slice(-limit);
    }

    /**
     * Clear all state
     */
    clear() {
        this.state = null;
        this.myPlayerName = null;
        this.history = [];
    }

    // Private methods

    _notifyListeners(event, data) {
        const callbacks = this.listeners.get(event) || [];
        callbacks.forEach(cb => {
            try {
                cb(data);
            } catch (e) {
                console.error(`Error in listener for ${event}:`, e);
            }
        });
    }

    _addToHistory(entry) {
        this.history.push({
            ...entry,
            timestamp: Date.now()
        });

        // Keep only recent history
        if (this.history.length > this.maxHistory) {
            this.history.shift();
        }
    }
}

// Export singleton
const gameState = new GameState();
