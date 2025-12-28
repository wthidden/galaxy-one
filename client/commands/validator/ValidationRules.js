/**
 * ValidationRules - Specific validation logic for game commands
 */
class ValidationRules {
    constructor(gameState) {
        this.gameState = gameState;
    }

    /**
     * Check if fleet exists and is owned by player
     */
    validateFleetOwnership(fleetId) {
        const state = this.gameState.getState();
        const fleet = state.fleets?.[fleetId];

        if (!fleet) {
            return { valid: false, error: `Fleet F${fleetId} does not exist` };
        }

        if (fleet.owner !== state.player_name) {
            return { valid: false, error: `Fleet F${fleetId} is not yours (owned by ${fleet.owner})` };
        }

        return { valid: true, fleet };
    }

    /**
     * Check if world exists and is owned by player
     */
    validateWorldOwnership(worldId) {
        const state = this.gameState.getState();
        const world = state.worlds?.[worldId];

        if (!world) {
            return { valid: false, error: `World W${worldId} does not exist` };
        }

        if (world.owner !== state.player_name) {
            return { valid: false, error: `World W${worldId} is not yours (owned by ${world.owner || 'nobody'})` };
        }

        return { valid: true, world };
    }

    /**
     * Check if fleet has an exclusive order
     */
    hasExclusiveOrder(fleetId) {
        const state = this.gameState.getState();
        const orders = state.orders || [];

        return orders.some(order =>
            order.fleet_id === fleetId &&
            ['MOVE', 'FIRE', 'AMBUSH'].includes(order.type)
        );
    }

    /**
     * Get player's fleet IDs
     */
    getMyFleetIds() {
        return this.gameState.getMyFleets().map(f => f.id);
    }

    /**
     * Get player's world IDs
     */
    getMyWorldIds() {
        return this.gameState.getMyWorlds().map(w => w.id);
    }

    /**
     * Get all visible fleet IDs
     */
    getVisibleFleetIds() {
        const state = this.gameState.getState();
        return Object.keys(state.fleets || {}).map(id => parseInt(id));
    }

    /**
     * Get fleets at a specific world
     */
    getFleetsAtWorld(worldId) {
        const state = this.gameState.getState();
        return Object.values(state.fleets || {})
            .filter(f => f.world === worldId);
    }

    /**
     * Get player's fleets at a specific world
     */
    getMyFleetsAtWorld(worldId) {
        const state = this.gameState.getState();
        return Object.values(state.fleets || {})
            .filter(f => f.world === worldId && f.owner === state.player_name);
    }

    /**
     * Get hostile fleets at a specific world
     */
    getHostileFleetsAtWorld(worldId) {
        const state = this.gameState.getState();
        return Object.values(state.fleets || {})
            .filter(f => f.world === worldId && f.owner !== state.player_name);
    }

    /**
     * Validate path connectivity (basic check)
     */
    validatePathConnectivity(startWorld, path) {
        const state = this.gameState.getState();
        let currentWorld = startWorld;

        for (const nextWorld of path) {
            const world = state.worlds?.[currentWorld];
            if (!world) {
                return { valid: false, error: `World W${currentWorld} does not exist` };
            }

            // Check if next world is connected
            if (world.connections && !world.connections.includes(nextWorld)) {
                return {
                    valid: false,
                    error: `World W${currentWorld} is not connected to W${nextWorld}`
                };
            }

            currentWorld = nextWorld;
        }

        return { valid: true };
    }

    /**
     * Validate amount is positive and within bounds
     */
    validateAmount(amount, max, resourceType) {
        if (amount <= 0) {
            return { valid: false, error: `Amount must be positive` };
        }

        if (amount > max) {
            return {
                valid: false,
                error: `Insufficient ${resourceType}: need ${amount}, have ${max}`
            };
        }

        return { valid: true };
    }
}
