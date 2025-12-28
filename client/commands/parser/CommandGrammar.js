/**
 * CommandGrammar - Grammar rules for StarWeb commands
 *
 * This file documents the formal grammar used by the parser.
 * BNF-like notation is used for clarity.
 */

const CommandGrammar = {
    /**
     * Top-level command rule
     *
     * Command ::= FleetCommand | WorldCommand | JoinCommand | TurnCommand
     */
    Command: [
        'FleetCommand',
        'WorldCommand',
        'JoinCommand',
        'TurnCommand'
    ],

    /**
     * Fleet commands
     *
     * FleetCommand ::= FLEET_PREFIX NUMBER (MoveAction | TransferAction | AttackAction)
     */
    FleetCommand: {
        prefix: 'FLEET_PREFIX',
        id: 'NUMBER',
        actions: ['MoveAction', 'TransferAction', 'AttackAction']
    },

    /**
     * Move action
     *
     * MoveAction ::= (WORLD_PREFIX NUMBER)+
     *
     * Examples:
     *   F5W10        - Move fleet 5 to world 10
     *   F5W1W3W10    - Move fleet 5 via path: 1 → 3 → 10
     */
    MoveAction: {
        pattern: '(WORLD_PREFIX NUMBER)+',
        minOccurrences: 1
    },

    /**
     * Transfer action
     *
     * TransferAction ::= TRANSFER NUMBER (TARGET_INDUSTRY | TARGET_POPULATION | FLEET_PREFIX NUMBER)
     *
     * Examples:
     *   F5T10I       - Transfer 10 to industry
     *   F5T10P       - Transfer 10 to population
     *   F5T10F7      - Transfer 10 to fleet 7
     */
    TransferAction: {
        action: 'TRANSFER',
        amount: 'NUMBER',
        target: ['TARGET_INDUSTRY', 'TARGET_POPULATION', 'FLEET_PREFIX NUMBER']
    },

    /**
     * Attack action
     *
     * AttackAction ::= ATTACK [TARGET_POPULATION | TARGET_INDUSTRY | FLEET_PREFIX NUMBER]
     *
     * Examples:
     *   F5A          - Ambush (no target)
     *   F5AP         - Fire at world population
     *   F5AI         - Fire at world industry
     *   F5AF10       - Fire at fleet 10
     */
    AttackAction: {
        action: 'ATTACK',
        target: ['TARGET_POPULATION', 'TARGET_INDUSTRY', 'FLEET_PREFIX NUMBER', 'null']
    },

    /**
     * World commands
     *
     * WorldCommand ::= WORLD_PREFIX NUMBER BuildAction
     */
    WorldCommand: {
        prefix: 'WORLD_PREFIX',
        id: 'NUMBER',
        actions: ['BuildAction']
    },

    /**
     * Build action
     *
     * BuildAction ::= BUILD NUMBER (TARGET_INDUSTRY | TARGET_POPULATION | FLEET_PREFIX NUMBER)
     *
     * Examples:
     *   W3B25I       - Build 25 industry
     *   W3B25P       - Build 25 pships
     *   W3B10F7      - Build 10 ships to fleet 7
     */
    BuildAction: {
        action: 'BUILD',
        amount: 'NUMBER',
        target: ['TARGET_INDUSTRY', 'TARGET_POPULATION', 'FLEET_PREFIX NUMBER']
    },

    /**
     * Join command
     *
     * JoinCommand ::= JOIN JOIN_ARGS
     *
     * Example:
     *   JOIN PlayerName EmpireBuilder
     */
    JoinCommand: {
        command: 'JOIN',
        args: 'JOIN_ARGS'
    },

    /**
     * Turn command
     *
     * TurnCommand ::= TURN
     *
     * Example:
     *   TURN
     */
    TurnCommand: {
        command: 'TURN'
    }
};

/**
 * Helper to validate grammar structure
 */
function validateGrammar() {
    // This could be extended to actually validate the grammar structure
    // For now, it's just documentation
    return true;
}
