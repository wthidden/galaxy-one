/**
 * ValidationResult - Wrapper for validation results
 */
class ValidationResult {
    constructor(isValid, warnings = [], errors = [], suggestions = []) {
        this.isValid = isValid;
        this.warnings = warnings;
        this.errors = errors;
        this.suggestions = suggestions;
    }

    /**
     * Add an error to the validation result
     */
    addError(error) {
        this.errors.push(error);
        this.isValid = false;
    }

    /**
     * Add a warning to the validation result
     */
    addWarning(warning) {
        this.warnings.push(warning);
    }

    /**
     * Add a suggestion to the validation result
     */
    addSuggestion(suggestion) {
        this.suggestions.push(suggestion);
    }

    /**
     * Check if there are any issues (errors or warnings)
     */
    hasIssues() {
        return this.errors.length > 0 || this.warnings.length > 0;
    }

    /**
     * Get a formatted message string
     */
    getMessage() {
        const parts = [];

        if (this.errors.length > 0) {
            parts.push('Errors: ' + this.errors.join(', '));
        }

        if (this.warnings.length > 0) {
            parts.push('Warnings: ' + this.warnings.join(', '));
        }

        if (this.suggestions.length > 0 && !this.isValid) {
            parts.push('Suggestions: ' + this.suggestions.join(', '));
        }

        return parts.join('\n');
    }

    /**
     * Create a valid result
     */
    static valid() {
        return new ValidationResult(true, [], [], []);
    }

    /**
     * Create an invalid result with errors
     */
    static invalid(...errors) {
        return new ValidationResult(false, [], errors, []);
    }
}
