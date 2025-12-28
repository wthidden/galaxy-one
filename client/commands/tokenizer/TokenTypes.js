/**
 * TokenTypes - Token type definitions for command parser
 */
const TokenTypes = {
    // Prefixes
    FLEET_PREFIX: 'FLEET_PREFIX',       // F
    WORLD_PREFIX: 'WORLD_PREFIX',       // W

    // Actions
    BUILD: 'BUILD',                     // B
    TRANSFER: 'TRANSFER',               // T
    ATTACK: 'ATTACK',                   // A

    // Targets
    TARGET_INDUSTRY: 'TARGET_INDUSTRY', // I
    TARGET_POPULATION: 'TARGET_POPULATION', // P

    // Values
    NUMBER: 'NUMBER',                   // 0-9+

    // Commands
    JOIN: 'JOIN',                       // JOIN
    TURN: 'TURN',                       // TURN
    JOIN_ARGS: 'JOIN_ARGS',            // Arguments for JOIN command

    // Special
    UNKNOWN: 'UNKNOWN',                 // Unrecognized character
    EOF: 'EOF'                          // End of input
};
