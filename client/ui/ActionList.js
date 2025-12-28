/**
 * ActionList - Displays available actions for selected world/fleet
 */
class ActionList {
    constructor(elementId) {
        this.element = document.getElementById(elementId);
        this.onActionClick = null;
    }

    /**
     * Update action list based on selection
     */
    update(gameState, selectedWorldId, selectedFleetId) {
        if (!this.element) return;

        if (selectedWorldId) {
            this._updateWorldActions(gameState, selectedWorldId);
        } else if (selectedFleetId) {
            this._updateFleetActions(gameState, selectedFleetId);
        } else {
            this.element.innerHTML = '<div class="empty-message">Select an item to see actions.</div>';
        }
    }

    /**
     * Update with actions for selected world
     */
    _updateWorldActions(gameState, worldId) {
        const world = gameState.worlds?.[worldId];
        if (!world) {
            this.element.innerHTML = '<div class="empty-message">World not found</div>';
            return;
        }

        const isMyWorld = world.owner === gameState.player_name;
        const actions = [];

        if (isMyWorld) {
            // Build actions
            actions.push({ id: 'build-ships', label: '🚀 Build Ships', description: 'Build new ships' });
            actions.push({ id: 'build-industry', label: '🏭 Build Industry', description: 'Increase production' });
            actions.push({ id: 'build-defenses', label: '🛡️ Build Defenses', description: 'Fortify world' });

            // Transfer actions if there are fleets
            const fleetsHere = Object.values(gameState.fleets || {})
                .filter(f => f.world === worldId && f.owner === gameState.player_name);

            if (fleetsHere.length > 0) {
                actions.push({ id: 'transfer', label: '📦 Transfer', description: 'Transfer cargo to fleet' });
            }

            // Set ambush
            actions.push({ id: 'ambush', label: '🎯 Set Ambush', description: 'Ambush incoming fleets' });
        } else {
            // Actions for hostile/neutral worlds
            actions.push({ id: 'fire-world', label: '💥 Fire at World', description: 'Attack world defenses' });
        }

        this._renderActions(actions, `World ${worldId}`);
    }

    /**
     * Update with actions for selected fleet
     */
    _updateFleetActions(gameState, fleetId) {
        const fleet = gameState.fleets?.[fleetId];
        if (!fleet) {
            this.element.innerHTML = '<div class="empty-message">Fleet not found</div>';
            return;
        }

        const isMyFleet = fleet.owner === gameState.player_name;
        const actions = [];

        if (isMyFleet) {
            // Move action
            actions.push({ id: 'move-fleet', label: '➡️ Move Fleet', description: 'Move to another world' });

            // Fire actions if at a world with hostiles
            if (fleet.world !== undefined) {
                const world = gameState.worlds?.[fleet.world];
                if (world && world.owner !== gameState.player_name) {
                    actions.push({ id: 'fire-world', label: '💥 Fire at World', description: 'Attack world' });
                }

                // Check for hostile fleets
                const hostileFleets = Object.values(gameState.fleets || {})
                    .filter(f => f.world === fleet.world && f.owner !== gameState.player_name);

                if (hostileFleets.length > 0) {
                    actions.push({ id: 'fire-fleet', label: '💥 Fire at Fleet', description: 'Attack hostile fleet' });
                }
            }
        } else {
            // Actions for hostile fleets
            if (fleet.world !== undefined) {
                actions.push({ id: 'fire-fleet', label: '💥 Fire at Fleet', description: 'Attack fleet' });
            }
        }

        this._renderActions(actions, `Fleet ${fleetId}`);
    }

    /**
     * Render action buttons
     */
    _renderActions(actions, title) {
        let html = `<div class="action-list-panel">`;
        html += `<div class="action-title">${title}</div>`;

        if (actions.length === 0) {
            html += '<div class="empty-message">No actions available</div>';
        } else {
            html += '<div class="action-buttons">';
            actions.forEach(action => {
                html += `
                    <button class="action-btn" data-action-id="${action.id}">
                        <span class="action-label">${action.label}</span>
                        <span class="action-description">${action.description}</span>
                    </button>
                `;
            });
            html += '</div>';
        }

        html += '</div>';
        this.element.innerHTML = html;

        // Add click listeners
        this.element.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const actionId = btn.dataset.actionId;
                if (this.onActionClick) {
                    this.onActionClick(actionId);
                }
            });
        });
    }

    /**
     * Set callback for action click events
     */
    setOnActionClick(callback) {
        this.onActionClick = callback;
    }

    /**
     * Clear the action list
     */
    clear() {
        if (this.element) {
            this.element.innerHTML = '<div class="empty-message">Select an item to see actions.</div>';
        }
    }
}
