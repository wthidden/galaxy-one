/**
 * Validator - Validates commands against game state
 */
class Validator {
    constructor(gameState) {
        this.gameState = gameState;
        this.rules = new ValidationRules(gameState);
    }

    /**
     * Validate a command AST
     *
     * @param {CommandNode} ast - The command AST to validate
     * @param {Object} options - Validation options
     * @returns {ValidationResult}
     */
    validate(ast, options = {}) {
        if (!ast) {
            return ValidationResult.invalid('No command parsed');
        }

        const result = new ValidationResult(true);

        // Partial commands are always valid (user is still typing)
        if (options.partial && this.isPartialCommand(ast)) {
            return result;
        }

        // Dispatch to specific validators
        try {
            if (ast instanceof MoveCommand) {
                this.validateMove(ast, result);
            } else if (ast instanceof BuildCommand) {
                this.validateBuild(ast, result);
            } else if (ast instanceof TransferCommand) {
                this.validateTransfer(ast, result);
            } else if (ast instanceof FireFleetCommand) {
                this.validateFireFleet(ast, result);
            } else if (ast instanceof FireWorldCommand) {
                this.validateFireWorld(ast, result);
            } else if (ast instanceof AmbushCommand) {
                this.validateAmbush(ast, result);
            } else if (ast instanceof JoinCommand) {
                this.validateJoin(ast, result);
            } else if (ast instanceof TurnCommand) {
                // TURN is always valid
                return result;
            } else if (this.isPartialCommand(ast)) {
                // Partial commands handled above
                return result;
            }
        } catch (error) {
            result.addError(error.message);
        }

        return result;
    }

    /**
     * Check if command is partial (incomplete)
     */
    isPartialCommand(ast) {
        return ast instanceof PartialFleetCommand ||
               ast instanceof PartialWorldCommand ||
               ast instanceof PartialBuildCommand ||
               ast instanceof PartialTransferCommand ||
               ast instanceof PartialJoinCommand;
    }

    /**
     * Validate move command
     */
    validateMove(ast, result) {
        // Check fleet exists and ownership
        const fleetCheck = this.rules.validateFleetOwnership(ast.fleetId);
        if (!fleetCheck.valid) {
            result.addError(fleetCheck.error);
            result.addSuggestion(`Your fleets: ${this.rules.getMyFleetIds().map(id => `F${id}`).join(', ')}`);
            return;
        }

        const fleet = fleetCheck.fleet;

        // Check exclusive orders
        if (this.rules.hasExclusiveOrder(ast.fleetId)) {
            result.addError(`Fleet F${ast.fleetId} already has an exclusive order (move/fire/ambush)`);
            result.addSuggestion('Cancel existing order or choose a different fleet');
            return;
        }

        // Check fleet has ships
        if (!fleet.ships || fleet.ships === 0) {
            result.addError(`Fleet F${ast.fleetId} has no ships`);
            return;
        }

        // Validate each world in path
        for (const worldId of ast.path) {
            const state = this.gameState.getState();
            const world = state.worlds?.[worldId];
            if (!world) {
                result.addError(`World W${worldId} does not exist`);
                result.addSuggestion(`Valid worlds: ${Object.keys(state.worlds || {}).join(', ')}`);
                return;
            }
        }

        // Check if fleet is already moving
        if (fleet.path && fleet.path.length > 0) {
            result.addWarning(`Fleet F${ast.fleetId} is already moving (will override)`);
        }

        // Validate path connectivity
        if (fleet.world !== undefined) {
            const pathCheck = this.rules.validatePathConnectivity(fleet.world, ast.path);
            if (!pathCheck.valid) {
                result.addError(pathCheck.error);
                result.addSuggestion('Check world connections on the map');
                return;
            }
        }
    }

    /**
     * Validate build command
     */
    validateBuild(ast, result) {
        // Check world exists and ownership
        const worldCheck = this.rules.validateWorldOwnership(ast.worldId);
        if (!worldCheck.valid) {
            result.addError(worldCheck.error);
            result.addSuggestion(`Your worlds: ${this.rules.getMyWorldIds().map(id => `W${id}`).join(', ')}`);
            return;
        }

        const world = worldCheck.world;

        // Check resources
        const available = world.industry || 0;
        const amountCheck = this.rules.validateAmount(ast.amount, available, 'industry');
        if (!amountCheck.valid) {
            result.addError(amountCheck.error);
            result.addSuggestion(`Maximum buildable: ${available}`);
            return;
        }

        // Target-specific validation
        if (ast.targetType === 'F') {
            const targetFleetCheck = this.rules.validateFleetOwnership(ast.targetId);
            if (!targetFleetCheck.valid) {
                result.addError(`Target ${targetFleetCheck.error}`);
                return;
            }

            const targetFleet = targetFleetCheck.fleet;
            if (targetFleet.world !== ast.worldId) {
                result.addError(`Fleet F${ast.targetId} is not at world W${ast.worldId}`);
                result.addSuggestion(`Fleet is at W${targetFleet.world}`);
                return;
            }
        }
    }

    /**
     * Validate transfer command
     */
    validateTransfer(ast, result) {
        // Check fleet exists and ownership
        const fleetCheck = this.rules.validateFleetOwnership(ast.fleetId);
        if (!fleetCheck.valid) {
            result.addError(fleetCheck.error);
            return;
        }

        const fleet = fleetCheck.fleet;

        // Check fleet has enough ships
        const ships = fleet.ships || 0;
        const amountCheck = this.rules.validateAmount(ast.amount, ships, 'ships');
        if (!amountCheck.valid) {
            result.addError(amountCheck.error);
            result.addSuggestion(`Fleet has ${ships} ships`);
            return;
        }

        // Check fleet is at a world (for I/P transfers)
        if ((ast.targetType === 'I' || ast.targetType === 'P') && fleet.world === undefined) {
            result.addError('Fleet must be at a world to transfer to garrison');
            return;
        }

        // Check target fleet
        if (ast.targetType === 'F') {
            const targetFleetCheck = this.rules.validateFleetOwnership(ast.targetId);
            if (!targetFleetCheck.valid) {
                result.addError(`Target ${targetFleetCheck.error}`);
                return;
            }

            const targetFleet = targetFleetCheck.fleet;
            if (targetFleet.world !== fleet.world) {
                result.addError('Both fleets must be at the same world');
                return;
            }
        }
    }

    /**
     * Validate fire fleet command
     */
    validateFireFleet(ast, result) {
        const state = this.gameState.getState();

        // Check source fleet
        const fleetCheck = this.rules.validateFleetOwnership(ast.fleetId);
        if (!fleetCheck.valid) {
            result.addError(fleetCheck.error);
            return;
        }

        const fleet = fleetCheck.fleet;

        // Check exclusive orders
        if (this.rules.hasExclusiveOrder(ast.fleetId)) {
            result.addError(`Fleet F${ast.fleetId} already has an exclusive order`);
            return;
        }

        // Check target fleet exists
        const targetFleet = state.fleets?.[ast.targetFleetId];
        if (!targetFleet) {
            result.addError(`Target fleet F${ast.targetFleetId} does not exist`);
            result.addSuggestion(`Visible fleets: ${this.rules.getVisibleFleetIds().map(id => `F${id}`).join(', ')}`);
            return;
        }

        // Check both fleets at same location
        if (fleet.world !== targetFleet.world) {
            result.addError('Fleets must be at the same world to fire');
            return;
        }

        // Warning if firing at own fleet
        if (targetFleet.owner === state.player_name) {
            result.addWarning('WARNING: You are attacking your own fleet!');
        }
    }

    /**
     * Validate fire world command
     */
    validateFireWorld(ast, result) {
        const state = this.gameState.getState();

        // Check fleet
        const fleetCheck = this.rules.validateFleetOwnership(ast.fleetId);
        if (!fleetCheck.valid) {
            result.addError(fleetCheck.error);
            return;
        }

        const fleet = fleetCheck.fleet;

        // Check exclusive orders
        if (this.rules.hasExclusiveOrder(ast.fleetId)) {
            result.addError(`Fleet F${ast.fleetId} already has an exclusive order`);
            return;
        }

        // Check fleet is at a world
        if (fleet.world === undefined) {
            result.addError('Fleet must be at a world to fire at it');
            return;
        }

        const world = state.worlds?.[fleet.world];
        if (!world) {
            result.addError(`World W${fleet.world} does not exist`);
            return;
        }

        // Warning if firing at own world
        if (world.owner === state.player_name) {
            result.addWarning('WARNING: You are attacking your own world!');
        }

        // Check target validity
        if (ast.target === 'P' && (!world.population || world.population === 0)) {
            result.addWarning('World has no population to fire at');
        }

        if (ast.target === 'I' && (!world.industry || world.industry === 0)) {
            result.addWarning('World has no industry to fire at');
        }
    }

    /**
     * Validate ambush command
     */
    validateAmbush(ast, result) {
        // Check fleet
        const fleetCheck = this.rules.validateFleetOwnership(ast.fleetId);
        if (!fleetCheck.valid) {
            result.addError(fleetCheck.error);
            return;
        }

        const fleet = fleetCheck.fleet;

        // Check exclusive orders
        if (this.rules.hasExclusiveOrder(ast.fleetId)) {
            result.addError(`Fleet F${ast.fleetId} already has an exclusive order`);
            return;
        }

        // Check fleet is at a world
        if (fleet.world === undefined) {
            result.addError('Fleet must be at a world to set ambush');
            return;
        }
    }

    /**
     * Validate join command
     */
    validateJoin(ast, result) {
        // Basic validation - check if args are provided
        if (!ast.args || ast.args.trim().length === 0) {
            result.addError('JOIN requires player name and character type');
            result.addSuggestion('Format: JOIN YourName CharacterType');
            return;
        }

        // Could validate character types here
        const validTypes = ['EmpireBuilder', 'Merchant', 'Pirate', 'ArtifactCollector', 'Berserker', 'Apostle'];
        const args = ast.args.trim();
        const hasValidType = validTypes.some(type => args.toUpperCase().includes(type.toUpperCase()));

        if (!hasValidType) {
            result.addWarning('Character type not recognized. Valid types: ' + validTypes.join(', '));
        }
    }
}
