/**
 * ModalManager - Modern modal dialog system
 * Provides accessible modal dialogs with focus management
 */
class ModalManager {
    constructor() {
        this.activeModal = null;
        this.focusTrap = null;
        this.escapeHandler = null;
        this.previousFocus = null;
    }

    /**
     * Show a modal dialog
     * @param {Object} options - Modal configuration
     */
    show(options) {
        const {
            title,
            content,
            buttons = [],
            closeOnOverlay = true,
            closeOnEscape = true,
            size = 'medium', // small, medium, large
            className = ''
        } = options;

        this.hide(); // Close any existing modal

        // Save current focus to restore later
        this.previousFocus = document.activeElement;

        const modal = document.createElement('div');
        modal.className = `modal modal-${size} ${className}`;
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-labelledby', 'modal-title');

        modal.innerHTML = `
            <div class="modal-overlay"></div>
            <div class="modal-dialog">
                <div class="modal-content-wrapper">
                    <div class="modal-header">
                        <h2 id="modal-title">${this.escapeHTML(title)}</h2>
                        <button class="modal-close" aria-label="Close dialog">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M18 6L6 18M6 6l12 12" stroke-width="2" stroke-linecap="round"/>
                            </svg>
                        </button>
                    </div>
                    <div class="modal-body">
                        ${typeof content === 'string' ? content : ''}
                    </div>
                    ${buttons.length > 0 ? `
                        <div class="modal-footer">
                            ${buttons.map((btn, idx) => `
                                <button class="btn ${btn.className || 'btn-ghost'}" data-button-index="${idx}">
                                    ${this.escapeHTML(btn.text)}
                                </button>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.activeModal = modal;

        // If content is a function, render it
        if (typeof content === 'function') {
            const bodyEl = modal.querySelector('.modal-body');
            content(bodyEl);
        }

        // Event listeners
        const closeBtn = modal.querySelector('.modal-close');
        const overlay = modal.querySelector('.modal-overlay');

        closeBtn.addEventListener('click', () => this.hide());

        if (closeOnOverlay) {
            overlay.addEventListener('click', () => this.hide());
        }

        if (closeOnEscape) {
            this.escapeHandler = (e) => {
                if (e.key === 'Escape') this.hide();
            };
            document.addEventListener('keydown', this.escapeHandler);
        }

        // Button handlers
        buttons.forEach((btn, idx) => {
            const btnEl = modal.querySelector(`[data-button-index="${idx}"]`);
            btnEl.addEventListener('click', async () => {
                if (btn.onClick) {
                    const result = await btn.onClick();
                    if (result !== false) this.hide();
                } else {
                    this.hide();
                }
            });
        });

        // Focus management
        this.setupFocusTrap(modal);

        // Animate in
        requestAnimationFrame(() => {
            modal.classList.add('modal-open');
        });

        // Focus first focusable element
        const firstFocusable = modal.querySelector('button, input, select, textarea');
        if (firstFocusable) {
            setTimeout(() => firstFocusable.focus(), 100);
        }
    }

    hide() {
        if (!this.activeModal) return;

        const modal = this.activeModal;
        modal.classList.remove('modal-open');
        modal.classList.add('modal-closing');

        if (this.escapeHandler) {
            document.removeEventListener('keydown', this.escapeHandler);
            this.escapeHandler = null;
        }

        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
            this.activeModal = null;

            // Restore previous focus
            if (this.previousFocus) {
                this.previousFocus.focus();
                this.previousFocus = null;
            }
        }, 300);
    }

    setupFocusTrap(modal) {
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];

        this.focusTrap = (e) => {
            if (e.key !== 'Tab') return;

            if (e.shiftKey) {
                if (document.activeElement === firstFocusable) {
                    e.preventDefault();
                    lastFocusable.focus();
                }
            } else {
                if (document.activeElement === lastFocusable) {
                    e.preventDefault();
                    firstFocusable.focus();
                }
            }
        };

        modal.addEventListener('keydown', this.focusTrap);
    }

    escapeHTML(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Confirm dialog helper
     */
    confirm(title, message, confirmText = 'Confirm', cancelText = 'Cancel') {
        return new Promise((resolve) => {
            this.show({
                title,
                content: `<p>${this.escapeHTML(message)}</p>`,
                buttons: [
                    {
                        text: cancelText,
                        className: 'btn-ghost',
                        onClick: () => resolve(false)
                    },
                    {
                        text: confirmText,
                        className: 'btn-primary',
                        onClick: () => resolve(true)
                    }
                ]
            });
        });
    }

    /**
     * Alert dialog helper
     */
    alert(title, message, buttonText = 'OK') {
        return new Promise((resolve) => {
            this.show({
                title,
                content: `<p>${this.escapeHTML(message)}</p>`,
                buttons: [
                    {
                        text: buttonText,
                        className: 'btn-primary',
                        onClick: () => resolve(true)
                    }
                ]
            });
        });
    }
}

// Global instance
if (typeof window !== 'undefined') {
    window.modalManager = new ModalManager();
}
