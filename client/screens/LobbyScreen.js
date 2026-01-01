/**
 * LobbyScreen - Game lobby for listing and joining games
 */
class LobbyScreen {
    constructor(sessionData, onGameSelected) {
        this.sessionData = sessionData; // {token, player_id, username}
        this.onGameSelected = onGameSelected; // Callback when game is selected
        this.container = null;
        this.myGames = [];
        this.availableGames = [];
        this.selectedGame = null;
        this.CHARACTER_TYPES = [
            "Empire Builder",
            "Merchant",
            "Pirate",
            "Artifact Collector",
            "Berserker",
            "Apostle"
        ];
    }

    /**
     * Render the lobby screen
     */
    render(parentElement) {
        this.container = document.createElement('div');
        this.container.id = 'lobby-screen';
        this.container.className = 'screen';

        this.container.innerHTML = `
            <div class="lobby-container">
                <!-- Header -->
                <header class="lobby-header" role="banner">
                    <h1>⭐ STARWEB LOBBY ⭐</h1>
                    <div class="user-info">
                        <span>Player: <strong>${this.sessionData.username}</strong></span>
                        <button id="logout-btn" class="btn btn-small" aria-label="Logout from game">Logout</button>
                    </div>
                </header>

                <!-- Admin Message Banner -->
                <div id="lobby-admin-message" class="lobby-admin-message" role="alert" aria-live="assertive" style="display: none;">
                    <div id="lobby-admin-message-content"></div>
                </div>

                <!-- Main content -->
                <main class="lobby-content" role="main">
                    <!-- Left panel: Game lists -->
                    <aside class="lobby-left" role="complementary" aria-label="Game lists">
                        <section class="game-list-section" aria-labelledby="my-games-heading">
                            <div class="section-header">
                                <h3 id="my-games-heading">My Games</h3>
                                <button id="create-game-btn" class="btn btn-primary btn-small" aria-label="Create a new game">+ Create Game</button>
                            </div>
                            <div id="my-games-list" class="game-list" role="list" aria-live="polite" aria-busy="true">
                                ${this.renderLoadingSkeleton(3)}
                            </div>
                        </section>

                        <section class="game-list-section" aria-labelledby="available-games-heading">
                            <div class="section-header">
                                <h3 id="available-games-heading">Available Games</h3>
                                <button id="refresh-games-btn" class="btn btn-small" aria-label="Refresh games list">🔄 Refresh</button>
                            </div>
                            <div id="available-games-list" class="game-list" role="list" aria-live="polite" aria-busy="true">
                                ${this.renderLoadingSkeleton(3)}
                            </div>
                        </section>
                    </aside>

                    <!-- Middle panel: Game details -->
                    <section class="lobby-middle" role="region" aria-labelledby="game-details-heading">
                        <div id="game-details-panel" class="game-details-panel">
                            <div class="empty-message">Select a game to view details</div>
                        </div>
                    </section>

                    <!-- Right panel: Chat -->
                    <aside class="lobby-right" role="complementary" aria-labelledby="lobby-chat-heading">
                        <div class="lobby-chat-panel">
                            <div class="lobby-chat-header">
                                <h3 id="lobby-chat-heading">Lobby Chat</h3>
                            </div>
                            <div id="lobby-chat-messages" class="lobby-chat-messages" role="log" aria-live="polite" aria-label="Chat messages">
                                <div class="chat-welcome">Welcome to the StarWeb lobby! Chat with other players here.</div>
                            </div>
                            <div class="lobby-chat-input-container">
                                <input type="text" id="lobby-chat-input" class="lobby-chat-input" placeholder="Type a message... (Press / to focus)" maxlength="500" aria-label="Chat message input">
                                <button id="lobby-chat-send" class="btn btn-small" aria-label="Send chat message">Send</button>
                            </div>
                        </div>
                    </aside>
                </main>
            </div>

            <!-- Create Game Modal -->
            <div id="create-game-modal" class="modal" style="display: none;">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>Create New Game</h2>
                        <button class="modal-close" id="modal-close-btn">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="form-group">
                            <label for="game-name-input">Game Name</label>
                            <input type="text" id="game-name-input" class="form-input" placeholder="My Epic Game">
                        </div>
                        <div class="form-group">
                            <label for="character-type-select">Your Character Type</label>
                            <select id="character-type-select" class="form-input">
                                ${this.CHARACTER_TYPES.map(type => `<option value="${type}">${type}</option>`).join('')}
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="character-name-input">Your Character Name</label>
                            <input type="text" id="character-name-input" class="form-input" placeholder="${this.sessionData.username}">
                        </div>
                        <div class="form-group">
                            <label for="max-players-input">Max Players</label>
                            <input type="number" id="max-players-input" class="form-input" value="6" min="2" max="12">
                        </div>
                        <div class="form-group">
                            <label for="map-size-input">Map Size</label>
                            <select id="map-size-input" class="form-input">
                                <option value="50">Small (50 worlds)</option>
                                <option value="100">Medium (100 worlds)</option>
                                <option value="150">Large (150 worlds)</option>
                                <option value="200">Huge (200 worlds)</option>
                                <option value="255" selected>Classic (255 worlds)</option>
                            </select>
                        </div>
                        <div class="form-error" id="create-game-error"></div>
                    </div>
                    <div class="modal-footer">
                        <button id="cancel-create-btn" class="btn">Cancel</button>
                        <button id="confirm-create-btn" class="btn btn-primary">Create Game</button>
                    </div>
                </div>
            </div>
        `;

        parentElement.appendChild(this.container);
        this.attachEventListeners();
        this.requestGamesList();
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Logout
        document.getElementById('logout-btn').addEventListener('click', () => this.handleLogout());

        // Create game
        document.getElementById('create-game-btn').addEventListener('click', () => this.showCreateGameModal());

        // Refresh games
        document.getElementById('refresh-games-btn').addEventListener('click', () => this.requestGamesList());

        // Modal controls
        document.getElementById('modal-close-btn').addEventListener('click', () => this.hideCreateGameModal());
        document.getElementById('cancel-create-btn').addEventListener('click', () => this.hideCreateGameModal());
        document.getElementById('confirm-create-btn').addEventListener('click', () => this.handleCreateGame());

        // Close modal on outside click
        document.getElementById('create-game-modal').addEventListener('click', (e) => {
            if (e.target.id === 'create-game-modal') {
                this.hideCreateGameModal();
            }
        });

        // Lobby chat
        const chatInput = document.getElementById('lobby-chat-input');
        const chatSendBtn = document.getElementById('lobby-chat-send');

        chatSendBtn.addEventListener('click', () => this.sendChatMessage());
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendChatMessage();
            }
        });
    }

    /**
     * Request games list from server
     */
    requestGamesList() {
        const message = {
            type: 'LIST_GAMES',
            token: this.sessionData.token
        };
        window.ws.send(JSON.stringify(message));
    }

    /**
     * Update games list display
     */
    updateGamesList(myGames, availableGames) {
        this.myGames = myGames;
        this.availableGames = availableGames;

        // Update my games
        const myGamesList = document.getElementById('my-games-list');
        myGamesList.setAttribute('aria-busy', 'false');

        if (myGames.length === 0) {
            myGamesList.innerHTML = '<div class="empty-message">No games yet. Create one!</div>';
        } else {
            myGamesList.innerHTML = myGames.map(game => this.renderGameCard(game, true)).join('');

            // Attach click handlers
            myGames.forEach(game => {
                document.getElementById(`game-${game.id}`).addEventListener('click', () => {
                    this.selectGame(game);
                });
                document.getElementById(`enter-game-${game.id}`).addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.enterGame(game);
                });
            });
        }

        // Update available games
        const availableGamesList = document.getElementById('available-games-list');
        availableGamesList.setAttribute('aria-busy', 'false');

        if (availableGames.length === 0) {
            availableGamesList.innerHTML = '<div class="empty-message">No available games</div>';
        } else {
            availableGamesList.innerHTML = availableGames.map(game => this.renderGameCard(game, false)).join('');

            // Attach click handlers
            availableGames.forEach(game => {
                document.getElementById(`game-${game.id}`).addEventListener('click', () => {
                    this.selectGame(game);
                });
                document.getElementById(`join-game-${game.id}`).addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.showJoinGamePrompt(game);
                });
            });
        }

        // Update keyboard navigation
        if (window.keyboardNav) {
            window.keyboardNav.updateListNavigation();
        }
    }

    /**
     * Render a game card
     */
    renderGameCard(game, isMyGame) {
        const statusClass = game.status === 'active' ? 'status-active' : 'status-waiting';
        const actionBtn = isMyGame
            ? `<button id="enter-game-${game.id}" class="btn btn-small btn-primary">Enter →</button>`
            : `<button id="join-game-${game.id}" class="btn btn-small">Join →</button>`;

        return `
            <div class="game-card" id="game-${game.id}" role="listitem">
                <div class="game-card-header">
                    <h4>${game.name}</h4>
                    <span class="game-status ${statusClass}">${game.status}</span>
                </div>
                <div class="game-card-body">
                    <div class="game-info">
                        <span>Turn: ${game.current_turn}</span>
                        <span>Players: ${game.player_count}/${game.max_players}</span>
                    </div>
                    ${actionBtn}
                </div>
            </div>
        `;
    }

    /**
     * Render loading skeleton for game cards
     */
    renderLoadingSkeleton(count = 3) {
        return Array.from({ length: count }, (_, i) => `
            <div class="skeleton-card" role="status" aria-label="Loading game ${i + 1}">
                <div class="skeleton skeleton-title"></div>
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text"></div>
            </div>
        `).join('');
    }

    /**
     * Select a game to view details
     */
    selectGame(game) {
        this.selectedGame = game;
        this.requestGameInfo(game.id);
    }

    /**
     * Request detailed game info
     */
    requestGameInfo(gameId) {
        const message = {
            type: 'GET_GAME_INFO',
            token: this.sessionData.token,
            game_id: gameId
        };
        window.ws.send(JSON.stringify(message));
    }

    /**
     * Update game details panel
     */
    updateGameDetails(gameInfo, scoreboard) {
        const panel = document.getElementById('game-details-panel');

        const createdDate = new Date(gameInfo.created_at);
        const timeAgo = this.getTimeAgo(createdDate);

        panel.innerHTML = `
            <h3>${gameInfo.name}</h3>
            <div class="game-detail-section">
                <div class="detail-row"><span>Status:</span><span>${gameInfo.status}</span></div>
                <div class="detail-row"><span>Turn:</span><span>${gameInfo.current_turn}</span></div>
                <div class="detail-row"><span>Players:</span><span>${gameInfo.player_count}/${gameInfo.max_players}</span></div>
                <div class="detail-row"><span>Created:</span><span>${timeAgo}</span></div>
            </div>

            ${scoreboard.length > 0 ? `
                <div class="game-detail-section">
                    <h4>Scoreboard</h4>
                    <table class="scoreboard-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Player</th>
                                <th>Character</th>
                                <th>Score</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${scoreboard.map((entry, index) => `
                                <tr>
                                    <td>${index + 1}</td>
                                    <td>${entry.character_name}</td>
                                    <td>${entry.character_type}</td>
                                    <td>${entry.score}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            ` : ''}
        `;
    }

    /**
     * Get human-readable time ago
     */
    getTimeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        const intervals = [
            { label: 'year', seconds: 31536000 },
            { label: 'month', seconds: 2592000 },
            { label: 'day', seconds: 86400 },
            { label: 'hour', seconds: 3600 },
            { label: 'minute', seconds: 60 }
        ];

        for (const interval of intervals) {
            const count = Math.floor(seconds / interval.seconds);
            if (count >= 1) {
                return `${count} ${interval.label}${count !== 1 ? 's' : ''} ago`;
            }
        }
        return 'just now';
    }

    /**
     * Show create game modal
     */
    showCreateGameModal() {
        document.getElementById('create-game-modal').style.display = 'flex';
        document.getElementById('game-name-input').focus();
        document.getElementById('create-game-error').textContent = '';
    }

    /**
     * Hide create game modal
     */
    hideCreateGameModal() {
        document.getElementById('create-game-modal').style.display = 'none';
    }

    /**
     * Handle create game
     */
    handleCreateGame() {
        const gameName = document.getElementById('game-name-input').value.trim();
        const characterType = document.getElementById('character-type-select').value;
        const characterName = document.getElementById('character-name-input').value.trim() || this.sessionData.username;
        const maxPlayers = parseInt(document.getElementById('max-players-input').value);
        const mapSize = parseInt(document.getElementById('map-size-input').value);

        if (!gameName) {
            document.getElementById('create-game-error').textContent = 'Please enter a game name';
            return;
        }

        // Send CREATE_GAME message
        const message = {
            type: 'CREATE_GAME',
            token: this.sessionData.token,
            name: gameName,
            character_type: characterType,
            character_name: characterName,
            max_players: maxPlayers,
            map_size: mapSize
        };

        window.ws.send(JSON.stringify(message));
        this.hideCreateGameModal();
    }

    /**
     * Show join game prompt
     */
    showJoinGamePrompt(game) {
        if (!window.modalManager) {
            console.error('ModalManager not available');
            return;
        }

        window.modalManager.show({
            title: `Join ${game.name}`,
            size: 'medium',
            content: (container) => {
                container.innerHTML = `
                    <div class="form-group">
                        <label for="join-character-type">Character Type</label>
                        <select id="join-character-type" class="form-input">
                            ${this.CHARACTER_TYPES.map(type => `<option value="${type}">${type}</option>`).join('')}
                        </select>
                        <div class="character-type-description" style="margin-top: 8px; font-size: 0.9em; color: rgba(255,255,255,0.7);">
                            Choose your playstyle for this game
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="join-character-name">Character Name</label>
                        <input type="text" id="join-character-name" class="form-input" value="${this.sessionData.username}" placeholder="Enter character name">
                    </div>
                `;
            },
            buttons: [
                {
                    text: 'Cancel',
                    className: 'btn-ghost'
                },
                {
                    text: 'Join Game',
                    className: 'btn-primary',
                    onClick: () => {
                        const characterType = document.getElementById('join-character-type').value;
                        const characterName = document.getElementById('join-character-name').value.trim() || this.sessionData.username;
                        this.joinGame(game.id, characterType, characterName);
                    }
                }
            ]
        });
    }

    /**
     * Join a game
     */
    joinGame(gameId, characterType, characterName) {
        const message = {
            type: 'JOIN_GAME',
            token: this.sessionData.token,
            game_id: gameId,
            character_type: characterType,
            character_name: characterName
        };

        window.ws.send(JSON.stringify(message));
    }

    /**
     * Enter a game (transition to game screen)
     */
    enterGame(game) {
        if (this.onGameSelected) {
            this.onGameSelected(game);
        }
    }

    /**
     * Handle logout
     */
    async handleLogout() {
        if (!window.modalManager) {
            console.error('ModalManager not available');
            return;
        }

        const confirmed = await window.modalManager.confirm(
            'Logout',
            'Are you sure you want to logout?',
            'Logout',
            'Cancel'
        );

        if (confirmed) {
            const message = {
                type: 'LOGOUT',
                token: this.sessionData.token
            };
            window.ws.send(JSON.stringify(message));

            // Clear session
            LoginScreen.clearSavedSession();

            // Reload page to go back to login
            window.location.reload();
        }
    }

    /**
     * Handle game created
     */
    handleGameCreated(game) {
        if (window.toastManager) {
            window.toastManager.success(`Game "${game.name}" created successfully!`);
        }
        this.requestGamesList();
        // Auto-enter the created game
        this.enterGame(game);
    }

    /**
     * Handle game joined
     */
    handleGameJoined(game) {
        if (window.toastManager) {
            window.toastManager.success(`Joined "${game.name}" successfully!`);
        }
        this.requestGamesList();
        // Auto-enter the joined game
        this.enterGame(game);
    }

    /**
     * Send lobby chat message
     */
    sendChatMessage() {
        const input = document.getElementById('lobby-chat-input');
        const text = input.value.trim();

        if (!text) return;

        const message = {
            type: 'LOBBY_CHAT',
            token: this.sessionData.token,
            text: text
        };

        window.ws.send(JSON.stringify(message));
        input.value = '';
        input.focus();
    }

    /**
     * Receive and display lobby chat message
     */
    receiveChatMessage(data) {
        const messagesContainer = document.getElementById('lobby-chat-messages');
        if (!messagesContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message';

        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const username = data.username || 'Unknown';
        const text = data.text || '';

        // Highlight own messages
        if (username === this.sessionData.username) {
            messageDiv.classList.add('chat-message-own');
        }

        messageDiv.innerHTML = `
            <span class="chat-timestamp">[${timestamp}]</span>
            <span class="chat-username">${username}:</span>
            <span class="chat-text">${this.escapeHTML(text)}</span>
        `;

        messagesContainer.appendChild(messageDiv);

        // Auto-scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Limit to last 100 messages
        while (messagesContainer.children.length > 100) {
            messagesContainer.removeChild(messagesContainer.firstChild);
        }
    }

    /**
     * Show admin message in lobby
     */
    showAdminMessage(message) {
        const panel = document.getElementById('lobby-admin-message');
        const content = document.getElementById('lobby-admin-message-content');

        if (panel && content && message) {
            content.innerHTML = this.escapeHTML(message);
            panel.style.display = 'block';
        }
    }

    /**
     * Handle error messages
     */
    handleError(errorMessage, details = '') {
        if (window.toastManager) {
            const message = details ? `${errorMessage}: ${details}` : errorMessage;
            window.toastManager.error(message, 5000);
        } else {
            console.error(errorMessage, details);
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHTML(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Remove the screen from DOM
     */
    destroy() {
        if (this.container && this.container.parentElement) {
            this.container.parentElement.removeChild(this.container);
        }
        this.container = null;
    }
}
