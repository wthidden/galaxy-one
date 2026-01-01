/**
 * ToastManager - Modern toast notification system
 * Provides non-intrusive notifications with accessibility support
 */
class ToastManager {
    constructor() {
        this.container = null;
        this.toasts = [];
        this.maxToasts = 5;
        this.initialize();
    }

    initialize() {
        // Create toast container
        this.container = document.createElement('div');
        this.container.id = 'toast-container';
        this.container.className = 'toast-container';
        this.container.setAttribute('role', 'region');
        this.container.setAttribute('aria-label', 'Notifications');
        this.container.setAttribute('aria-live', 'polite');
        document.body.appendChild(this.container);
    }

    /**
     * Show a toast notification
     * @param {string} message - Message to display
     * @param {string} type - Type: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duration in ms (0 = permanent)
     */
    show(message, type = 'info', duration = 4000) {
        const toast = {
            id: Date.now() + Math.random(),
            message,
            type,
            duration
        };

        this.toasts.push(toast);
        this.render(toast);

        if (duration > 0) {
            setTimeout(() => this.dismiss(toast.id), duration);
        }

        // Limit number of toasts
        if (this.toasts.length > this.maxToasts) {
            const oldestToast = this.toasts.shift();
            this.dismiss(oldestToast.id);
        }

        return toast.id;
    }

    render(toast) {
        const toastEl = document.createElement('div');
        toastEl.className = `toast toast-${toast.type}`;
        toastEl.id = `toast-${toast.id}`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-atomic', 'true');

        const icon = this.getIcon(toast.type);

        toastEl.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-content">
                <div class="toast-message">${this.escapeHTML(toast.message)}</div>
            </div>
            <button class="toast-close" aria-label="Dismiss notification">×</button>
        `;

        // Add close handler
        toastEl.querySelector('.toast-close').addEventListener('click', () => {
            this.dismiss(toast.id);
        });

        this.container.appendChild(toastEl);

        // Trigger animation
        requestAnimationFrame(() => {
            toastEl.classList.add('toast-enter');
        });
    }

    dismiss(toastId) {
        const toastEl = document.getElementById(`toast-${toastId}`);
        if (!toastEl) return;

        toastEl.classList.remove('toast-enter');
        toastEl.classList.add('toast-exit');

        setTimeout(() => {
            if (toastEl.parentNode) {
                toastEl.parentNode.removeChild(toastEl);
            }
            this.toasts = this.toasts.filter(t => t.id !== toastId);
        }, 300);
    }

    dismissAll() {
        this.toasts.forEach(toast => this.dismiss(toast.id));
    }

    getIcon(type) {
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        return icons[type] || icons.info;
    }

    escapeHTML(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Convenience methods
    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Create global instance
if (typeof window !== 'undefined') {
    window.toastManager = new ToastManager();
}
