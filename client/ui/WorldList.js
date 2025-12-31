/**
 * WorldList - Displays player's worlds
 */
class WorldList {
    constructor(elementId) {
        this.element = document.getElementById(elementId);
        this.onWorldClick = null;
        this.filter = 'own'; // own, all, neutral, enemy
    }

    /**
     * Set the filter mode
     */
    setFilter(filter) {
        this.filter = filter;
    }

    /**
     * Update world list with current game state
     */
    update(gameState) {
        if (!this.element || !gameState.worlds || !gameState.player_name) return;

        // Filter worlds based on filter mode
        let worlds = Object.values(gameState.worlds);

        if (this.filter === 'own') {
            worlds = worlds.filter(w => w.owner === gameState.player_name);
        } else if (this.filter === 'neutral') {
            worlds = worlds.filter(w => !w.owner);
        } else if (this.filter === 'enemy') {
            worlds = worlds.filter(w => w.owner && w.owner !== gameState.player_name);
        }
        // 'all' shows everything, no filtering needed

        // Sort worlds
        worlds.sort((a, b) => {
            // Sort by: key worlds first, then by ID
            if (a.key && !b.key) return -1;
            if (!a.key && b.key) return 1;
            return a.id - b.id;
        });

        // Build HTML
        let html = '<div class="world-list">';

        if (worlds.length === 0) {
            html += '<div class="empty-message">No worlds found</div>';
        } else {
            worlds.forEach(world => {
                const isKey = world.key ? '🔑' : '';
                const iships = world.iships || 0;
                const pships = world.pships || 0;
                const defenseStr = `I${iships}/P${pships}`;
                const industry = world.industry || 0;
                const population = world.population || 0;
                const artifacts = world.artifacts || [];

                // Build artifact list
                let artifactStr = '';
                if (artifacts.length > 0) {
                    const artifactIds = artifacts.map(a => `A${a.id}`).join(', ');
                    artifactStr = `<span class="artifact-list" title="Artifacts: ${artifactIds}">✨${artifacts.length}</span>`;
                }

                // Show owner if not player's world
                let ownerStr = '';
                if (world.owner && world.owner !== gameState.player_name) {
                    ownerStr = `<span class="world-owner" title="Owner">${world.owner}</span>`;
                } else if (!world.owner) {
                    ownerStr = `<span class="world-owner neutral" title="Neutral">Neutral</span>`;
                }

                html += `
                    <div class="world-entry" data-world-id="${world.id}">
                        <div class="world-header">
                            <span class="world-id">W${world.id}</span>
                            ${isKey ? `<span class="key-icon">${isKey}</span>` : ''}
                            ${ownerStr}
                        </div>
                        <div class="world-stats">
                            <span title="Population">👥${population}</span>
                            <span title="Industry">🏭${industry}</span>
                            <span title="Defenses (Industry Ships/Population Ships)">🛡️${defenseStr}</span>
                            ${artifactStr}
                        </div>
                    </div>
                `;
            });
        }

        html += '</div>';
        this.element.innerHTML = html;

        // Add click listeners
        this.element.querySelectorAll('.world-entry').forEach(entry => {
            entry.addEventListener('click', () => {
                const worldId = parseInt(entry.dataset.worldId);
                if (this.onWorldClick) {
                    this.onWorldClick(worldId);
                }
            });
        });
    }

    /**
     * Set callback for world click events
     */
    setOnWorldClick(callback) {
        this.onWorldClick = callback;
    }
}
