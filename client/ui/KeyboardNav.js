/**
 * KeyboardNav - Enhanced keyboard navigation for StarWeb
 * Provides keyboard shortcuts and accessible navigation
 */
class KeyboardNav {
    constructor() {
        this.focusableSelectors = 'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])';
        this.setupGlobalHandlers();
    }

    setupGlobalHandlers() {
        document.addEventListener('keydown', (e) => {
            // Skip if typing in input
            if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) {
                return;
            }

            switch(e.key) {
                case '/':
                    e.preventDefault();
                    this.focusChatInput();
                    break;
                case 'Escape':
                    this.clearFocus();
                    break;
                case 'g':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.focusGamesList();
                    }
                    break;
            }
        });
    }

    focusChatInput() {
        const chatInput = document.getElementById('lobby-chat-input');
        if (chatInput) {
            chatInput.focus();
            this.announceToScreenReader('Chat input focused');
        }
    }

    focusGamesList() {
        const firstGame = document.querySelector('.game-card');
        if (firstGame) {
            firstGame.focus();
            this.announceToScreenReader('Game list focused');
        }
    }

    clearFocus() {
        if (document.activeElement) {
            document.activeElement.blur();
        }
    }

    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', 'polite');
        announcement.className = 'sr-only';
        announcement.textContent = message;
        document.body.appendChild(announcement);

        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    /**
     * Make a list navigable with arrow keys
     */
    makeListNavigable(listElement) {
        const items = Array.from(listElement.querySelectorAll('.game-card'));

        items.forEach((item, index) => {
            item.setAttribute('tabindex', '0');
            item.setAttribute('role', 'button');

            item.addEventListener('keydown', (e) => {
                switch(e.key) {
                    case 'ArrowDown':
                        e.preventDefault();
                        if (index < items.length - 1) {
                            items[index + 1].focus();
                        }
                        break;
                    case 'ArrowUp':
                        e.preventDefault();
                        if (index > 0) {
                            items[index - 1].focus();
                        }
                        break;
                    case 'Enter':
                    case ' ':
                        e.preventDefault();
                        item.click();
                        break;
                }
            });
        });
    }

    /**
     * Update navigable lists after content changes
     */
    updateListNavigation() {
        const myGamesList = document.getElementById('my-games-list');
        const availableGamesList = document.getElementById('available-games-list');

        if (myGamesList) {
            this.makeListNavigable(myGamesList);
        }
        if (availableGamesList) {
            this.makeListNavigable(availableGamesList);
        }
    }
}

// Initialize
if (typeof window !== 'undefined') {
    window.keyboardNav = new KeyboardNav();
}
