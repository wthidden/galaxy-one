/**
 * CommandInput - Enhanced command input with parser integration
 *
 * Replaces CommandHint.js with full parser integration
 */
class CommandInput {
    constructor(inputElement, hintElement, gameState) {
        this.inputElement = inputElement;
        this.hintElement = hintElement;
        this.gameState = gameState;
        this.parser = new CommandParser(gameState);
        this.suggestionBox = null;
        this.currentSuggestions = [];
        this.selectedSuggestionIndex = -1;

        this.setupEventListeners();
        this.createSuggestionBox();
    }

    /**
     * Setup event listeners for input
     */
    setupEventListeners() {
        // Input event - progressive parsing
        this.inputElement.addEventListener('input', (e) => {
            this.onInput(e.target.value);
        });

        // Keydown - history navigation and suggestion selection
        this.inputElement.addEventListener('keydown', (e) => {
            this.onKeyDown(e);
        });

        // Focus - show suggestions
        this.inputElement.addEventListener('focus', () => {
            if (this.currentSuggestions.length > 0) {
                this.suggestionBox.style.display = 'block';
            }
        });

        // Blur - hide suggestions after delay
        this.inputElement.addEventListener('blur', () => {
            // Delay to allow clicking suggestions
            setTimeout(() => {
                this.suggestionBox.style.display = 'none';
            }, 200);
        });
    }

    /**
     * Handle input changes
     */
    onInput(value) {
        const result = this.parser.parseProgressive(value);

        // Update hints
        this.updateHints(result);

        // Update suggestions
        if (result.suggestions) {
            this.updateSuggestions(result.suggestions);
        } else {
            this.updateSuggestions([]);
        }

        // Reset history navigation
        this.parser.resetHistory();
    }

    /**
     * Handle keyboard events
     */
    onKeyDown(e) {
        if (e.key === 'ArrowUp') {
            e.preventDefault();

            if (this.currentSuggestions.length > 0 && this.suggestionBox.style.display !== 'none') {
                // Navigate suggestions
                if (this.selectedSuggestionIndex === -1) {
                    this.selectedSuggestionIndex = 0;
                } else {
                    this.selectedSuggestionIndex = Math.max(0, this.selectedSuggestionIndex - 1);
                }
                this.highlightSuggestion();
            } else {
                // Navigate history
                const cmd = this.parser.getHistory('up');
                if (cmd) {
                    this.inputElement.value = cmd;
                    this.onInput(cmd);
                }
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();

            if (this.currentSuggestions.length > 0 && this.suggestionBox.style.display !== 'none') {
                // Navigate suggestions
                this.selectedSuggestionIndex = Math.min(
                    this.currentSuggestions.length - 1,
                    this.selectedSuggestionIndex + 1
                );
                this.highlightSuggestion();
            } else {
                // Navigate history
                const cmd = this.parser.getHistory('down');
                if (cmd !== null) {
                    this.inputElement.value = cmd;
                    this.onInput(cmd);
                } else {
                    this.inputElement.value = '';
                    this.onInput('');
                }
            }
        } else if (e.key === 'Tab') {
            e.preventDefault();

            // Accept current suggestion
            if (this.selectedSuggestionIndex >= 0 && this.currentSuggestions.length > 0) {
                const suggestion = this.currentSuggestions[this.selectedSuggestionIndex];
                this.applySuggestion(suggestion);
            } else if (this.currentSuggestions.length > 0) {
                // Accept first suggestion
                this.applySuggestion(this.currentSuggestions[0]);
            }
        } else if (e.key === 'Escape') {
            this.suggestionBox.style.display = 'none';
            this.selectedSuggestionIndex = -1;
        } else {
            // Reset suggestion selection on other keys
            this.selectedSuggestionIndex = -1;
        }
    }

    /**
     * Update hint display based on parse result
     */
    updateHints(result) {
        let html = '';

        // Show multi-hop path indicator for move commands
        if (result.context && result.context.stage === 'move_path' && result.suggestions && result.suggestions.length > 0) {
            const firstSuggestion = result.suggestions[0];
            if (firstSuggestion.pathInfo) {
                html += `<div class="hint-path">🗺️ ${this.escapeHtml(firstSuggestion.pathInfo)} → ?</div>`;
            }
        }

        // Parse errors
        if (result.errors && result.errors.length > 0) {
            html += '<div class="hint-errors">';
            result.errors.forEach(err => {
                html += `<div class="error">❌ ${this.escapeHtml(err.message || err)}</div>`;
            });
            html += '</div>';
        }

        // Validation errors/warnings
        if (result.validation) {
            if (!result.validation.isValid && result.validation.errors.length > 0) {
                html += '<div class="hint-validation">';
                result.validation.errors.forEach(err => {
                    html += `<div class="error">❌ ${this.escapeHtml(err)}</div>`;
                });
                if (result.validation.warnings.length > 0) {
                    result.validation.warnings.forEach(warn => {
                        html += `<div class="warning">⚠️  ${this.escapeHtml(warn)}</div>`;
                    });
                }
                if (result.validation.suggestions.length > 0) {
                    html += `<div class="suggestions-text">💡 ${this.escapeHtml(result.validation.suggestions[0])}</div>`;
                }
                html += '</div>';
            } else if (result.validation.isValid && result.isComplete) {
                html += '<div class="hint-success">✓ Valid command</div>';
            } else if (result.validation.warnings.length > 0) {
                html += '<div class="hint-validation">';
                result.validation.warnings.forEach(warn => {
                    html += `<div class="warning">⚠️  ${this.escapeHtml(warn)}</div>`;
                });
                html += '</div>';
            }
        }

        this.hintElement.innerHTML = html;
    }

    /**
     * Create suggestion dropdown box
     */
    createSuggestionBox() {
        this.suggestionBox = document.createElement('div');
        this.suggestionBox.className = 'command-suggestions';
        this.suggestionBox.style.display = 'none';

        // Insert after hint element
        const parent = this.inputElement.parentElement;
        parent.style.position = 'relative';
        parent.appendChild(this.suggestionBox);
    }

    /**
     * Update suggestion display
     */
    updateSuggestions(suggestions) {
        this.currentSuggestions = suggestions;
        this.selectedSuggestionIndex = -1;

        if (suggestions.length === 0) {
            this.suggestionBox.innerHTML = '';
            this.suggestionBox.style.display = 'none';
            return;
        }

        let html = '<div class="suggestion-list">';
        suggestions.forEach((sug, index) => {
            const highlight = sug.highlight === 'danger' ? 'danger' : '';
            html += `
                <div class="suggestion-item ${highlight}" data-index="${index}">
                    <span class="suggestion-text">${this.escapeHtml(sug.text)}</span>
                    <span class="suggestion-description">${this.escapeHtml(sug.description)}</span>
                </div>
            `;
        });
        html += '</div>';

        this.suggestionBox.innerHTML = html;
        this.suggestionBox.style.display = 'block';

        // Add click listeners
        this.suggestionBox.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const index = parseInt(item.dataset.index);
                this.applySuggestion(this.currentSuggestions[index]);
            });
        });
    }

    /**
     * Highlight selected suggestion
     */
    highlightSuggestion() {
        const items = this.suggestionBox.querySelectorAll('.suggestion-item');
        items.forEach((item, index) => {
            if (index === this.selectedSuggestionIndex) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }

    /**
     * Apply a suggestion to the input
     */
    applySuggestion(suggestion) {
        this.inputElement.value = suggestion.text;
        this.onInput(suggestion.text);

        if (suggestion.complete) {
            this.suggestionBox.style.display = 'none';
        } else {
            this.inputElement.focus();
        }
    }

    /**
     * Escape HTML for safe display
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
