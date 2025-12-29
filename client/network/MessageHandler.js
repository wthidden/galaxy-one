/**
 * MessageHandler - Routes server messages to appropriate handlers
 */
class MessageHandler {
    constructor(webSocketClient, gameState) {
        this.ws = webSocketClient;
        this.gameState = gameState;
        this.setupHandlers();
    }

    setupHandlers() {
        // Welcome message
        this.ws.on('welcome', (data) => {
            console.log(`Connected. Player ID: ${data.id}`);
            this._logMessage(`Connected. ID: ${data.id}`);
        });

        // Full state update
        this.ws.on('update', (data) => {
            this.gameState.applyFullUpdate(data.state);
        });

        // Delta update
        this.ws.on('delta', (data) => {
            this.gameState.applyDelta(data.changes);
        });

        // Timer tick
        this.ws.on('timer', (data) => {
            this.gameState.applyTimerTick(data);
        });

        // Info message
        this.ws.on('info', (data) => {
            this._logMessage(data.text);
        });

        // Error message
        this.ws.on('error', (data) => {
            this._logMessage(`Error: ${data.text}`, 'error');
        });

        // Event message
        this.ws.on('event', (data) => {
            this._logEvent(data.text, data.event_type);
        });

        // Animation message
        this.ws.on('animate', (data) => {
            this._handleAnimation(data);
        });

        // Chat message
        this.ws.on('chat', (data) => {
            this._handleChat(data);
        });

        // Admin message
        this.ws.on('admin_message', (data) => {
            this._handleAdminMessage(data);
        });

        // Connection status
        this.ws.on('connected', () => {
            this._updateConnectionStatus('Connected', '#4caf50');
        });

        this.ws.on('disconnected', () => {
            this._updateConnectionStatus('Disconnected', '#f44336');
        });

        this.ws.on('error', () => {
            this._updateConnectionStatus('Error', '#f44336');
        });
    }

    // Private methods

    _logMessage(message, type = 'info') {
        const logDiv = document.getElementById('log');
        if (logDiv) {
            const entry = document.createElement('div');
            entry.textContent = message;
            if (type === 'error') {
                entry.style.color = '#f44336';
            }
            logDiv.appendChild(entry);
            logDiv.scrollTop = logDiv.scrollHeight;
        }
    }

    _logEvent(message, eventType = 'info') {
        const eventLogDiv = document.getElementById('event-log');
        if (eventLogDiv) {
            const entry = document.createElement('div');
            entry.className = `event-${eventType}`;
            entry.innerHTML = this._parseMarkdown(message);
            eventLogDiv.appendChild(entry);
            eventLogDiv.scrollTop = eventLogDiv.scrollHeight;

            // Keep only last 50 events
            while (eventLogDiv.children.length > 50) {
                eventLogDiv.removeChild(eventLogDiv.firstChild);
            }
        }
    }

    _parseMarkdown(text) {
        // Bold
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Italic
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        // Code
        text = text.replace(/`(.*?)`/g, '<code>$1</code>');
        return text;
    }

    _updateConnectionStatus(status, color) {
        const statusDiv = document.getElementById('connection-status');
        if (statusDiv) {
            statusDiv.textContent = status;
            statusDiv.style.color = color;
        }
    }

    _handleAnimation(data) {
        // Animation data will be handled by animator system
        // For now, just log it
        console.log('Animation:', data);

        // Dispatch custom event for animator to pick up
        window.dispatchEvent(new CustomEvent('game-animation', {
            detail: data
        }));
    }

    _handleChat(data) {
        this._logMessage(`[${data.from}]: ${data.message}`, 'chat');

        // Could show in separate chat UI
        window.dispatchEvent(new CustomEvent('game-chat', {
            detail: data
        }));
    }

    _handleAdminMessage(data) {
        const adminPanel = document.getElementById('admin-message-panel');
        const adminContent = document.getElementById('admin-message-content');

        if (adminPanel && adminContent) {
            // Update content with markdown parsing
            adminContent.innerHTML = this._parseMarkdown(data.text);

            // Show panel (expand if collapsed)
            adminPanel.style.display = 'block';
            adminPanel.classList.remove('collapsed');

            // Add flash animation to indicate new message
            adminPanel.classList.add('flash');
            setTimeout(() => {
                adminPanel.classList.remove('flash');
            }, 1000);

            // Auto-collapse after 10 seconds
            if (adminPanel._collapseTimeout) {
                clearTimeout(adminPanel._collapseTimeout);
            }
            adminPanel._collapseTimeout = setTimeout(() => {
                adminPanel.classList.add('collapsed');
            }, 10000);

            // Click to re-expand
            adminPanel.onclick = () => {
                if (adminPanel.classList.contains('collapsed')) {
                    adminPanel.classList.remove('collapsed');
                    // Auto-collapse again after 10 seconds
                    if (adminPanel._collapseTimeout) {
                        clearTimeout(adminPanel._collapseTimeout);
                    }
                    adminPanel._collapseTimeout = setTimeout(() => {
                        adminPanel.classList.add('collapsed');
                    }, 10000);
                }
            };
        }
    }
}
