/**
 * CommandHint - Provides real-time hints for command input
 */
class CommandHint {
    constructor(elementId) {
        this.element = document.getElementById(elementId);
    }

    /**
     * Update hint based on current input
     */
    update(input, gameState) {
        if (!this.element) return;

        if (!input) {
            this.element.innerHTML = '';
            return;
        }

        const hint = this._getHint(input.toUpperCase(), gameState);
        if (hint) {
            this.element.innerHTML = `<div class="hint-message">${hint}</div>`;
        } else {
            this.element.innerHTML = '';
        }
    }

    /**
     * Get hint for current input
     */
    _getHint(input, gameState) {
        // JOIN command
        if (input.startsWith('JOIN')) {
            return '💡 Format: JOIN &lt;name&gt; &lt;score&gt; &lt;type&gt; - Join the game';
        }

        // TURN command
        if (input.startsWith('TURN')) {
            return '💡 End your turn and submit orders';
        }

        // MOVE command (F#W#)
        if (input.startsWith('F') && input.includes('W')) {
            const match = input.match(/F(\d+)W(\d+)/);
            if (match) {
                const fleetId = parseInt(match[1]);
                const worldId = parseInt(match[2]);

                // Validate fleet exists
                const fleet = gameState?.fleets?.[fleetId];
                if (!fleet) {
                    return '❌ Fleet F' + fleetId + ' does not exist';
                }

                // Validate world exists
                const world = gameState?.worlds?.[worldId];
                if (!world) {
                    return '❌ World W' + worldId + ' does not exist';
                }

                // Check if it's your fleet
                if (fleet.owner !== gameState?.player_name) {
                    return '❌ Fleet F' + fleetId + ' is not yours';
                }

                // Check if already moving
                if (fleet.path && fleet.path.length > 0) {
                    return '⚠️ Fleet F' + fleetId + ' is already moving';
                }

                return '✓ Move F' + fleetId + ' to W' + worldId;
            }
            return '💡 Format: F&lt;fleet&gt;W&lt;world&gt; - Move fleet to world';
        }

        // BUILD command (B#X)
        if (input.startsWith('B')) {
            const match = input.match(/B(\d+)([SIDP])/);
            if (match) {
                const worldId = parseInt(match[1]);
                const type = match[2];

                const typeMap = {
                    'S': 'Ships',
                    'I': 'Industry',
                    'D': 'Defenses',
                    'P': 'Population'
                };

                const world = gameState?.worlds?.[worldId];
                if (!world) {
                    return '❌ World W' + worldId + ' does not exist';
                }

                if (world.owner !== gameState?.player_name) {
                    return '❌ World W' + worldId + ' is not yours';
                }

                return '✓ Build ' + typeMap[type] + ' at W' + worldId;
            }
            return '💡 Format: B&lt;world&gt;&lt;type&gt; - Build (S=Ships, I=Industry, D=Defenses)';
        }

        // TRANSFER command (T#F#A#X)
        if (input.startsWith('T')) {
            return '💡 Format: T&lt;world&gt;F&lt;fleet&gt;A&lt;amount&gt;&lt;type&gt; - Transfer cargo';
        }

        // FIRE command (X#X#)
        if (input.startsWith('X')) {
            return '💡 Format: X&lt;source&gt;&lt;target&gt; - Fire at target (W=world, F=fleet)';
        }

        // AMBUSH command (A#W#)
        if (input.startsWith('A')) {
            return '💡 Format: A&lt;fleet&gt;W&lt;world&gt; - Set ambush';
        }

        return null;
    }

    /**
     * Clear the hint
     */
    clear() {
        if (this.element) {
            this.element.innerHTML = '';
        }
    }
}
