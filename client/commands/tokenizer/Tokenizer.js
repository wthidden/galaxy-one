/**
 * Tokenizer - Convert input string to tokens for parsing
 */
class Tokenizer {
    tokenize(input) {
        const tokens = [];
        let pos = 0;
        const text = input.trim().toUpperCase();

        while (pos < text.length) {
            // Fleet prefix: F followed by digit
            if (text[pos] === 'F' && pos + 1 < text.length && this.isDigit(text[pos + 1])) {
                tokens.push({ type: TokenTypes.FLEET_PREFIX, value: 'F', pos });
                pos++;
                continue;
            }

            // World prefix: W followed by digit
            if (text[pos] === 'W' && pos + 1 < text.length && this.isDigit(text[pos + 1])) {
                tokens.push({ type: TokenTypes.WORLD_PREFIX, value: 'W', pos });
                pos++;
                continue;
            }

            // Build action: B
            if (text[pos] === 'B') {
                tokens.push({ type: TokenTypes.BUILD, value: 'B', pos });
                pos++;
                continue;
            }

            // Transfer action: T
            if (text[pos] === 'T') {
                tokens.push({ type: TokenTypes.TRANSFER, value: 'T', pos });
                pos++;
                continue;
            }

            // Attack action: A
            if (text[pos] === 'A') {
                tokens.push({ type: TokenTypes.ATTACK, value: 'A', pos });
                pos++;
                continue;
            }

            // Target industry: I
            if (text[pos] === 'I') {
                tokens.push({ type: TokenTypes.TARGET_INDUSTRY, value: 'I', pos });
                pos++;
                continue;
            }

            // Target population: P
            if (text[pos] === 'P') {
                tokens.push({ type: TokenTypes.TARGET_POPULATION, value: 'P', pos });
                pos++;
                continue;
            }

            // Numbers
            if (this.isDigit(text[pos])) {
                const start = pos;
                while (pos < text.length && this.isDigit(text[pos])) {
                    pos++;
                }
                const value = parseInt(text.substring(start, pos));
                tokens.push({ type: TokenTypes.NUMBER, value, pos: start });
                continue;
            }

            // JOIN command
            if (text.startsWith('JOIN', pos)) {
                tokens.push({ type: TokenTypes.JOIN, value: 'JOIN', pos });
                pos += 4;
                // Capture rest of input as join args (preserve original case for name)
                const rest = input.substring(pos + (input.length - text.length)).trim();
                if (rest) {
                    tokens.push({ type: TokenTypes.JOIN_ARGS, value: rest, pos });
                }
                break;
            }

            // TURN command
            if (text.startsWith('TURN', pos)) {
                tokens.push({ type: TokenTypes.TURN, value: 'TURN', pos });
                break;
            }

            // Whitespace (ignore)
            if (text[pos] === ' ') {
                pos++;
                continue;
            }

            // Unknown character
            tokens.push({ type: TokenTypes.UNKNOWN, value: text[pos], pos });
            pos++;
        }

        tokens.push({ type: TokenTypes.EOF, value: null, pos: text.length });
        return tokens;
    }

    isDigit(char) {
        return char && char >= '0' && char <= '9';
    }
}
