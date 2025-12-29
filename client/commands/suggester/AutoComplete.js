/**
 * AutoComplete - Context-aware command suggestions
 */
class AutoComplete {
    constructor(gameState) {
        this.gameState = gameState;
        this.fuzzyMatcher = new FuzzyMatcher();
    }

    /**
     * Get suggestions based on current input and context
     *
     * @param {string} input - Current input string
     * @param {Object} context - Parsing context
     * @param {ValidationResult} validation - Validation result
     * @returns {Array} - Array of suggestion objects
     */
    suggest(input, context, validation) {
        if (!input || input.length === 0) {
            return this.getTopLevelSuggestions();
        }

        if (!context) {
            return [];
        }

        switch (context.type) {
            case 'fleet':
                return this.suggestFleetCommand(input, context, validation);
            case 'world':
                return this.suggestWorldCommand(input, context, validation);
            case 'join':
                return this.suggestJoinCommand(input);
            case 'turn':
                return [{ text: 'TURN', description: 'End your turn', type: 'command' }];
            default:
                return this.getTopLevelSuggestions();
        }
    }

    /**
     * Get top-level command suggestions
     */
    getTopLevelSuggestions() {
        const suggestions = [];
        const state = this.gameState.getState();

        if (!state) return suggestions;

        // Fleet commands
        const myFleets = this.gameState.getMyFleets();
        myFleets.forEach(fleet => {
            const worldText = fleet.world !== undefined ? ` at W${fleet.world}` : ' (in transit)';
            suggestions.push({
                text: `F${fleet.id}`,
                description: `Fleet ${fleet.id} (${fleet.ships || 0} ships${worldText})`,
                type: 'fleet',
                preview: `F${fleet.id}W`,
                priority: 10
            });
        });

        // World commands
        const myWorlds = this.gameState.getMyWorlds();
        myWorlds.forEach(world => {
            suggestions.push({
                text: `W${world.id}`,
                description: `World ${world.id} (I:${world.industry || 0}, P:${world.population || 0})`,
                type: 'world',
                preview: `W${world.id}B`,
                priority: 8
            });
        });

        // System commands
        suggestions.push({
            text: 'TURN',
            description: 'End your turn',
            type: 'command',
            priority: 5
        });

        if (!state.player_name) {
            suggestions.push({
                text: 'JOIN',
                description: 'Join the game',
                type: 'command',
                preview: 'JOIN YourName EmpireBuilder',
                priority: 100
            });
        }

        return suggestions.sort((a, b) => (b.priority || 0) - (a.priority || 0)).slice(0, 10);
    }

    /**
     * Suggest fleet commands based on context stage
     */
    suggestFleetCommand(input, context, validation) {
        const suggestions = [];
        const state = this.gameState.getState();

        if (!state) return suggestions;

        switch (context.stage) {
            case 'fleet_id':
                // Suggest fleet IDs
                const myFleets = this.gameState.getMyFleets();
                myFleets.forEach(fleet => {
                    const text = `F${fleet.id}`;
                    const worldText = fleet.world !== undefined ? ` at W${fleet.world}` : ' (in transit)';
                    suggestions.push({
                        text,
                        description: `${fleet.ships || 0} ships${worldText}`,
                        type: 'fleet',
                        complete: false
                    });
                });
                break;

            case 'action':
                // Suggest next action: W (move), T (transfer), A (attack/ambush)
                suggestions.push({
                    text: input + 'W',
                    description: 'Move fleet to world',
                    type: 'action',
                    complete: false
                });
                suggestions.push({
                    text: input + 'T',
                    description: 'Transfer cargo',
                    type: 'action',
                    complete: false
                });
                suggestions.push({
                    text: input + 'A',
                    description: 'Attack or Ambush',
                    type: 'action',
                    complete: false
                });
                break;

            case 'move_path':
                // Parse current path to determine last world
                const pathWorlds = this.extractMovePath(input);
                let currentWorld = null;

                if (pathWorlds.length > 0) {
                    // Get the last world in the path
                    const lastWorldId = pathWorlds[pathWorlds.length - 1];
                    currentWorld = state.worlds?.[lastWorldId];
                } else {
                    // No path yet, determine starting world from fleet location
                    const fleetId = this.extractFleetId(input);
                    const fleet = state.fleets?.[fleetId];
                    if (fleet && fleet.world !== undefined) {
                        currentWorld = state.worlds?.[fleet.world];
                    }
                }

                // Only suggest connected worlds
                if (currentWorld && currentWorld.connections) {
                    currentWorld.connections.forEach(worldId => {
                        const targetWorld = state.worlds?.[worldId];
                        if (targetWorld) {
                            const hopNumber = pathWorlds.length + 1;
                            suggestions.push({
                                text: input + (input.match(/W\d*$/) ? '' : 'W') + worldId,
                                description: `Hop ${hopNumber}: W${worldId} (${targetWorld.owner || 'neutral'})`,
                                type: 'world',
                                complete: false,
                                priority: 10
                            });
                        }
                    });
                }

                // Show current path in description if multi-hop
                if (pathWorlds.length > 0 && suggestions.length > 0) {
                    const pathDescription = `Path so far: ${pathWorlds.map(w => `W${w}`).join(' → ')}`;
                    // Add path indicator to first suggestion
                    if (suggestions[0]) {
                        suggestions[0].pathInfo = pathDescription;
                    }
                }
                break;

            case 'transfer_target':
                // Suggest I, P, or F#
                suggestions.push({
                    text: input + 'I',
                    description: 'Transfer to industry',
                    type: 'target',
                    complete: true
                });
                suggestions.push({
                    text: input + 'P',
                    description: 'Transfer to population ships',
                    type: 'target',
                    complete: true
                });

                // Suggest nearby fleets
                const fleetId = this.extractFleetId(input);
                const fleet = state.fleets?.[fleetId];
                if (fleet && fleet.world !== undefined) {
                    const nearbyFleets = Object.values(state.fleets || {})
                        .filter(f =>
                            f.world === fleet.world &&
                            f.owner === state.player_name &&
                            f.id !== fleet.id
                        );

                    nearbyFleets.forEach(f => {
                        suggestions.push({
                            text: input + `F${f.id}`,
                            description: `Transfer to Fleet ${f.id} (${f.ships || 0} ships)`,
                            type: 'fleet',
                            complete: true
                        });
                    });
                }
                break;

            case 'attack_type':
                // Suggest attack targets
                suggestions.push({
                    text: input,
                    description: 'Set ambush (wait for incoming fleets)',
                    type: 'ambush',
                    complete: true
                });
                suggestions.push({
                    text: input + 'P',
                    description: 'Fire at world population',
                    type: 'attack',
                    complete: true
                });
                suggestions.push({
                    text: input + 'I',
                    description: 'Fire at world industry',
                    type: 'attack',
                    complete: true
                });

                // Suggest hostile fleets at same location
                const atkFleetId = this.extractFleetId(input);
                const atkFleet = state.fleets?.[atkFleetId];
                if (atkFleet && atkFleet.world !== undefined) {
                    const enemyFleets = Object.values(state.fleets || {})
                        .filter(f =>
                            f.world === atkFleet.world &&
                            f.owner !== state.player_name
                        );

                    enemyFleets.forEach(f => {
                        suggestions.push({
                            text: input + `F${f.id}`,
                            description: `Fire at Fleet ${f.id} (${f.owner})`,
                            type: 'attack',
                            complete: true,
                            highlight: 'danger'
                        });
                    });
                }
                break;
        }

        return suggestions.slice(0, 10);
    }

    /**
     * Suggest world commands based on context stage
     */
    suggestWorldCommand(input, context, validation) {
        const suggestions = [];
        const state = this.gameState.getState();

        if (!state) return suggestions;

        switch (context.stage) {
            case 'world_id':
                // Suggest world IDs
                const myWorlds = this.gameState.getMyWorlds();
                myWorlds.forEach(world => {
                    const text = `W${world.id}`;
                    suggestions.push({
                        text,
                        description: `I:${world.industry || 0}, P:${world.population || 0}`,
                        type: 'world',
                        complete: false
                    });
                });
                break;

            case 'action':
                // Suggest B (build)
                suggestions.push({
                    text: input + 'B',
                    description: 'Build at world',
                    type: 'action',
                    complete: false
                });
                break;

            case 'build_target':
                // Suggest I, P, or F#
                suggestions.push({
                    text: input + 'I',
                    description: 'Build industry ships',
                    type: 'target',
                    complete: true
                });
                suggestions.push({
                    text: input + 'P',
                    description: 'Build population ships',
                    type: 'target',
                    complete: true
                });

                // Suggest fleets at this world
                const worldId = this.extractWorldId(input);
                const fleetsAtWorld = Object.values(state.fleets || {})
                    .filter(f =>
                        f.world === worldId &&
                        f.owner === state.player_name
                    );

                fleetsAtWorld.forEach(f => {
                    suggestions.push({
                        text: input + `F${f.id}`,
                        description: `Build ships to Fleet ${f.id}`,
                        type: 'fleet',
                        complete: true
                    });
                });
                break;
        }

        return suggestions.slice(0, 10);
    }

    /**
     * Suggest join commands
     */
    suggestJoinCommand(input) {
        const characterTypes = [
            'EmpireBuilder',
            'Merchant',
            'Pirate',
            'ArtifactCollector',
            'Berserker',
            'Apostle'
        ];

        return characterTypes.map(type => ({
            text: `JOIN YourName ${type}`,
            description: type,
            type: 'join',
            complete: true
        }));
    }

    // Helper methods

    extractFleetId(input) {
        const match = input.match(/F(\d+)/);
        return match ? parseInt(match[1]) : null;
    }

    extractWorldId(input) {
        const match = input.match(/W(\d+)/);
        return match ? parseInt(match[1]) : null;
    }

    extractMovePath(input) {
        // Extract all world IDs from a move command like "F5W10W23W45"
        const worldMatches = input.matchAll(/W(\d+)/g);
        const path = [];
        for (const match of worldMatches) {
            path.push(parseInt(match[1]));
        }
        return path;
    }
}
