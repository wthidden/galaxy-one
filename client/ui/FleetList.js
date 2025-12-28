/**
 * FleetList - Displays player's fleets
 */
class FleetList {
    constructor(elementId) {
        this.element = document.getElementById(elementId);
        this.onFleetClick = null;
    }

    /**
     * Update fleet list with current game state
     */
    update(gameState) {
        if (!this.element || !gameState.fleets || !gameState.player_name) return;

        // Get player's fleets
        const myFleets = Object.values(gameState.fleets)
            .filter(f => f.owner === gameState.player_name);

        if (myFleets.length === 0) {
            this.element.innerHTML = '<div class="fleet-list"><div class="empty-message">No fleets</div></div>';
            return;
        }

        // Group fleets by world
        const fleetsByWorld = this._groupFleetsByWorld(myFleets);

        // Sort worlds: conflict worlds first, then by world ID
        const sortedWorlds = this._sortWorldsByConflict(fleetsByWorld, gameState);

        // Build HTML
        let html = '<div class="fleet-list">';

        sortedWorlds.forEach(({ worldId, fleets, hasConflict }) => {
            // World header
            const worldName = this._getWorldName(worldId, gameState);
            const conflictIndicator = hasConflict ? ' ⚔️' : '';

            html += `
                <div class="fleet-world-group ${hasConflict ? 'conflict' : ''}">
                    <div class="world-header">${worldName}${conflictIndicator}</div>
            `;

            // Sort fleets by ID within group
            fleets.sort((a, b) => a.id - b.id);

            fleets.forEach(fleet => {
                const ships = fleet.ships || 0;
                const cargo = fleet.cargo || 0;
                const isMoving = fleet.path && fleet.path.length > 0;
                const isEmpty = ships <= 0;
                const artifacts = fleet.artifacts || [];

                // Build artifact list
                let artifactStr = '';
                if (artifacts.length > 0) {
                    const artifactIds = artifacts.map(a => `A${a.id}`).join(', ');
                    artifactStr = `<span class="artifact-list" title="Artifacts: ${artifactIds}">✨${artifacts.length}</span>`;
                }

                html += `
                    <div class="fleet-entry ${isEmpty ? 'empty-fleet' : ''}" data-fleet-id="${fleet.id}">
                        <div class="fleet-header">
                            <span class="fleet-id">F${fleet.id}</span>
                            ${isEmpty ? '<span class="empty-icon" title="Empty (no ships)">⚪</span>' : ''}
                            ${isMoving ? '<span class="moving-icon">➡️</span>' : ''}
                        </div>
                        <div class="fleet-stats">
                            <span title="Ships">🚀${ships}</span>
                            ${cargo > 0 ? `<span title="Cargo">📦${cargo}</span>` : ''}
                            ${artifactStr}
                        </div>
                    </div>
                `;
            });

            html += '</div>';
        });

        html += '</div>';
        this.element.innerHTML = html;

        // Add click listeners
        this.element.querySelectorAll('.fleet-entry').forEach(entry => {
            entry.addEventListener('click', () => {
                const fleetId = parseInt(entry.dataset.fleetId);
                if (this.onFleetClick) {
                    this.onFleetClick(fleetId);
                }
            });
        });
    }

    /**
     * Group fleets by the world they're orbiting
     */
    _groupFleetsByWorld(fleets) {
        const groups = {};

        fleets.forEach(fleet => {
            const worldId = fleet.world !== undefined ? fleet.world : 'moving';
            if (!groups[worldId]) {
                groups[worldId] = [];
            }
            groups[worldId].push(fleet);
        });

        return groups;
    }

    /**
     * Sort worlds with conflict (hostile fleets) first
     */
    _sortWorldsByConflict(fleetsByWorld, gameState) {
        const worldGroups = [];

        for (const worldId in fleetsByWorld) {
            const hasConflict = this._hasConflict(worldId, gameState);
            worldGroups.push({
                worldId: worldId,
                fleets: fleetsByWorld[worldId],
                hasConflict: hasConflict
            });
        }

        // Sort: conflict first, then by world ID
        worldGroups.sort((a, b) => {
            if (a.hasConflict && !b.hasConflict) return -1;
            if (!a.hasConflict && b.hasConflict) return 1;

            // Both same conflict status, sort by world ID
            const aId = a.worldId === 'moving' ? Infinity : parseInt(a.worldId);
            const bId = b.worldId === 'moving' ? Infinity : parseInt(b.worldId);
            return aId - bId;
        });

        return worldGroups;
    }

    /**
     * Check if a world has hostile fleets (conflict)
     */
    _hasConflict(worldId, gameState) {
        if (worldId === 'moving') return false;

        // Get all fleets at this world
        const fleetsAtWorld = Object.values(gameState.fleets || {})
            .filter(f => f.world == worldId);

        // Check if there are hostile fleets
        const hasHostile = fleetsAtWorld.some(f => f.owner !== gameState.player_name);

        return hasHostile;
    }

    /**
     * Get world name/label
     */
    _getWorldName(worldId, gameState) {
        if (worldId === 'moving') {
            return '🚀 In Transit';
        }

        const world = gameState.worlds?.[worldId];
        const owned = world?.owner === gameState.player_name;
        const ownerLabel = owned ? ' (yours)' : (world?.owner ? ` (${world.owner})` : '');

        return `W${worldId}${ownerLabel}`;
    }

    /**
     * Get human-readable fleet location
     */
    _getFleetLocation(fleet, gameState) {
        if (fleet.path && fleet.path.length > 0) {
            const from = fleet.path[0];
            const to = fleet.path[fleet.path.length - 1];
            return `W${from} → W${to}`;
        } else if (fleet.world !== undefined) {
            return `@ W${fleet.world}`;
        }
        return 'Unknown';
    }

    /**
     * Set callback for fleet click events
     */
    setOnFleetClick(callback) {
        this.onFleetClick = callback;
    }
}
