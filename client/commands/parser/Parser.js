/**
 * Parser - Convert tokens to Abstract Syntax Tree (AST)
 *
 * Supports partial parsing for progressive feedback as users type
 */
class Parser {
    constructor() {
        this.tokens = [];
        this.pos = 0;
        this.context = null;
    }

    /**
     * Parse tokens (partial parse for live feedback)
     */
    parsePartial(tokens) {
        this.tokens = tokens;
        this.pos = 0;
        this.context = this.detectContext();

        try {
            const ast = this.parseCommand();
            return {
                ast,
                context: this.context,
                isComplete: this.isAtEnd(),
                errors: []
            };
        } catch (error) {
            return {
                ast: null,
                context: this.context,
                isComplete: false,
                errors: [error]
            };
        }
    }

    /**
     * Parse tokens (full parse for command submission)
     */
    parse(tokens) {
        const result = this.parsePartial(tokens);
        if (!result.isComplete && result.ast) {
            result.errors.push(new Error('Incomplete command'));
        }
        return result;
    }

    /**
     * Parse top-level command
     */
    parseCommand() {
        const token = this.peek();

        if (!token || token.type === TokenTypes.EOF) {
            return null;
        }

        switch (token.type) {
            case TokenTypes.FLEET_PREFIX:
                return this.parseFleetCommand();
            case TokenTypes.WORLD_PREFIX:
                return this.parseWorldCommand();
            case TokenTypes.JOIN:
                return this.parseJoinCommand();
            case TokenTypes.TURN:
                return this.parseTurnCommand();
            default:
                throw new Error(`Unexpected token: ${token.type} at position ${token.pos}`);
        }
    }

    /**
     * Parse fleet command: F<id><action>
     */
    parseFleetCommand() {
        this.expect(TokenTypes.FLEET_PREFIX);
        const fleetId = this.expect(TokenTypes.NUMBER).value;

        const next = this.peek();

        if (!next || next.type === TokenTypes.EOF) {
            // Partial: "F5"
            return new PartialFleetCommand(fleetId);
        }

        switch (next.type) {
            case TokenTypes.WORLD_PREFIX:
                // Move: F5W10 or F5W1W3W10
                return this.parseMoveCommand(fleetId);
            case TokenTypes.TRANSFER:
                // Transfer: F5T10I
                return this.parseTransferCommand(fleetId);
            case TokenTypes.ATTACK:
                // Fire or Ambush: F5A, F5AI, F5AP, F5AF10
                return this.parseAttackCommand(fleetId);
            default:
                throw new Error(`Expected action after fleet ID, got ${next.type}`);
        }
    }

    /**
     * Parse move command: F<id>W<id>[W<id>...]
     */
    parseMoveCommand(fleetId) {
        const path = [];

        while (this.peek()?.type === TokenTypes.WORLD_PREFIX) {
            this.advance(); // consume W
            const worldId = this.expect(TokenTypes.NUMBER).value;
            path.push(worldId);
        }

        if (path.length === 0) {
            throw new Error('Move command requires at least one world');
        }

        return new MoveCommand(fleetId, path);
    }

    /**
     * Parse transfer command: F<id>T<amount><target>
     */
    parseTransferCommand(fleetId) {
        this.expect(TokenTypes.TRANSFER);
        const amount = this.expect(TokenTypes.NUMBER).value;

        const target = this.peek();

        if (!target || target.type === TokenTypes.EOF) {
            return new PartialTransferCommand(fleetId, amount);
        }

        let targetType, targetId = null;

        if (target.type === TokenTypes.TARGET_INDUSTRY) {
            this.advance();
            targetType = 'I';
        } else if (target.type === TokenTypes.TARGET_POPULATION) {
            this.advance();
            targetType = 'P';
        } else if (target.type === TokenTypes.FLEET_PREFIX) {
            this.advance();
            targetId = this.expect(TokenTypes.NUMBER).value;
            targetType = 'F';
        } else {
            throw new Error(`Invalid transfer target: ${target.type}`);
        }

        return new TransferCommand(fleetId, amount, targetType, targetId);
    }

    /**
     * Parse attack command: F<id>A[target]
     */
    parseAttackCommand(fleetId) {
        this.expect(TokenTypes.ATTACK);

        const next = this.peek();

        if (!next || next.type === TokenTypes.EOF) {
            // Ambush: F5A
            return new AmbushCommand(fleetId);
        }

        if (next.type === TokenTypes.TARGET_POPULATION) {
            this.advance();
            return new FireWorldCommand(fleetId, 'P');
        }

        if (next.type === TokenTypes.TARGET_INDUSTRY) {
            this.advance();
            return new FireWorldCommand(fleetId, 'I');
        }

        if (next.type === TokenTypes.FLEET_PREFIX) {
            this.advance();
            const targetFleetId = this.expect(TokenTypes.NUMBER).value;
            return new FireFleetCommand(fleetId, targetFleetId);
        }

        // If no valid target, treat as ambush
        return new AmbushCommand(fleetId);
    }

    /**
     * Parse world command: W<id><action>
     */
    parseWorldCommand() {
        this.expect(TokenTypes.WORLD_PREFIX);
        const worldId = this.expect(TokenTypes.NUMBER).value;

        const next = this.peek();

        if (!next || next.type === TokenTypes.EOF) {
            return new PartialWorldCommand(worldId);
        }

        if (next.type === TokenTypes.BUILD) {
            return this.parseBuildCommand(worldId);
        }

        throw new Error(`Expected action after world ID, got ${next.type}`);
    }

    /**
     * Parse build command: W<id>B<amount><target>
     */
    parseBuildCommand(worldId) {
        this.expect(TokenTypes.BUILD);
        const amount = this.expect(TokenTypes.NUMBER).value;

        const target = this.peek();

        if (!target || target.type === TokenTypes.EOF) {
            return new PartialBuildCommand(worldId, amount);
        }

        let targetType, targetId = null;

        if (target.type === TokenTypes.TARGET_INDUSTRY) {
            this.advance();
            targetType = 'I';
        } else if (target.type === TokenTypes.TARGET_POPULATION) {
            this.advance();
            targetType = 'P';
        } else if (target.type === TokenTypes.FLEET_PREFIX) {
            this.advance();
            targetId = this.expect(TokenTypes.NUMBER).value;
            targetType = 'F';
        } else {
            throw new Error(`Invalid build target: ${target.type}`);
        }

        return new BuildCommand(worldId, amount, targetType, targetId);
    }

    /**
     * Parse join command: JOIN <args>
     */
    parseJoinCommand() {
        this.expect(TokenTypes.JOIN);
        const argsToken = this.peek();

        if (argsToken?.type === TokenTypes.JOIN_ARGS) {
            this.advance();
            return new JoinCommand(argsToken.value);
        }

        return new PartialJoinCommand();
    }

    /**
     * Parse turn command: TURN
     */
    parseTurnCommand() {
        this.expect(TokenTypes.TURN);
        return new TurnCommand();
    }

    /**
     * Detect context from tokens (for suggestions)
     */
    detectContext() {
        if (this.tokens.length === 0) {
            return { type: 'empty' };
        }

        const first = this.tokens[0];

        if (first.type === TokenTypes.FLEET_PREFIX) {
            return { type: 'fleet', stage: this.detectFleetStage() };
        }

        if (first.type === TokenTypes.WORLD_PREFIX) {
            return { type: 'world', stage: this.detectWorldStage() };
        }

        if (first.type === TokenTypes.JOIN) {
            return { type: 'join' };
        }

        if (first.type === TokenTypes.TURN) {
            return { type: 'turn' };
        }

        return { type: 'unknown' };
    }

    /**
     * Detect what stage of fleet command we're at
     */
    detectFleetStage() {
        const tokens = this.tokens;

        if (tokens.length <= 2) {
            return 'fleet_id';
        }

        const thirdToken = tokens[2];

        if (thirdToken.type === TokenTypes.WORLD_PREFIX) {
            return 'move_path';
        }

        if (thirdToken.type === TokenTypes.TRANSFER) {
            if (tokens.length <= 4) {
                return 'transfer_amount';
            }
            return 'transfer_target';
        }

        if (thirdToken.type === TokenTypes.ATTACK) {
            if (tokens.length <= 3) {
                return 'attack_type';
            }
            return 'attack_target';
        }

        return 'action';
    }

    /**
     * Detect what stage of world command we're at
     */
    detectWorldStage() {
        const tokens = this.tokens;

        if (tokens.length <= 2) {
            return 'world_id';
        }

        if (tokens[2].type === TokenTypes.BUILD) {
            if (tokens.length <= 4) {
                return 'build_amount';
            }
            return 'build_target';
        }

        return 'action';
    }

    // Utility methods

    peek() {
        return this.tokens[this.pos] || null;
    }

    advance() {
        return this.tokens[this.pos++];
    }

    expect(type) {
        const token = this.peek();
        if (!token || token.type !== type) {
            throw new Error(`Expected ${type}, got ${token?.type || 'EOF'} at position ${token?.pos || this.pos}`);
        }
        return this.advance();
    }

    isAtEnd() {
        return this.peek()?.type === TokenTypes.EOF;
    }
}
