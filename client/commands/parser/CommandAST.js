/**
 * CommandAST - Abstract Syntax Tree node classes for commands
 */

// Base class for all commands
class CommandNode {
    toCommandString() {
        throw new Error('toCommandString must be implemented');
    }
}

// Complete commands

class MoveCommand extends CommandNode {
    constructor(fleetId, path) {
        super();
        this.fleetId = fleetId;
        this.path = path; // Array of world IDs
    }

    toCommandString() {
        return `F${this.fleetId}${this.path.map(w => `W${w}`).join('')}`;
    }
}

class BuildCommand extends CommandNode {
    constructor(worldId, amount, targetType, targetId = null) {
        super();
        this.worldId = worldId;
        this.amount = amount;
        this.targetType = targetType; // 'I', 'P', or 'F'
        this.targetId = targetId; // Fleet ID if targetType is 'F'
    }

    toCommandString() {
        if (this.targetType === 'F') {
            return `W${this.worldId}B${this.amount}F${this.targetId}`;
        }
        return `W${this.worldId}B${this.amount}${this.targetType}`;
    }
}

class TransferCommand extends CommandNode {
    constructor(fleetId, amount, targetType, targetId = null) {
        super();
        this.fleetId = fleetId;
        this.amount = amount;
        this.targetType = targetType; // 'I', 'P', or 'F'
        this.targetId = targetId; // Fleet ID if targetType is 'F'
    }

    toCommandString() {
        if (this.targetType === 'F') {
            return `F${this.fleetId}T${this.amount}F${this.targetId}`;
        }
        return `F${this.fleetId}T${this.amount}${this.targetType}`;
    }
}

class FireWorldCommand extends CommandNode {
    constructor(fleetId, target) {
        super();
        this.fleetId = fleetId;
        this.target = target; // 'P' or 'I'
    }

    toCommandString() {
        return `F${this.fleetId}A${this.target}`;
    }
}

class FireFleetCommand extends CommandNode {
    constructor(fleetId, targetFleetId) {
        super();
        this.fleetId = fleetId;
        this.targetFleetId = targetFleetId;
    }

    toCommandString() {
        return `F${this.fleetId}AF${this.targetFleetId}`;
    }
}

class AmbushCommand extends CommandNode {
    constructor(fleetId) {
        super();
        this.fleetId = fleetId;
    }

    toCommandString() {
        return `F${this.fleetId}A`;
    }
}

class JoinCommand extends CommandNode {
    constructor(args) {
        super();
        this.args = args; // Full argument string
    }

    toCommandString() {
        return `JOIN ${this.args}`;
    }
}

class TurnCommand extends CommandNode {
    toCommandString() {
        return 'TURN';
    }
}

// Partial commands (incomplete input)

class PartialFleetCommand extends CommandNode {
    constructor(fleetId) {
        super();
        this.fleetId = fleetId;
    }

    toCommandString() {
        return `F${this.fleetId}`;
    }
}

class PartialWorldCommand extends CommandNode {
    constructor(worldId) {
        super();
        this.worldId = worldId;
    }

    toCommandString() {
        return `W${this.worldId}`;
    }
}

class PartialBuildCommand extends CommandNode {
    constructor(worldId, amount) {
        super();
        this.worldId = worldId;
        this.amount = amount;
    }

    toCommandString() {
        return `W${this.worldId}B${this.amount}`;
    }
}

class PartialTransferCommand extends CommandNode {
    constructor(fleetId, amount) {
        super();
        this.fleetId = fleetId;
        this.amount = amount;
    }

    toCommandString() {
        return `F${this.fleetId}T${this.amount}`;
    }
}

class PartialJoinCommand extends CommandNode {
    toCommandString() {
        return 'JOIN';
    }
}
