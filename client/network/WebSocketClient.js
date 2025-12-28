/**
 * WebSocketClient - Handles WebSocket connection and messaging
 */
class WebSocketClient {
    constructor() {
        this.socket = null;
        this.handlers = new Map();
        this.reconnectDelay = 3000;
        this.isConnecting = false;
    }

    /**
     * Connect to WebSocket server
     */
    connect() {
        if (this.isConnecting || (this.socket && this.socket.readyState === WebSocket.OPEN)) {
            return;
        }

        this.isConnecting = true;
        const host = window.location.hostname;
        this.socket = new WebSocket(`ws://${host}:8765`);

        this.socket.onopen = () => {
            this.isConnecting = false;
            this._notifyHandlers('connected', null);
            console.log('Connected to server');
        };

        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this._handleMessage(data);
            } catch (e) {
                console.error('Failed to parse message:', e, event.data);
            }
        };

        this.socket.onclose = () => {
            this.isConnecting = false;
            this._notifyHandlers('disconnected', null);
            console.log('Disconnected from server');

            // Reconnect after delay
            setTimeout(() => this.connect(), this.reconnectDelay);
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this._notifyHandlers('error', error);
        };
    }

    /**
     * Send a message to server
     */
    send(message) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
            return true;
        }
        console.warn('Cannot send message: not connected');
        return false;
    }

    /**
     * Send a command
     */
    sendCommand(commandText) {
        return this.send({
            type: 'command',
            text: commandText
        });
    }

    /**
     * Send a chat message
     */
    sendChat(to, message) {
        return this.send({
            type: 'chat',
            to: to,
            message: message
        });
    }

    /**
     * Register a handler for a message type
     */
    on(messageType, handler) {
        if (!this.handlers.has(messageType)) {
            this.handlers.set(messageType, []);
        }
        this.handlers.get(messageType).push(handler);
    }

    /**
     * Unregister a handler
     */
    off(messageType, handler) {
        if (!this.handlers.has(messageType)) return;
        const handlers = this.handlers.get(messageType);
        const index = handlers.indexOf(handler);
        if (index >= 0) {
            handlers.splice(index, 1);
        }
    }

    /**
     * Check if connected
     */
    isConnected() {
        return this.socket && this.socket.readyState === WebSocket.OPEN;
    }

    /**
     * Close connection
     */
    close() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }

    // Private methods

    _handleMessage(data) {
        const messageType = data.type;

        // Notify specific handlers
        const handlers = this.handlers.get(messageType) || [];
        handlers.forEach(handler => {
            try {
                handler(data);
            } catch (e) {
                console.error(`Error in handler for ${messageType}:`, e);
            }
        });

        // Notify wildcard handlers
        const wildcardHandlers = this.handlers.get('*') || [];
        wildcardHandlers.forEach(handler => {
            try {
                handler(data);
            } catch (e) {
                console.error('Error in wildcard handler:', e);
            }
        });
    }

    _notifyHandlers(event, data) {
        const handlers = this.handlers.get(event) || [];
        handlers.forEach(handler => {
            try {
                handler(data);
            } catch (e) {
                console.error(`Error in ${event} handler:`, e);
            }
        });
    }
}

// Export singleton
const webSocketClient = new WebSocketClient();
