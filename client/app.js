/**
 * StarWeb App - Main Application Controller
 * Handles screen routing: Login → Lobby → Game
 */

class StarWebApp {
    constructor() {
        this.currentScreen = null;
        this.sessionData = null;
        this.ws = null;
        this.appContainer = null;

        // Screens
        this.loginScreen = null;
        this.lobbyScreen = null;

        // Current game info
        this.currentGame = null;
    }

    /**
     * Initialize the application
     */
    async initialize() {
        console.log('Initializing StarWeb App...');

        // Create app container
        this.appContainer = document.getElementById('app-container');
        if (!this.appContainer) {
            this.appContainer = document.createElement('div');
            this.appContainer.id = 'app-container';
            document.body.appendChild(this.appContainer);
        }

        // Connect to WebSocket
        await this.connectWebSocket();

        // Check for saved session
        if (LoginScreen.hasSavedSession()) {
            const savedSession = LoginScreen.getSavedSession();
            console.log('Found saved session, validating...');
            this.validateSavedSession(savedSession);
        } else {
            // Show login screen
            this.showLoginScreen();
        }
    }

    /**
     * Connect to WebSocket server
     */
    async connectWebSocket() {
        return new Promise((resolve, reject) => {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.hostname}:8765`;

            console.log(`Connecting to ${wsUrl}...`);

            this.ws = new WebSocket(wsUrl);
            window.ws = this.ws; // Make available globally for screens

            this.ws.onopen = () => {
                console.log('WebSocket connected');
                resolve();
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.showConnectionError();
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.handleDisconnect();
            };

            this.ws.onmessage = (event) => {
                this.handleMessage(event.data);
            };

            // Timeout after 5 seconds
            setTimeout(() => {
                if (this.ws.readyState !== WebSocket.OPEN) {
                    reject(new Error('Connection timeout'));
                }
            }, 5000);
        });
    }

    /**
     * Handle incoming WebSocket messages
     */
    handleMessage(rawData) {
        try {
            const data = JSON.parse(rawData);
            const type = data.type;

            console.log('Received message:', type, data);

            // Route messages based on type
            switch (type) {
                // Auth responses
                case 'AUTH_SUCCESS':
                    this.handleAuthSuccess(data);
                    break;

                case 'SESSION_VALID':
                    this.handleSessionValid(data);
                    break;

                case 'SESSION_INVALID':
                    this.handleSessionInvalid();
                    break;

                case 'LOGOUT_SUCCESS':
                    this.handleLogoutSuccess();
                    break;

                // Lobby responses
                case 'GAMES_LIST':
                    this.handleGamesList(data);
                    break;

                case 'GAME_CREATED':
                    this.handleGameCreated(data);
                    break;

                case 'GAME_JOINED':
                    this.handleGameJoined(data);
                    break;

                case 'GAME_INFO':
                    this.handleGameInfo(data);
                    break;

                // Lobby chat
                case 'LOBBY_CHAT':
                    this.handleLobbyChat(data);
                    break;

                // Game messages - forward to game screen if active
                case 'update':
                case 'delta':
                case 'timer':
                case 'event':
                case 'chat':
                    if (this.currentScreen === 'game' && window.messageHandler) {
                        window.messageHandler.handleMessage(data);
                    }
                    break;

                // Error messages
                case 'error':
                    this.handleError(data.text);
                    break;

                case 'info':
                    console.log('Info:', data.text);
                    break;

                default:
                    console.log('Unhandled message type:', type);
            }
        } catch (error) {
            console.error('Error handling message:', error);
        }
    }

    /**
     * Validate saved session with server
     */
    validateSavedSession(sessionData) {
        const message = {
            type: 'VALIDATE_SESSION',
            token: sessionData.token
        };
        this.ws.send(JSON.stringify(message));
    }

    /**
     * Handle session validation success
     */
    handleSessionValid(data) {
        console.log('Session valid, logging in...');
        this.sessionData = LoginScreen.getSavedSession();
        this.showLobbyScreen();
    }

    /**
     * Handle session validation failure
     */
    handleSessionInvalid() {
        console.log('Session invalid, clearing...');
        LoginScreen.clearSavedSession();
        this.showLoginScreen();
    }

    /**
     * Handle auth success (login or signup)
     */
    handleAuthSuccess(data) {
        console.log('Authentication successful');
        this.sessionData = {
            token: data.token,
            player_id: data.player_id,
            username: data.username
        };

        if (this.loginScreen) {
            this.loginScreen.handleAuthSuccess(data);
        }

        this.showLobbyScreen();
    }

    /**
     * Handle logout success
     */
    handleLogoutSuccess() {
        console.log('Logout successful');
        this.sessionData = null;
        this.showLoginScreen();
    }

    /**
     * Handle games list
     */
    handleGamesList(data) {
        if (this.lobbyScreen) {
            this.lobbyScreen.updateGamesList(data.my_games, data.available_games);
        }
    }

    /**
     * Handle game created
     */
    handleGameCreated(data) {
        console.log('Game created:', data.game);
        if (this.lobbyScreen) {
            this.lobbyScreen.handleGameCreated(data.game);
        }
    }

    /**
     * Handle game joined
     */
    handleGameJoined(data) {
        console.log('Game joined:', data.game);
        if (this.lobbyScreen) {
            this.lobbyScreen.handleGameJoined(data.game);
        }
    }

    /**
     * Handle game info
     */
    handleGameInfo(data) {
        if (this.lobbyScreen) {
            this.lobbyScreen.updateGameDetails(data.game, data.scoreboard);
        }
    }

    /**
     * Handle lobby chat message
     */
    handleLobbyChat(data) {
        if (this.lobbyScreen) {
            this.lobbyScreen.receiveChatMessage(data);
        }
    }

    /**
     * Handle error message
     */
    handleError(message) {
        console.error('Server error:', message);

        // Show error to appropriate screen
        if (this.loginScreen && this.currentScreen === 'login') {
            this.loginScreen.handleAuthError(message);
        } else {
            alert(`Error: ${message}`);
        }
    }

    /**
     * Handle disconnect
     */
    handleDisconnect() {
        if (this.currentScreen === 'game') {
            // In game - show reconnection UI
            alert('Disconnected from server. Please refresh to reconnect.');
        }
    }

    /**
     * Show connection error
     */
    showConnectionError() {
        this.appContainer.innerHTML = `
            <div class="error-screen">
                <h1>Connection Error</h1>
                <p>Unable to connect to game server.</p>
                <button onclick="window.location.reload()">Retry</button>
            </div>
        `;
    }

    /**
     * Show login screen
     */
    showLoginScreen() {
        this.destroyCurrentScreen();
        this.currentScreen = 'login';

        this.loginScreen = new LoginScreen((sessionData) => {
            // Auth successful callback
            this.sessionData = sessionData;
            this.showLobbyScreen();
        });

        this.loginScreen.render(this.appContainer);
    }

    /**
     * Show lobby screen
     */
    showLobbyScreen() {
        this.destroyCurrentScreen();
        this.currentScreen = 'lobby';

        this.lobbyScreen = new LobbyScreen(this.sessionData, (game) => {
            // Game selected callback
            this.currentGame = game;
            this.showGameScreen(game);
        });

        this.lobbyScreen.render(this.appContainer);
    }

    /**
     * Show game screen
     */
    showGameScreen(game) {
        this.destroyCurrentScreen();
        this.currentScreen = 'game';

        console.log('Entering game:', game);

        // Hide app container
        this.appContainer.style.display = 'none';

        // Show the game UI elements
        document.getElementById('game-container').style.display = 'flex';

        // Send ENTER_GAME message to server
        const message = {
            type: 'ENTER_GAME',
            token: this.sessionData.token,
            game_id: game.id
        };
        this.ws.send(JSON.stringify(message));

        // Pass the existing websocket to the game screen
        // so it doesn't create a new connection
        if (typeof webSocketClient !== 'undefined') {
            webSocketClient.socket = this.ws;
            webSocketClient.isConnecting = false;

            // Set up message handlers to route to game's message handler
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    webSocketClient._handleMessage(data);
                } catch (e) {
                    console.error('Failed to parse message:', e, event.data);
                }
            };
        }

        // Initialize the game screen (from main.js)
        // Don't let it reconnect - we're reusing the lobby websocket
        if (typeof initializeApp === 'function') {
            initializeApp(true); // Pass true to indicate we're already connected
        }
    }

    /**
     * Destroy current screen
     */
    destroyCurrentScreen() {
        if (this.loginScreen) {
            this.loginScreen.destroy();
            this.loginScreen = null;
        }

        if (this.lobbyScreen) {
            this.lobbyScreen.destroy();
            this.lobbyScreen = null;
        }

        // Hide game container if showing
        const gameContainer = document.getElementById('game-container');
        if (gameContainer) {
            gameContainer.style.display = 'none';
        }

        // Show app container for login/lobby
        if (this.appContainer) {
            this.appContainer.style.display = 'block';
        }
    }
}

// Global app instance
let starwebApp;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    starwebApp = new StarWebApp();
    starwebApp.initialize();
});
