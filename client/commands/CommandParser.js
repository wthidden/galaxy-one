/**
 * CommandParser - Main entry point for command processing
 *
 * Orchestrates tokenization, parsing, validation, and suggestions
 */
class CommandParser {
    constructor(gameState) {
        this.gameState = gameState;
        this.tokenizer = new Tokenizer();
        this.parser = new Parser();
        // Initialize validator (Phase 2)
        this.validator = new Validator(gameState);
        // Initialize auto-complete (Phase 3)
        this.suggester = new AutoComplete(gameState);
        // Initialize command history (Phase 4)
        this.history = new CommandHistory();
        // Builder will be added in Phase 5 (optional)
        this.builder = null;
    }

    /**
     * Parse input progressively (for live feedback)
     *
     * Returns: {
     *   ast: CommandAST | null,
     *   validation: ValidationResult | null,
     *   suggestions: Suggestion[] | null,
     *   errors: Error[],
     *   context: Object,
     *   isComplete: boolean
     * }
     */
    parseProgressive(input) {
        // Tokenize
        const tokens = this.tokenizer.tokenize(input);

        // Parse (tolerant of incomplete input)
        const parseResult = this.parser.parsePartial(tokens);

        // Validate (partial validation) - Phase 2
        let validation = null;
        if (this.validator && parseResult.ast) {
            validation = this.validator.validate(parseResult.ast, {
                partial: true,
                context: parseResult.context
            });
        }

        // Generate suggestions - Phase 3
        let suggestions = null;
        if (this.suggester) {
            suggestions = this.suggester.suggest(
                input,
                parseResult.context,
                validation
            );
        }

        return {
            ast: parseResult.ast,
            validation,
            suggestions,
            errors: parseResult.errors,
            context: parseResult.context,
            isComplete: parseResult.isComplete
        };
    }

    /**
     * Parse complete command (for submission)
     *
     * Returns: {
     *   ast: CommandAST | null,
     *   validation: ValidationResult | null,
     *   command: string | null,
     *   errors: Error[]
     * }
     */
    parseFinal(input) {
        const tokens = this.tokenizer.tokenize(input);
        const parseResult = this.parser.parse(tokens);

        // Validate - Phase 2
        let validation = null;
        if (this.validator && parseResult.ast) {
            validation = this.validator.validate(parseResult.ast, {
                partial: false
            });
        } else if (!parseResult.ast) {
            // Create a fake validation result for parse errors
            validation = {
                isValid: false,
                errors: parseResult.errors.map(e => e.message),
                warnings: [],
                suggestions: []
            };
        }

        // Add to history if valid - Phase 4
        if (validation && validation.isValid && this.history) {
            this.history.add(input);
        }

        return {
            ast: parseResult.ast,
            validation,
            command: (validation && validation.isValid && parseResult.ast) ?
                parseResult.ast.toCommandString() : null,
            errors: parseResult.errors
        };
    }

    /**
     * Get command from history (Phase 4)
     *
     * @param {string} direction - 'up' or 'down'
     * @returns {string|null} - Command from history or null
     */
    getHistory(direction) {
        if (!this.history) return null;
        return this.history.navigate(direction);
    }

    /**
     * Reset history position (Phase 4)
     */
    resetHistory() {
        if (this.history) {
            this.history.reset();
        }
    }

    /**
     * Open interactive builder (Phase 5)
     *
     * @param {string} commandType - Optional command type to start with
     * @returns {Promise<string|null>} - Generated command or null if cancelled
     */
    openBuilder(commandType = null) {
        if (!this.builder) {
            return Promise.resolve(null);
        }
        return this.builder.open(commandType);
    }

    /**
     * Set validator (called during Phase 2 integration)
     */
    setValidator(validator) {
        this.validator = validator;
    }

    /**
     * Set auto-complete suggester (called during Phase 3 integration)
     */
    setSuggester(suggester) {
        this.suggester = suggester;
    }

    /**
     * Set command history (called during Phase 4 integration)
     */
    setHistory(history) {
        this.history = history;
    }

    /**
     * Set command builder (called during Phase 5 integration)
     */
    setBuilder(builder) {
        this.builder = builder;
    }
}
