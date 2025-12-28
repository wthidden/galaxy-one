/**
 * FleetInfo - Displays detailed information about selected fleet
 */
class FleetInfo {
    constructor(elementId) {
        this.element = document.getElementById(elementId);
    }

    /**
     * Update fleet info panel with selected fleet
     */
    update(gameState, fleetId) {
        if (!this.element) return;

        if (!fleetId || !gameState.fleets || !gameState.fleets[fleetId]) {
            this.element.innerHTML = '<div class="empty-message">Click a fleet to see details</div>';
            return;
        }

        const fleet = gameState.fleets[fleetId];
        const isMyFleet = fleet.owner === gameState.player_name;
        const world = gameState.worlds?.[fleet.world];

        // Build HTML
        let html = '<div class="fleet-info-panel">';

        // Header
        html += `
            <div class="info-header">
                <h4>Fleet ${fleet.id}</h4>
                <div class="owner">Owner: ${fleet.owner}</div>
            </div>
        `;

        // Location
        html += '<div class="info-section">';
        html += '<div class="section-label">Location</div>';
        const worldName = world ? (world.key || `World ${world.id}`) : 'Unknown';
        const worldOwner = world?.owner || '[Neutral]';
        html += `<div class="info-row"><span>At:</span><span>W${fleet.world} ${worldName} (${worldOwner})</span></div>`;
        html += '</div>';

        // Fleet Composition (only for owned fleets)
        if (isMyFleet) {
            html += '<div class="info-section">';
            html += '<div class="section-label">Composition</div>';
            html += '<div class="info-row"><span>Ships:</span><span>🚀 ' + (fleet.ships || 0) + '</span></div>';
            html += '<div class="info-row"><span>Cargo:</span><span>📦 ' + (fleet.cargo || 0) + '</span></div>';
            html += '</div>';
        } else {
            // Limited info for enemy fleets
            html += '<div class="info-section">';
            html += '<div class="section-label">Visible Info</div>';
            html += '<div class="info-row"><span>Ships:</span><span>🚀 ' + (fleet.ships || 0) + '</span></div>';
            html += '</div>';
        }

        // Status
        if (isMyFleet && (fleet.moved || fleet.is_ambushing || fleet.has_pbb)) {
            html += '<div class="info-section">';
            html += '<div class="section-label">Status</div>';

            if (fleet.moved) {
                html += '<div class="info-row"><span>Movement:</span><span>➡️ Moving</span></div>';
            }
            if (fleet.is_ambushing) {
                html += '<div class="info-row"><span>Combat:</span><span>⚔️ Ambushing</span></div>';
            }
            if (fleet.has_pbb) {
                html += '<div class="info-row"><span>Weapons:</span><span>💣 Planet Buster Bomb</span></div>';
            }

            html += '</div>';
        }

        // Artifacts (detailed list with names)
        if (fleet.artifacts && fleet.artifacts.length > 0) {
            html += '<div class="info-section">';
            html += '<div class="section-label">✨ Artifacts (' + fleet.artifacts.length + ')</div>';

            if (isMyFleet) {
                // Show full artifact details for owned fleets
                html += '<div class="artifacts-list">';
                fleet.artifacts.forEach(artifact => {
                    const artName = artifact.name || `Artifact ${artifact.id}`;
                    html += `<div class="artifact-item">
                        <span class="artifact-id">A${artifact.id}</span>
                        <span class="artifact-name">${artName}</span>
                    </div>`;
                });
                html += '</div>';

                // Add helpful hint about unloading
                html += '<div class="info-hint">💡 To unload: UNLOAD F' + fleet.id + ' A' + fleet.artifacts[0].id + '</div>';
            } else {
                // Just show count for enemy fleets
                html += '<div class="info-row"><span>Count:</span><span>✨ ' + fleet.artifacts.length + '</span></div>';
            }

            html += '</div>';
        }

        // Nearby fleets (at same world)
        if (world && fleet.world !== undefined) {
            const fleetsHere = Object.values(gameState.fleets || {})
                .filter(f => f.world === fleet.world && f.id !== fleet.id);

            if (fleetsHere.length > 0) {
                html += '<div class="info-section">';
                html += '<div class="section-label">Other Fleets Here:</div>';

                const friendlyFleets = fleetsHere.filter(f => f.owner === gameState.player_name);
                const hostileFleets = fleetsHere.filter(f => f.owner !== gameState.player_name);

                if (friendlyFleets.length > 0) {
                    html += '<div class="fleet-group">Friendly:</div>';
                    friendlyFleets.forEach(f => {
                        const artifactCount = (f.artifacts && f.artifacts.length > 0) ? ` ✨${f.artifacts.length}` : '';
                        html += `<div class="fleet-tag">F${f.id} (🚀${f.ships || 0})${artifactCount}</div>`;
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
        }

        // Available actions hint (for owned fleets)
        if (isMyFleet) {
            html += '<div class="info-section">';
            html += '<div class="section-label">Quick Commands</div>';
            html += '<div class="command-hints">';
            html += `<code>F${fleet.id}W#</code> Move to world<br>`;
            html += `<code>F${fleet.id}LW#</code> Load cargo<br>`;
            html += `<code>F${fleet.id}UW#</code> Unload cargo<br>`;
            if (fleet.artifacts && fleet.artifacts.length > 0) {
                html += `<code>UNLOAD F${fleet.id} A#</code> Unload artifact<br>`;
            }
            html += '</div>';
            html += '</div>';
        }

        html += '</div>';
        this.element.innerHTML = html;
    }

    /**
     * Clear the fleet info panel
     */
    clear() {
        if (this.element) {
            this.element.innerHTML = '<div class="empty-message">Click a fleet to see details</div>';
        }
    }
}
