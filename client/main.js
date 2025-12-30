/**
 * StarWeb Client - Main Entry Point
 *
 * Modular frontend with:
 * - Clean state management
 * - Network layer abstraction
 * - Rendering system (to be implemented)
 * - UI components (to be implemented)
 */

// Import core systems (loaded via script tags in HTML)
// - client/state/GameState.js
// - client/network/WebSocketClient.js
// - client/network/MessageHandler.js

// Global instances (gameState and webSocketClient are exported as singletons from their modules)
let messageHandler;
let selectedWorldId = null;
let selectedFleetId = null;

// Rendering system
let renderer;
let camera;
let worldLayout;

// UI Panels
let scoreboard;
let worldList;
let fleetList;
let queuedOrders;
let worldInfo;
let fleetInfo;
let actionList;
let commandInputManager; // Enhanced command input with parser

// Initialize application
function initializeApp() {
    console.log('Initializing StarWeb client...');

    // Setup message handler to connect network and state
    messageHandler = new MessageHandler(webSocketClient, gameState);

    // Initialize UI panels
    initializeUIPanels();

    // Connect to server
    webSocketClient.connect();

    // Setup UI event listeners
    setupUIListeners();

    // Setup state change listeners
    setupStateListeners();

    // Setup canvas
    setupCanvas();

    console.log('StarWeb client initialized');
}

function initializeUIPanels() {
    scoreboard = new Scoreboard('scoreboard');
    worldList = new WorldList('world-list');
    fleetList = new FleetList('fleet-list');
    queuedOrders = new QueuedOrders('queued-orders');
    worldInfo = new WorldInfo('selection-info');
    fleetInfo = new FleetInfo('selection-info');
    actionList = new ActionList('action-list');
    commandInputManager = new CommandInput(
        document.getElementById('command-input'),
        document.getElementById('command-hint'),
        gameState
    );

    // Set up callbacks
    worldList.setOnWorldClick((worldId) => {
        selectedWorldId = worldId;
        selectedFleetId = null;

        const worldLayer = renderer?.getLayer('worlds');
        const connectionLayer = renderer?.getLayer('connections');
        if (worldLayer) {
            worldLayer.setSelectedWorld(worldId);
        }
        if (connectionLayer) {
            connectionLayer.setSelectedWorld(worldId);
        }

        updateSelectionInfoSidebar();
        updateActionList();
        renderGame();

        // Focus camera on world
        if (camera && worldLayout) {
            const pos = worldLayout.getPosition(worldId);
            if (pos) {
                camera.focusOn(pos.x, pos.y);
                renderGame();
            }
        }

        // Insert world ID into command if there's a partial command
        insertWorldIdIntoCommand(worldId);
    });

    fleetList.setOnFleetClick((fleetId) => {
        selectedFleetId = fleetId;
        selectedWorldId = null;

        // Focus camera on the fleet's world with zoom to show connections
        const state = gameState.getState();
        const fleet = state.fleets?.[fleetId];

        if (fleet && fleet.world !== undefined) {
            const worldId = fleet.world;

            // Highlight the world where the fleet is located
            const worldLayer = renderer?.getLayer('worlds');
            const connectionLayer = renderer?.getLayer('connections');
            if (worldLayer) {
                worldLayer.setSelectedWorld(worldId);
            }
            if (connectionLayer) {
                connectionLayer.setSelectedWorld(worldId);
            }

            // Focus and zoom camera
            if (camera && worldLayout) {
                const worldPos = worldLayout.getPosition(worldId);

                if (worldPos) {
                    // Get connected worlds to calculate appropriate zoom level
                    const world = state.worlds?.[worldId];
                    const connections = world?.connections || [];

                    // Calculate distances to connected worlds
                    let maxDistance = 0;
                    if (connections.length > 0) {
                        for (const connectedWorldId of connections) {
                            const connectedPos = worldLayout.getPosition(connectedWorldId);
                            if (connectedPos) {
                                const dx = connectedPos.x - worldPos.x;
                                const dy = connectedPos.y - worldPos.y;
                                const distance = Math.sqrt(dx * dx + dy * dy);
                                maxDistance = Math.max(maxDistance, distance);
                            }
                        }
                    }

                    // Calculate zoom level to show connected worlds
                    // We want connected worlds to be visible, so zoom out based on max distance
                    // Assume we want the farthest connection to be within 40% of screen
                    const canvas = document.getElementById('game-canvas');
                    if (canvas && maxDistance > 0) {
                        const screenSize = Math.min(canvas.width, canvas.height);
                        const desiredViewportSize = maxDistance * 2.5; // 2.5x to show all connections comfortably
                        const zoom = screenSize / desiredViewportSize;
                        camera.focusOn(worldPos.x, worldPos.y, Math.max(0.3, Math.min(1.0, zoom)));
                    } else {
                        // No connections or couldn't calculate, use default zoom
                        camera.focusOn(worldPos.x, worldPos.y, 0.6);
                    }
                }
            }
        } else {
            // Fleet not found or no world, clear selection
            const worldLayer = renderer?.getLayer('worlds');
            const connectionLayer = renderer?.getLayer('connections');
            if (worldLayer) {
                worldLayer.setSelectedWorld(null);
            }
            if (connectionLayer) {
                connectionLayer.setSelectedWorld(null);
            }
        }

        updateSelectionInfoSidebar();
        updateActionList();
        renderGame();

        // Insert fleet ID into command if there's a partial command
        insertFleetIdIntoCommand(fleetId);
    });

    queuedOrders.setOnCancelOrder((orderIndex) => {
        // Send cancel command to server
        webSocketClient.sendCommand(`CANCEL ${orderIndex}`);
    });

    actionList.setOnActionClick((actionId) => {
        handleActionClick(actionId);
    });
}

function setupUIListeners() {
    // Send button
    const sendBtn = document.getElementById('send-btn');
    const commandInput = document.getElementById('command-input');

    sendBtn?.addEventListener('click', () => {
        const command = commandInput.value.trim();
        if (command) {
            // Special commands always pass through
            const cmd = command.split(' ')[0].toUpperCase();
            if (cmd === 'HELP' || cmd === '?' || cmd === 'TURN' || cmd === 'JOIN' || cmd === 'CANCEL') {
                webSocketClient.sendCommand(command);
                commandInput.value = '';
                commandInputManager.onInput('');
                return;
            }

            // Parse and validate before sending
            const result = commandInputManager.parser.parseFinal(command);

            if (result.validation && result.validation.isValid) {
                webSocketClient.sendCommand(command);
                commandInput.value = '';
                commandInputManager.onInput('');
            } else if (result.ast === null) {
                // Couldn't parse at all - send to server anyway (might be valid server command)
                // Server will validate properly
                webSocketClient.sendCommand(command);
                commandInput.value = '';
                commandInputManager.onInput('');
            } else {
                // Parsed but invalid - show errors but still allow sending
                console.warn('Invalid command:', result.validation?.errors);
            }
        }
    });

    // Help button
    const helpBtn = document.getElementById('help-btn');
    helpBtn?.addEventListener('click', () => {
        webSocketClient.sendCommand('HELP');
    });

    // Manual download button - shows modal with document choices
    const manualBtn = document.getElementById('manual-btn');
    const downloadModal = document.getElementById('download-modal');
    const downloadCancelBtn = document.getElementById('download-cancel-btn');

    manualBtn?.addEventListener('click', () => {
        // Show download modal
        downloadModal.style.display = 'flex';
    });

    // Download option buttons
    const downloadOptionBtns = document.querySelectorAll('.download-option-btn');
    downloadOptionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const url = btn.getAttribute('data-url');
            window.open(url, '_blank');
            downloadModal.style.display = 'none';
        });
    });

    downloadCancelBtn?.addEventListener('click', () => {
        downloadModal.style.display = 'none';
    });

    // Close download modal when clicking outside
    downloadModal?.addEventListener('click', (e) => {
        if (e.target === downloadModal) {
            downloadModal.style.display = 'none';
        }
    });

    // Bug report button
    const bugReportBtn = document.getElementById('bug-report-btn');
    const bugReportModal = document.getElementById('bug-report-modal');
    const bugDescription = document.getElementById('bug-description');
    const bugSubmitBtn = document.getElementById('bug-submit-btn');
    const bugCancelBtn = document.getElementById('bug-cancel-btn');

    bugReportBtn?.addEventListener('click', () => {
        // Show modal
        bugReportModal.style.display = 'flex';
        bugDescription.value = '';
        bugDescription.focus();
    });

    bugCancelBtn?.addEventListener('click', () => {
        // Hide modal
        bugReportModal.style.display = 'none';
    });

    bugSubmitBtn?.addEventListener('click', () => {
        const description = bugDescription.value.trim();
        if (description) {
            // Send bug report to server
            webSocketClient.send({
                type: 'bug_report',
                description: description,
                timestamp: new Date().toISOString(),
                game_turn: gameState.gameTurn || 0,
                player_name: gameState.playerName || 'Unknown'
            });

            // Hide modal and show confirmation
            bugReportModal.style.display = 'none';
            addEventLog('Bug report submitted. Thank you for helping improve StarWeb!', 'info');
        }
    });

    // Close modal when clicking outside
    bugReportModal?.addEventListener('click', (e) => {
        if (e.target === bugReportModal) {
            bugReportModal.style.display = 'none';
        }
    });

    commandInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendBtn?.click();
        }
    });

    // Join button
    const joinBtn = document.getElementById('join-btn');
    const playerNameInput = document.getElementById('player-name-input');
    const characterTypeSelect = document.getElementById('character-type-select');
    const scoreVoteInput = document.getElementById('score-vote-input');

    joinBtn?.addEventListener('click', () => {
        const name = playerNameInput.value.trim();
        const charType = characterTypeSelect.value;
        const scoreVote = scoreVoteInput.value;

        if (name) {
            webSocketClient.sendCommand(`JOIN ${name} ${scoreVote} ${charType}`);
        }
    });

    playerNameInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            joinBtn?.click();
        }
    });

    // End turn button
    const endTurnBtn = document.getElementById('end-turn-btn');
    if (!endTurnBtn) {
        const controlsDiv = document.getElementById('controls');
        const btn = document.createElement('button');
        btn.id = 'end-turn-btn';
        btn.textContent = 'End Turn';
        btn.style.backgroundColor = '#e91e63';
        btn.style.marginLeft = '10px';
        btn.onclick = () => webSocketClient.sendCommand('TURN');
        controlsDiv?.appendChild(btn);
    } else {
        endTurnBtn.onclick = () => webSocketClient.sendCommand('TURN');
    }

    // Command hints are now handled by CommandInput internally
    // (input event listeners are set up in CommandInput constructor)

    // Window resize
    window.addEventListener('resize', () => {
        resizeCanvas();
        renderGame();
    });
}

function setupStateListeners() {
    // Listen for full updates
    gameState.on('full-update', ({ state, isFirstUpdate }) => {
        console.log('Full update received:', state);

        // Show game UI if player has joined
        if (state.player_name) {
            const loginOverlay = document.getElementById('login-overlay');
            const gameContainer = document.getElementById('game-container');

            if (loginOverlay && loginOverlay.style.display !== 'none') {
                loginOverlay.style.display = 'none';
                gameContainer.style.display = 'flex';
                resizeCanvas();
            }

            // Update layers with player name
            if (renderer) {
                const worldLayer = renderer.getLayer('worlds');
                const fleetLayer = renderer.getLayer('fleets');
                const orderLayer = renderer.getLayer('order-indicators');
                if (worldLayer) worldLayer.setMyPlayerName(state.player_name);
                if (fleetLayer) fleetLayer.setMyPlayerName(state.player_name);
                if (orderLayer) orderLayer.setMyPlayerName(state.player_name);
            }

            // Focus camera on homeworld on first update
            if (isFirstUpdate) {
                focusCameraOnHomeworld();
            }
        }

        // Update UI
        updateAllUI();
    });

    // Listen for delta updates
    gameState.on('delta-update', ({ delta }) => {
        console.log('Delta update received:', delta);
        updateAllUI();
    });

    // Listen for timer ticks
    gameState.on('timer-tick', (data) => {
        updateTimerDisplay();
    });
}

function updateAllUI() {
    const state = gameState.getState();
    if (!state) return;

    calculateLayout();
    renderGame();
    updateSidebars();
    updateTimerDisplay();
    updateQueuedOrders();
    updateScoreboard();
    updateActionList();
    updateSelectionInfoSidebar();
}

// Rendering setup
function setupCanvas() {
    const canvas = document.getElementById('game-canvas');
    if (!canvas) {
        console.error('Canvas not found');
        return;
    }

    // Initialize rendering system
    worldLayout = new WorldLayout();
    camera = new Camera();
    renderer = new Renderer(canvas);

    renderer.setCamera(camera);
    renderer.setWorldLayout(worldLayout);

    // Add layers in order (back to front)
    renderer.addLayer(new BackgroundLayer());
    renderer.addLayer(new ConnectionLayer());
    renderer.addLayer(new WorldLayer());
    renderer.addLayer(new FleetLayer());
    renderer.addLayer(new OrderIndicatorsLayer());

    // Setup canvas interaction
    setupCanvasInteraction(canvas);
}

function resizeCanvas() {
    if (renderer) {
        renderer.resize();
    }
}

function calculateLayout() {
    const state = gameState.getState();
    if (!state || !state.worlds || !worldLayout) return;

    worldLayout.calculateLayout(state.worlds);
}

function renderGame() {
    const state = gameState.getState();
    if (!renderer || !state) return;

    renderer.render(state);
}

function updateSidebars() {
    const state = gameState.getState();
    if (!state) return;

    if (worldList) worldList.update(state);
    if (fleetList) fleetList.update(state);
}

function updateTimerDisplay() {
    const state = gameState.getState();
    if (!state) return;

    const minutes = Math.floor(state.time_remaining / 60);
    const seconds = state.time_remaining % 60;
    const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;

    const timerDisplay = document.getElementById('timer-display');
    if (timerDisplay) {
        timerDisplay.textContent = `Turn ${state.game_turn} | ${timeStr} | ${state.players_ready}/${state.total_players} ready`;
    }

    updateEndTurnButton();
}

function updateEndTurnButton() {
    const state = gameState.getState();
    const endTurnBtn = document.getElementById('end-turn-btn');
    if (!endTurnBtn || !state || !state.players) return;

    const players = Object.values(state.players);
    const notReady = players.filter(p => !p.ready);

    if (notReady.length === 0) {
        endTurnBtn.textContent = 'End Turn';
        endTurnBtn.title = 'All players ready!';
    } else {
        const notReadyNames = notReady.map(p => p.name).join(', ');
        endTurnBtn.textContent = `End Turn (${notReady.length} waiting)`;
        endTurnBtn.title = `Waiting for: ${notReadyNames}`;
    }
}

function updateQueuedOrders() {
    const state = gameState.getState();
    if (!state || !queuedOrders) return;

    queuedOrders.update(state);
}

function updateScoreboard() {
    const state = gameState.getState();
    if (!state || !scoreboard) return;

    scoreboard.update(state);
}

function updateActionList() {
    const state = gameState.getState();
    if (!actionList) return;

    actionList.update(state, selectedWorldId, selectedFleetId);
}

function updateSelectionInfoSidebar() {
    const state = gameState.getState();
    const titleElement = document.getElementById('selection-info-title');

    if (selectedFleetId) {
        // Show fleet info
        if (fleetInfo) {
            fleetInfo.update(state, selectedFleetId);
        }
        if (titleElement) {
            titleElement.textContent = 'Fleet Info';
        }
    } else if (selectedWorldId) {
        // Show world info
        if (worldInfo) {
            worldInfo.update(state, selectedWorldId);
        }
        if (titleElement) {
            titleElement.textContent = 'World Info';
        }
    } else {
        // Clear both
        if (worldInfo) {
            worldInfo.clear();
        }
        if (titleElement) {
            titleElement.textContent = 'Selection Info';
        }
    }
}

function focusCameraOnHomeworld() {
    const state = gameState.getState();
    if (!state || !camera || !worldLayout) return;

    // Find player's homeworld
    const homeworld = state.worlds && Object.values(state.worlds).find(
        w => w.owner === state.player_name && w.key
    );

    if (homeworld) {
        const pos = worldLayout.getPosition(homeworld.id);
        if (pos) {
            camera.focusOn(pos.x, pos.y);
        }
    }
}

function handleActionClick(actionId) {
    const commandInput = document.getElementById('command-input');
    if (!commandInput) return;

    const state = gameState.getState();

    switch (actionId) {
        case 'build-ships':
            if (selectedWorldId) {
                // Format: W<worldId>B<amount>F<fleetId> or W<worldId>B<amount>I or W<worldId>B<amount>P
                // For ships, we need to specify a fleet to build into or build I/P ships
                commandInput.value = `W${selectedWorldId}B10I`;
                commandInput.focus();
                // Select the amount so user can type over it
                commandInput.setSelectionRange(selectedWorldId.toString().length + 2, selectedWorldId.toString().length + 4);
            }
            break;

        case 'build-industry':
            if (selectedWorldId) {
                // This option is confusing - in StarWeb, you can't "build industry"
                // You build ships (I or P ships). Let's make this build IShips instead
                commandInput.value = `W${selectedWorldId}B10I`;
                commandInput.focus();
                commandInput.setSelectionRange(selectedWorldId.toString().length + 2, selectedWorldId.toString().length + 4);
            }
            break;

        case 'build-defenses':
            if (selectedWorldId) {
                // Build PShips (defensive ships)
                commandInput.value = `W${selectedWorldId}B10P`;
                commandInput.focus();
                commandInput.setSelectionRange(selectedWorldId.toString().length + 2, selectedWorldId.toString().length + 4);
            }
            break;

        case 'transfer':
            if (selectedWorldId) {
                // Transfer requires a fleet ID, need to find a fleet at this world
                const fleetsHere = Object.values(state.fleets || {})
                    .filter(f => f.world === selectedWorldId && f.owner === state.player_name);

                if (fleetsHere.length > 0) {
                    // Format: F<fleetId>T<amount><target>
                    const fleetId = fleetsHere[0].id;
                    commandInput.value = `F${fleetId}T10I`;
                    commandInput.focus();
                    commandInput.setSelectionRange(fleetId.toString().length + 2, fleetId.toString().length + 4);
                }
            }
            break;

        case 'ambush':
            if (selectedWorldId) {
                // Ambush requires a fleet ID, need to find a fleet at this world
                const fleetsHere = Object.values(state.fleets || {})
                    .filter(f => f.world === selectedWorldId && f.owner === state.player_name);

                if (fleetsHere.length > 0) {
                    // Format: F<fleetId>A
                    const fleetId = fleetsHere[0].id;
                    commandInput.value = `F${fleetId}A`;
                    commandInput.focus();
                }
            }
            break;

        case 'move-fleet':
            if (selectedFleetId) {
                // Format: F<fleetId>W<worldId>
                commandInput.value = `F${selectedFleetId}W`;
                commandInput.focus();
            }
            break;

        case 'fire-world':
            if (selectedFleetId) {
                // Format: F<fleetId>A<target> where target is P or I for population/industry
                commandInput.value = `F${selectedFleetId}AP`;
                commandInput.focus();
            } else if (selectedWorldId) {
                // Need a fleet to fire from
                const fleetsHere = Object.values(state.fleets || {})
                    .filter(f => f.world === selectedWorldId && f.owner === state.player_name);

                if (fleetsHere.length > 0) {
                    const fleetId = fleetsHere[0].id;
                    commandInput.value = `F${fleetId}AP`;
                    commandInput.focus();
                }
            }
            break;

        case 'fire-fleet':
            if (selectedFleetId) {
                // Format: F<fleetId>AF<targetFleetId>
                const fleet = state.fleets?.[selectedFleetId];
                if (fleet && fleet.world !== undefined) {
                    // Find hostile fleets at the same world
                    const hostileFleets = Object.values(state.fleets || {})
                        .filter(f => f.world === fleet.world && f.owner !== state.player_name);

                    if (hostileFleets.length > 0) {
                        commandInput.value = `F${selectedFleetId}AF${hostileFleets[0].id}`;
                        commandInput.focus();
                    } else {
                        commandInput.value = `F${selectedFleetId}AF`;
                        commandInput.focus();
                    }
                }
            }
            break;

        default:
            console.log('Unknown action:', actionId);
    }

    // Command hint updates are now automatic via CommandInput
    // No manual update needed
}

function insertWorldIdIntoCommand(worldId) {
    const commandInput = document.getElementById('command-input');
    if (!commandInput) return;

    const currentValue = commandInput.value.trim();

    // If empty, start with world command
    if (!currentValue) {
        commandInput.value = `W${worldId}`;
        commandInput.focus();
        commandInputManager.onInput(commandInput.value);
        return;
    }

    // Check if this ends with just 'W' (from speed action, waiting for world ID)
    const trailingWPattern = /^(.+)W$/i;
    const trailingWMatch = currentValue.match(trailingWPattern);
    if (trailingWMatch) {
        // Replace trailing W with W + world ID
        commandInput.value = `${trailingWMatch[1]}W${worldId}`;
        commandInput.focus();
        commandInputManager.onInput(commandInput.value);
        return;
    }

    // Check if this looks like a fleet move command (F123 or F123W456)
    const fleetMovePattern = /^F(\d+)(W\d+)*$/i;
    if (fleetMovePattern.test(currentValue)) {
        // Add world to move path
        commandInput.value = `${currentValue}W${worldId}`;
        commandInput.focus();
        commandInputManager.onInput(commandInput.value);
        return;
    }

    // Check if this is a world build command without target
    const worldBuildPattern = /^W(\d+)B(\d+)$/i;
    if (worldBuildPattern.test(currentValue)) {
        // Don't add anything - waiting for build target (I/P/F)
        return;
    }

    // Check if this is a migration command without destination
    const migrationPattern = /^W(\d+)M(\d+)$/i;
    if (migrationPattern.test(currentValue)) {
        // Complete migration with destination world
        commandInput.value = `${currentValue}W${worldId}`;
        commandInput.focus();
        commandInputManager.onInput(commandInput.value);
        return;
    }

    // Check if this is an artifact transfer from world waiting for fleet target
    const artifactWorldPattern = /^W(\d+)TA(\d+)$/i;
    if (artifactWorldPattern.test(currentValue)) {
        // Don't add world - waiting for F (fleet target)
        return;
    }

    // Otherwise, just append the world ID
    commandInput.value = `${currentValue}W${worldId}`;
    commandInput.focus();
    commandInputManager.onInput(commandInput.value);
}

function insertFleetIdIntoCommand(fleetId) {
    const commandInput = document.getElementById('command-input');
    if (!commandInput) return;

    const currentValue = commandInput.value.trim();

    // If empty, start with fleet command
    if (!currentValue) {
        commandInput.value = `F${fleetId}`;
        commandInput.focus();
        commandInputManager.onInput(commandInput.value);
        return;
    }

    // Check if this is a transfer waiting for target fleet: F123T10
    const transferPattern = /^F(\d+)T(\d+)$/i;
    if (transferPattern.test(currentValue)) {
        commandInput.value = `${currentValue}F${fleetId}`;
        commandInput.focus();
        commandInputManager.onInput(commandInput.value);
        return;
    }

    // Check if this is a fire command waiting for target fleet: F123AF
    const fireFleetPattern = /^F(\d+)AF$/i;
    if (fireFleetPattern.test(currentValue)) {
        commandInput.value = `${currentValue}${fleetId}`;
        commandInput.focus();
        commandInputManager.onInput(commandInput.value);
        return;
    }

    // Check if this is a build command waiting for target fleet: W123B10
    const buildFleetPattern = /^W(\d+)B(\d+)$/i;
    if (buildFleetPattern.test(currentValue)) {
        commandInput.value = `${currentValue}F${fleetId}`;
        commandInput.focus();
        commandInputManager.onInput(commandInput.value);
        return;
    }

    // Check if this is an artifact transfer waiting for fleet target: F123TA456 or W123TA456
    const artifactFleetPattern = /^[FW](\d+)TA(\d+)$/i;
    if (artifactFleetPattern.test(currentValue)) {
        commandInput.value = `${currentValue}F${fleetId}`;
        commandInput.focus();
        commandInputManager.onInput(commandInput.value);
        return;
    }

    // Otherwise, start a new fleet command
    commandInput.value = `F${fleetId}`;
    commandInput.focus();
    commandInputManager.onInput(commandInput.value);
}

// Status panel update functions for hover tooltips
function updateStatusPanelForWorld(worldId) {
    const statusPanel = document.getElementById('status-panel');
    if (!statusPanel || !gameState) return;

    const state = gameState.getState();
    if (!state || !state.worlds) return;

    const world = state.worlds[worldId];
    if (!world) return;

    // Home worlds use 'key' field, other worlds use 'name'
    const name = world.key || world.name || 'World';
    const owner = world.owner || '[Neutral]';
    const pop = world.population || 0;
    const industry = world.industry || 0;
    const metal = world.metal || 0;
    const iships = world.iships || 0;
    const pships = world.pships || 0;
    const artifacts = world.artifacts ? world.artifacts.length : 0;

    let html = `<strong>W${worldId} ${name}</strong> (${owner})`;
    html += ` | 👥 ${pop} | 🏭 ${industry} | 🔩 ${metal}`;

    if (iships > 0 || pships > 0) {
        html += ` | 🛡️ I:${iships} P:${pships}`;
    }

    if (artifacts > 0) {
        html += ` | ✨ ${artifacts}`;
    }

    statusPanel.innerHTML = html;
}

function updateStatusPanelForFleet(fleetId) {
    const statusPanel = document.getElementById('status-panel');
    if (!statusPanel || !gameState) return;

    const state = gameState.getState();
    if (!state || !state.fleets) return;

    const fleet = state.fleets[fleetId];
    if (!fleet) return;

    const owner = fleet.owner || 'Unknown';
    const location = state.worlds[fleet.world];
    // Use 'key' for home worlds, 'name' for other worlds
    const locationName = location ? (location.key || location.name || 'World') : 'Unknown';
    const ships = fleet.ships || 0;
    const cargo = typeof fleet.cargo === 'number' ? fleet.cargo : 0;
    const artifacts = fleet.artifacts ? fleet.artifacts.length : 0;
    const isMine = owner === state.playerName;
    const hasPBB = fleet.has_pbb || false;

    let html = `<strong>F${fleetId}</strong> (${owner})`;
    html += ` at ${locationName}`;

    if (isMine) {
        // Always show ships, cargo, and artifacts for owned fleets (even if 0)
        html += ` | 🚀 ${ships}`;
        html += ` | 📦 ${cargo}`;

        if (artifacts > 0) {
            html += ` | ✨ ${artifacts}`;
        }

        if (hasPBB) {
            html += ` | 💣 PBB`;
        }

        if (fleet.moved) {
            html += ` | ➡️ Moving`;
        }
        if (fleet.is_ambushing) {
            html += ` | ⚔️ Ambushing`;
        }
    } else {
        // For enemy fleets, show only ships
        html += ` | 🚀 ${ships}`;
    }

    statusPanel.innerHTML = html;
}

function clearStatusPanel() {
    const statusPanel = document.getElementById('status-panel');
    if (!statusPanel) return;
    statusPanel.innerHTML = 'Hover over a world or fleet to see details';
}

function setupCanvasInteraction(canvas) {
    // Mouse down - start drag
    canvas.addEventListener('mousedown', (e) => {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        camera.startDrag(x, y);
    });

    // Mouse move - drag or hover
    canvas.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        if (e.buttons === 1 && camera.isDragging) {
            camera.updateDrag(x, y);
            renderGame();
        } else {
            // Check for fleet hover first (fleets are smaller and more specific)
            const fleetId = renderer ? renderer.findFleetAtScreen(x, y) : null;

            if (fleetId) {
                // Hovering over a fleet
                const worldLayer = renderer.getLayer('worlds');
                if (worldLayer) {
                    worldLayer.setHoveredWorld(null);
                }
                updateStatusPanelForFleet(fleetId);
                renderGame();
            } else {
                // Check for world hover
                const worldId = renderer ? renderer.findWorldAtScreen(x, y) : null;
                const worldLayer = renderer ? renderer.getLayer('worlds') : null;
                if (worldLayer) {
                    worldLayer.setHoveredWorld(worldId);
                }

                if (worldId) {
                    updateStatusPanelForWorld(worldId);
                } else {
                    clearStatusPanel();
                }
                renderGame();
            }
        }
    });

    // Mouse up - end drag or handle click
    canvas.addEventListener('mouseup', (e) => {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Check if this was a click (not a drag)
        if (!camera.wasSignificantDrag(x, y)) {
            // Click - select world
            const worldId = renderer.findWorldAtScreen(x, y);
            selectedWorldId = worldId;
            selectedFleetId = null;

            const worldLayer = renderer.getLayer('worlds');
            const connectionLayer = renderer.getLayer('connections');
            if (worldLayer) {
                worldLayer.setSelectedWorld(worldId);
            }
            if (connectionLayer) {
                connectionLayer.setSelectedWorld(worldId);
            }

            updateSelectionInfoSidebar();
            updateActionList();
            renderGame();

            // Insert world ID into command input
            if (worldId) {
                insertWorldIdIntoCommand(worldId);
            }
        }

        camera.endDrag();
    });

    // Mouse wheel - zoom
    canvas.addEventListener('wheel', (e) => {
        e.preventDefault();

        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Get world position at mouse
        const worldPos = camera.screenToWorld(x, y, canvas);

        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        camera.zoomAt(worldPos.x, worldPos.y, delta);
        renderGame();
    });

    // Mouse leave - clear hover
    canvas.addEventListener('mouseleave', () => {
        const worldLayer = renderer.getLayer('worlds');
        if (worldLayer) {
            worldLayer.setHoveredWorld(null);
        }
        clearStatusPanel();
        renderGame();
        camera.endDrag();
    });
}

// Start app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}
