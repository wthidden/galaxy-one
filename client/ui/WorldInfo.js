/**
 * WorldInfo - Displays detailed information about selected world
 */
class WorldInfo {
    constructor(elementId) {
        this.element = document.getElementById(elementId);
    }

    /**
     * Update world info panel with selected world
     */
    update(gameState, worldId) {
        if (!this.element) return;

        if (!worldId || !gameState.worlds || !gameState.worlds[worldId]) {
            this.element.innerHTML = '<div class="empty-message">Click a world to see details</div>';
            return;
        }

        const world = gameState.worlds[worldId];
        const isMyWorld = world.owner === gameState.player_name;

        // Build HTML
        let html = '<div class="world-info-panel">';

        // Header
        html += `
            <div class="info-header">
                <h4>World ${world.id} ${world.key ? '🔑' : ''}</h4>
                ${world.owner ? `<div class="owner">Owner: ${world.owner}</div>` : '<div class="owner">Unowned</div>'}
            </div>
        `;

        // BLACK HOLE WARNING
        if (world.is_blackhole) {
            html += '<div class="info-section blackhole-warning">';
            html += '<div class="section-label">⚫ BLACK HOLE ⚫</div>';
            html += '<div class="warning-text">Ships entering this world will be DESTROYED!</div>';
            html += '<div class="warning-text">Fleet keys will respawn at random locations.</div>';
            html += '</div>';
        }

        // Resources
        html += '<div class="info-section">';
        html += '<div class="section-label">Resources</div>';
        html += '<div class="info-row"><span>Metal:</span><span>⚙️ ' + (world.metal || 0) + '</span></div>';
        html += '<div class="info-row"><span>Mines:</span><span>⛏️ ' + (world.mines || 0) + '</span></div>';
        html += '</div>';

        // Population
        html += '<div class="info-section">';
        html += '<div class="section-label">Population</div>';

        // Population type indicator
        let popIcon = '👥';
        let popType = '';
        if (world.population_type === 'robot') {
            popIcon = '🤖';
            popType = ' (Robots)';
        }

        // Normal population
        if (world.population_type !== 'robot') {
            html += '<div class="info-row"><span>Normal:</span><span>' + popIcon + ' ' + (world.population || 0);
            if (world.limit && world.limit > 0) {
                html += ' / ' + world.limit;
            }
            html += '</span></div>';
        } else {
            // Robot population (no limit)
            html += '<div class="info-row"><span>Robots:</span><span>' + popIcon + ' ' + (world.population || 0) + popType + '</span></div>';
        }

        // Converts (Apostle population)
        if (world.converts && world.converts > 0) {
            html += '<div class="info-row"><span>Converts:</span><span>✝️ ' + world.converts;
            if (world.convert_owner) {
                html += ' (' + world.convert_owner + ')';
            }
            html += '</span></div>';
        }

        // Effective population (available for work)
        if (world.population !== '?') {
            const effectivePop = Math.min(world.population || 0, world.industry || 0);
            html += '<div class="info-row info-secondary"><span>Effective Pop:</span><span>👷 ' + effectivePop + '</span></div>';
        }
        html += '</div>';

        // Industry
        html += '<div class="info-section">';
        html += '<div class="section-label">Industry</div>';
        html += '<div class="info-row"><span>Industry:</span><span>🏭 ' + (world.industry || 0) + '</span></div>';

        // Effective industry (can run with available population)
        if (world.industry !== '?') {
            const effectiveInd = Math.min(world.industry || 0, world.population || 0);
            html += '<div class="info-row info-secondary"><span>Effective Ind:</span><span>⚡ ' + effectiveInd + '</span></div>';
        }
        html += '</div>';

        // Defenses
        html += '<div class="info-section">';
        html += '<div class="section-label">Defenses</div>';
        html += '<div class="info-row"><span>IShips:</span><span>🔵 ' + (world.iships || 0) + '</span></div>';
        html += '<div class="info-row"><span>PShips:</span><span>🟢 ' + (world.pships || 0) + '</span></div>';
        html += '</div>';

        // Status warnings
        if (world.plundered || world.planet_buster) {
            html += '<div class="info-section info-warning">';
            html += '<div class="section-label">⚠️ Status</div>';
            if (world.plundered) {
                html += '<div class="warning-text">🏴‍☠️ Plundered</div>';
            }
            if (world.planet_buster) {
                html += '<div class="warning-text">💣 Planet Buster</div>';
            }
            html += '</div>';
        }

        // Artifacts
        if (world.artifacts && world.artifacts.length > 0) {
            html += '<div class="info-section">';
            html += '<div class="section-label">✨ Artifacts (' + world.artifacts.length + ')</div>';
            html += '<div class="artifacts-list">';
            world.artifacts.forEach(artifact => {
                const artName = artifact.name || `Artifact ${artifact.id}`;
                html += `<div class="artifact-item">
                    <span class="artifact-id">A${artifact.id}</span>
                    <span class="artifact-name">${artName}</span>
                </div>`;
            });
            html += '</div>';
            html += '</div>';
        }

        html += '</div>';

        // Connections
        if (world.connections && world.connections.length > 0) {
            html += '<div class="info-section">';
            html += '<div class="section-label">Connections:</div>';
            html += '<div class="connections-list">';
            world.connections.forEach(connId => {
                html += `<span class="connection-tag">W${connId}</span>`;
            });
            html += '</div>';
            html += '</div>';
        }

        // Fleets at world
        const fleetsHere = Object.values(gameState.fleets || {})
            .filter(f => f.world === worldId && !f.path);

        if (fleetsHere.length > 0) {
            html += '<div class="info-section">';
            html += '<div class="section-label">Fleets:</div>';

            const myFleets = fleetsHere.filter(f => f.owner === gameState.player_name);
            const hostileFleets = fleetsHere.filter(f => f.owner !== gameState.player_name);

            if (myFleets.length > 0) {
                html += '<div class="fleet-group">Friendly:</div>';
                myFleets.forEach(f => {
                    const artifactCount = (f.artifacts && f.artifacts.length > 0) ? ` ✨${f.artifacts.length}` : '';
                    const artifactIds = (f.artifacts && f.artifacts.length > 0)
                        ? f.artifacts.map(a => `A${a.id}`).join(', ')
                        : '';
                    const artifactTitle = artifactIds ? ` title="Artifacts: ${artifactIds}"` : '';
                    html += `<div class="fleet-tag"${artifactTitle}>F${f.id} (🚀${f.ships || 0})${artifactCount}</div>`;
                });
            }

            if (hostileFleets.length > 0) {
                html += '<div class="fleet-group">Hostile:</div>';
                hostileFleets.forEach(f => {
                    const artifactCount = (f.artifacts && f.artifacts.length > 0) ? ` ✨${f.artifacts.length}` : '';
                    html += `<div class="fleet-tag hostile">${f.owner}: F${f.id} (🚀${f.ships || 0})${artifactCount}</div>`;
                });
            }

            html += '</div>';
        }

        html += '</div>';
        this.element.innerHTML = html;
    }

    /**
     * Clear the world info panel
     */
    clear() {
        if (this.element) {
            this.element.innerHTML = '<div class="empty-message">Click a world to see details</div>';
        }
    }
}
