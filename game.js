const statusDiv = document.getElementById('connection-status');
const canvas = document.getElementById('game-canvas');
const ctx = canvas.getContext('2d');
const commandInput = document.getElementById('command-input');
const sendBtn = document.getElementById('send-btn');
const logDiv = document.getElementById('log');
const eventLogDiv = document.getElementById('event-log');
const fleetListDiv = document.getElementById('fleet-list');
const worldListDiv = document.getElementById('world-list');
const statusPanel = document.getElementById('status-panel');
const worldInfoDiv = document.getElementById('world-info');
const commandHintDiv = document.getElementById('command-hint');
const queuedOrdersDiv = document.getElementById('queued-orders');
const scoreboardDiv = document.getElementById('scoreboard');
const actionListDiv = document.getElementById('action-list');

// Login Elements
const loginOverlay = document.getElementById('login-overlay');
const gameContainer = document.getElementById('game-container');
const playerNameInput = document.getElementById('player-name-input');
const characterTypeSelect = document.getElementById('character-type-select');
const scoreVoteInput = document.getElementById('score-vote-input');
const joinBtn = document.getElementById('join-btn');

// ---- CONFIG / CONSTANTS ----
const WS_RECONNECT_DELAY_MS = 3000;
const CAMERA_ZOOM_MIN = 0.1;
const CAMERA_ZOOM_MAX = 5;
const CAMERA_DEFAULT_ZOOM = 1;
const CAMERA_FOCUS_ZOOM = 1.5;
const CLICK_MAX_DISTANCE_PX = 5;

// ---- STATE ----
let socket;
let gameState = null;
let worldPositions = {};
let hoveredWorldId = null;
let selectedWorldId = null;
let selectedFleetId = null;
let myPlayerName = null;
let timerInterval = null;

// Camera state
let camera = { x: 0, y: 0, zoom: CAMERA_DEFAULT_ZOOM };
let isDragging = false;
let lastMouseX = 0;
let lastMouseY = 0;
let dragStart = { x: 0, y: 0 };

// ---- GENERIC HELPERS ----
function isSocketOpen() {
    return socket && socket.readyState === WebSocket.OPEN;
}

function safeJsonParse(raw) {
    try {
        return JSON.parse(raw);
    } catch (err) {
        console.error('Failed to parse server message:', err, raw);
        log('Received malformed data from server.');
        return null;
    }
}

function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
}

// ---- NETWORKING ----
function connect() {
    const host = window.location.hostname;
    socket = new WebSocket(`ws://${host}:8765`);

    socket.onopen = handleSocketOpen;
    socket.onmessage = handleSocketMessage;
    socket.onclose = handleSocketClose;
    socket.onerror = handleSocketError;
}

function handleSocketOpen() {
    statusDiv.textContent = 'Connected';
    statusDiv.style.color = '#4caf50';
    log('Connected to server');
}

function handleSocketMessage(event) {
    const data = safeJsonParse(event.data);
    if (!data) return;
    handleMessage(data);
}

function handleSocketClose() {
    statusDiv.textContent = 'Disconnected';
    statusDiv.style.color = '#f44336';
    log('Disconnected from server');
    // Reconnect with simple backoff
    setTimeout(connect, WS_RECONNECT_DELAY_MS);
}

function handleSocketError(error) {
    console.error('WebSocket error:', error);
    statusDiv.textContent = 'Error';
    statusDiv.style.color = '#f44336';
}

// ---- MESSAGE DISPATCH ----
function handleMessage(data) {
    if (data.type === 'welcome') {
        log(`Connected. ID: ${data.id}`);
    } else if (data.type === 'update') {
        handleUpdateMessage(data);
    } else if (data.type === 'delta') {
        handleDeltaMessage(data);
    } else if (data.type === 'timer') {
        handleTimerTick(data);
    } else if (data.type === 'info') {
        log(data.text);
    } else if (data.type === 'error') {
        log(`Error: ${data.text}`);
    } else if (data.type === 'event') {
        logEvent(data.text, data.event_type);
    } else {
        log(`Received: ${JSON.stringify(data)}`);
    }
}

function handleUpdateMessage(data) {
    const isFirstUpdate = !gameState;
    gameState = data.state;

    if (data.state.player_name) {
        myPlayerName = data.state.player_name;
        if (loginOverlay.style.display !== 'none') {
            loginOverlay.style.display = 'none';
            gameContainer.style.display = 'flex';
            resizeCanvas();
            calculateLayout();
        }
    }

    if (loginOverlay.style.display === 'none') {
        calculateLayout();

        if (isFirstUpdate) {
            focusCameraOnHomeworld();
        }

        renderGame();
        updateSidebars();
        updateTimerDisplay();
        updateQueuedOrders();
        updateScoreboard();
        updateActionList();
        if (hoveredWorldId) updateStatusPanel(hoveredWorldId);
        updateWorldInfoSidebar();
    }
}

function handleDeltaMessage(data) {
    if (!gameState) return; // Need full state first

    const changes = data.changes;

    // Apply top-level changes
    if ('score' in changes) gameState.score = changes.score;
    if ('game_turn' in changes) gameState.game_turn = changes.game_turn;
    if ('players_ready' in changes) gameState.players_ready = changes.players_ready;
    if ('total_players' in changes) gameState.total_players = changes.total_players;
    if ('orders' in changes) gameState.orders = changes.orders;

    // Apply world changes
    if (changes.worlds) {
        for (const worldId in changes.worlds) {
            gameState.worlds[worldId] = changes.worlds[worldId];
        }
    }

    // Remove worlds
    if (changes.removed_worlds) {
        changes.removed_worlds.forEach(worldId => {
            delete gameState.worlds[worldId];
            delete worldPositions[worldId];
        });
    }

    // Apply fleet changes
    if (changes.fleets) {
        changes.fleets.forEach(fleetData => {
            const index = gameState.fleets.findIndex(f => f.id === fleetData.id);
            if (index >= 0) {
                gameState.fleets[index] = fleetData;
            } else {
                gameState.fleets.push(fleetData);
            }
        });
    }

    // Remove fleets
    if (changes.removed_fleets) {
        changes.removed_fleets.forEach(fleetId => {
            const index = gameState.fleets.findIndex(f => f.id === fleetId);
            if (index >= 0) {
                gameState.fleets.splice(index, 1);
            }
        });
    }

    // Recalculate layout if worlds changed
    if (changes.worlds || changes.removed_worlds) {
        calculateLayout();
    }

    // Update UI
    renderGame();
    updateSidebars();
    updateTimerDisplay();
    updateQueuedOrders();
    updateScoreboard();
    updateActionList();
    if (hoveredWorldId) updateStatusPanel(hoveredWorldId);
    updateWorldInfoSidebar();
}

function handleTimerTick(data) {
    // Lightweight timer update - only update timer-related info
    if (gameState) {
        gameState.time_remaining = data.time_remaining;
        gameState.players_ready = data.players_ready;
        gameState.total_players = data.total_players;
        updateTimerDisplay();
    }
}

function focusCameraOnHomeworld() {
    if (!gameState || !gameState.worlds || !myPlayerName) return;
    const myWorlds = Object.values(gameState.worlds).filter(
        (w) => w.owner === myPlayerName
    );
    if (myWorlds.length === 0) return;

    const homeWorldId = myWorlds[0].id;
    const pos = worldPositions[homeWorldId];
    if (pos) {
        camera.x = pos.x;
        camera.y = pos.y;
        camera.zoom = CAMERA_DEFAULT_ZOOM;
        selectedWorldId = homeWorldId;
    }
}

function log(message) {
    const entry = document.createElement('div');
    entry.textContent = message;
    logDiv.appendChild(entry);
    logDiv.scrollTop = logDiv.scrollHeight;
}

function logEvent(message, eventType = 'info') {
    const entry = document.createElement('div');
    entry.className = `event-${eventType}`;
    entry.innerHTML = parseMarkdown(message);
    eventLogDiv.appendChild(entry);
    eventLogDiv.scrollTop = eventLogDiv.scrollHeight;

    // Keep only last 50 events
    while (eventLogDiv.children.length > 50) {
        eventLogDiv.removeChild(eventLogDiv.firstChild);
    }
}

function parseMarkdown(text) {
    // Bold
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italic
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Code
    text = text.replace(/`(.*?)`/g, '<code>$1</code>');
    return text;
}

function updateTimerDisplay() {
    if (!gameState) return;
    const minutes = Math.floor(gameState.time_remaining / 60);
    const seconds = gameState.time_remaining % 60;
    const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;

    const timerDisplay = document.getElementById('timer-display');
    if (timerDisplay) {
        timerDisplay.textContent = `Turn ${gameState.game_turn} | ${timeStr} | ${gameState.players_ready}/${gameState.total_players} ready`;
    }
}

function updateQueuedOrders() {
    if (!gameState || !gameState.orders) {
        queuedOrdersDiv.innerHTML = '<div style="color: #888;">No orders queued</div>';
        return;
    }

    queuedOrdersDiv.innerHTML = '<h3>Queued Orders</h3>';

    if (gameState.orders.length === 0) {
        queuedOrdersDiv.innerHTML += '<div style="color: #888;">No orders queued</div>';
        return;
    }

    gameState.orders.forEach((order, index) => {
        const orderDiv = document.createElement('div');
        orderDiv.style.cssText = 'padding: 5px; margin: 2px 0; background: #2a2a2a; border-radius: 3px; display: flex; justify-content: space-between; align-items: center;';

        const orderText = document.createElement('span');
        orderText.textContent = order;
        orderText.style.flex = '1';

        const cancelBtn = document.createElement('button');
        cancelBtn.textContent = '✕';
        cancelBtn.style.cssText = 'background: #f44336; border: none; color: white; padding: 2px 8px; cursor: pointer; border-radius: 3px; margin-left: 10px;';
        cancelBtn.onclick = () => cancelOrder(index);

        orderDiv.appendChild(orderText);
        orderDiv.appendChild(cancelBtn);
        queuedOrdersDiv.appendChild(orderDiv);
    });
}

function updateScoreboard() {
    if (!gameState) return;

    scoreboardDiv.innerHTML = '<h3>Scoreboard</h3>';

    const playerScores = [];

    // Count worlds and ships for each player
    const worldCounts = {};
    const shipCounts = {};

    for (const worldId in gameState.worlds) {
        const world = gameState.worlds[worldId];
        if (world.owner) {
            worldCounts[world.owner] = (worldCounts[world.owner] || 0) + 1;
        }
    }

    if (gameState.fleets) {
        gameState.fleets.forEach(fleet => {
            if (fleet.owner && fleet.ships) {
                shipCounts[fleet.owner] = (shipCounts[fleet.owner] || 0) + (typeof fleet.ships === 'number' ? fleet.ships : 0);
            }
        });
    }

    const allPlayers = new Set([...Object.keys(worldCounts), ...Object.keys(shipCounts)]);

    allPlayers.forEach(playerName => {
        playerScores.push({
            name: playerName,
            worlds: worldCounts[playerName] || 0,
            ships: shipCounts[playerName] || 0,
            isMe: playerName === myPlayerName
        });
    });

    playerScores.sort((a, b) => b.worlds - a.worlds || b.ships - a.ships);

    if (playerScores.length === 0) {
        scoreboardDiv.innerHTML += '<div style="color: #888;">No players yet</div>';
        return;
    }

    playerScores.forEach(player => {
        const playerDiv = document.createElement('div');
        playerDiv.style.cssText = `padding: 5px; margin: 2px 0; background: ${player.isMe ? '#1a3a4a' : '#2a2a2a'}; border-radius: 3px; border-left: 3px solid ${player.isMe ? '#4da6ff' : '#666'};`;
        playerDiv.innerHTML = `
            <div style="font-weight: bold; color: ${player.isMe ? '#4da6ff' : '#fff'};">${player.name}</div>
            <div style="font-size: 0.9em; color: #aaa;">Worlds: ${player.worlds} | Ships: ${player.ships}</div>
        `;
        scoreboardDiv.appendChild(playerDiv);
    });
}

function cancelOrder(index) {
    if (!gameState || !gameState.orders) return;

    // Send cancel command to server
    const orderText = gameState.orders[index];
    if (isSocketOpen()) {
        socket.send(JSON.stringify({
            type: 'command',
            text: `CANCEL ${index}`
        }));
        log(`Cancelled order: ${orderText}`);
    }
}

function calculateLayout() {
    if (!gameState || !gameState.worlds) return;

    const worldIds = Object.keys(gameState.worlds);
    const mapRadius = 800;

    worldIds.forEach((worldId, index) => {
        const world = gameState.worlds[worldId];
        const id = parseInt(worldId);

        // Create a deterministic position based on world ID
        const angle = (id / 255) * Math.PI * 2;
        const radius = mapRadius * (0.5 + Math.sin(id * 0.1) * 0.3);

        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius;

        const pop = (typeof world.population === 'number') ? world.population : 0;
        const worldRadius = 15 + pop * 0.1;

        worldPositions[worldId] = {
            x: x,
            y: y,
            radius: Math.min(worldRadius, 30)
        };
    });
}

function resizeCanvas() {
    const container = canvas.parentElement;
    canvas.width = container.clientWidth;
    canvas.height = container.clientHeight;
    renderGame();
}

function renderGame() {
    if (!gameState) return;

    renderBackground();
    ctx.save();
    applyCameraTransform();

    const movingFleets = getMovingFleetsFromOrders();
    const stationaryFleetsByWorld = groupStationaryFleetsByWorld(movingFleets);

    renderConnections();
    renderWorlds();
    renderStationaryFleets(stationaryFleetsByWorld);
    renderMovingFleets(movingFleets);

    ctx.restore();
}

function renderBackground() {
    ctx.fillStyle = '#050505';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function applyCameraTransform() {
    ctx.translate(canvas.width / 2, canvas.height / 2);
    ctx.scale(camera.zoom, camera.zoom);
    ctx.translate(-camera.x, -camera.y);
}

function renderConnections() {
    ctx.strokeStyle = '#444';
    ctx.lineWidth = 1 / camera.zoom;

    const drawnConnections = new Set();

    for (const worldId in gameState.worlds) {
        const world = gameState.worlds[worldId];
        const pos1 = worldPositions[worldId];
        if (!pos1) continue;

        world.connections.forEach((targetId) => {
            if (!worldPositions[targetId]) return;

            const pos2 = worldPositions[targetId];
            const connectionKey = [worldId, targetId].sort().join('-');

            if (!drawnConnections.has(connectionKey)) {
                ctx.beginPath();
                ctx.moveTo(pos1.x, pos1.y);
                ctx.lineTo(pos2.x, pos2.y);
                ctx.stroke();
                drawnConnections.add(connectionKey);
            }
        });
    }
}

function renderWorlds() {
    for (const worldId in gameState.worlds) {
        const world = gameState.worlds[worldId];
        const pos = worldPositions[worldId];
        if (!pos) continue;

        renderWorldDefenses(world, pos);
        renderWorldCircle(worldId, world, pos);
        renderWorldLabel(worldId, pos);
    }
}

function renderWorldDefenses(world, pos) {
    if (world.iships <= 0 && world.pships <= 0) return;

    ctx.beginPath();
    ctx.arc(pos.x, pos.y, pos.radius + 5, 0, 2 * Math.PI);

    if (world.iships > 0 && world.pships > 0) {
        ctx.strokeStyle = '#00ffff'; // Cyan for both
    } else if (world.iships > 0) {
        ctx.strokeStyle = '#4da6ff'; // Blue for IShips
    } else {
        ctx.strokeStyle = '#4caf50'; // Green for PShips
    }

    ctx.lineWidth = 3 / camera.zoom;
    ctx.stroke();
}

function renderWorldCircle(worldId, world, pos) {
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, pos.radius, 0, 2 * Math.PI);

    if (world.owner) {
        ctx.fillStyle = world.owner === myPlayerName ? '#4da6ff' : '#ff5722';
    } else {
        ctx.fillStyle = '#666';
    }

    if (hoveredWorldId == worldId) {
        ctx.fillStyle = '#88ccee';
    }

    ctx.fill();

    if (selectedWorldId == worldId) {
        ctx.strokeStyle = '#ffff00';
        ctx.lineWidth = 4 / camera.zoom;
    } else {
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2 / camera.zoom;
    }

    ctx.stroke();
}

function renderWorldLabel(worldId, pos) {
    const fontSize = Math.max(10, 14 / camera.zoom);
    ctx.fillStyle = '#fff';
    ctx.font = `bold ${fontSize}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(worldId, pos.x, pos.y);
}

function getMovingFleetsFromOrders() {
    const movingFleets = {};
    if (!gameState.orders) return movingFleets;

    gameState.orders.forEach((orderText) => {
        const moveMatch = orderText.match(/^Move F(\d+) -> W(\d+)$/);
        if (!moveMatch) return;

        const fleetId = parseInt(moveMatch[1], 10);
        const destId = parseInt(moveMatch[2], 10);
        const fleet = gameState.fleets.find((f) => f.id === fleetId);
        if (!fleet) return;

        movingFleets[fleetId] = {
            origin: fleet.world,
            dest: destId,
            isMultiHop: orderText.includes('-> W'),
        };
    });

    return movingFleets;
}

function groupStationaryFleetsByWorld(movingFleets) {
    const fleetsByWorld = {};
    if (!gameState.fleets) return fleetsByWorld;

    gameState.fleets.forEach((fleet) => {
        if (movingFleets[fleet.id]) return; // skip moving fleets

        if (!fleetsByWorld[fleet.world]) {
            fleetsByWorld[fleet.world] = [];
        }
        fleetsByWorld[fleet.world].push(fleet);
    });

    return fleetsByWorld;
}

function renderStationaryFleets(fleetsByWorld) {
    for (const worldId in fleetsByWorld) {
        const worldPos = worldPositions[worldId];
        if (!worldPos) continue;

        const fleets = fleetsByWorld[worldId];
        const friendlyFleets = fleets.filter((f) => f.owner === myPlayerName);
        const hostileFleets = fleets.filter((f) => f.owner !== myPlayerName);

        const fleetIconSize = Math.max(6, 10 / camera.zoom);
        const worldRadius = worldPos.radius;

        renderFleetRing(
            friendlyFleets,
            worldPos,
            worldRadius + 5,
            fleetIconSize,
            true
        );
        renderFleetRing(
            hostileFleets,
            worldPos,
            worldRadius + 15,
            fleetIconSize,
            false
        );
    }
}

function renderFleetRing(fleets, worldPos, orbitRadius, fleetIconSize, isFriendly) {
    fleets.forEach((fleet, index) => {
        const angle = (index / fleets.length) * 2 * Math.PI;
        const drawX = worldPos.x + Math.cos(angle) * orbitRadius;
        const drawY = worldPos.y + Math.sin(angle) * orbitRadius;

        if (isFriendly && selectedFleetId == fleet.id) {
            ctx.strokeStyle = '#ffff00';
            ctx.lineWidth = 2 / camera.zoom;
            ctx.strokeRect(
                drawX - fleetIconSize / 2 - 1,
                drawY - fleetIconSize / 2 - 1,
                fleetIconSize + 2,
                fleetIconSize + 2
            );
        }

        ctx.fillStyle = isFriendly ? '#4caf50' : '#f44336';
        ctx.fillRect(
            drawX - fleetIconSize / 2,
            drawY - fleetIconSize / 2,
            fleetIconSize,
            fleetIconSize
        );

        if (fleetIconSize > 4) {
            ctx.fillStyle = '#fff';
            ctx.font = `${fleetIconSize * 0.8}px Arial`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(fleet.id, drawX, drawY);
        }
    });
}

function renderMovingFleets(movingFleets) {
    if (!gameState.fleets) return;

    for (const fleetId in movingFleets) {
        const move = movingFleets[fleetId];
        const originPos = worldPositions[move.origin];
        const destPos = worldPositions[move.dest];
        if (!originPos || !destPos) continue;

        const midX = (originPos.x + destPos.x) / 2;
        const midY = (originPos.y + destPos.y) / 2;

        const fleet = gameState.fleets.find((f) => f.id == fleetId);
        if (!fleet) continue;

        const size = Math.max(6, 10 / camera.zoom);
        const color = fleet.owner === myPlayerName ? '#4caf50' : '#f44336';

        if (move.isMultiHop) {
            ctx.beginPath();
            ctx.moveTo(midX, midY - size / 2);
            ctx.lineTo(midX - size / 2, midY + size / 2);
            ctx.lineTo(midX + size / 2, midY + size / 2);
            ctx.closePath();
            ctx.fillStyle = color;
            ctx.fill();
        } else {
            ctx.fillStyle = color;
            ctx.fillRect(midX - size / 2, midY - size / 2, size, size);
        }

        if (size > 4) {
            ctx.fillStyle = '#fff';
            ctx.font = `${size * 0.8}px Arial`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(fleet.id, midX, midY);
        }
    }
}

function handleSelection(type, id) {
    if (type === 'world') {
        if (selectedWorldId == id) {
            selectedWorldId = null;
        } else {
            selectedWorldId = id;
            selectedFleetId = null;
            updateWorldInfoSidebar();
        }
    } else if (type === 'fleet') {
        if (selectedFleetId == id) {
            selectedFleetId = null;
        } else {
            selectedFleetId = id;
            selectedWorldId = null;
        }
    }
    renderGame();
    updateSidebars();
}

function updateSidebars() {
    updateFleetList();
    updateWorldList();
}

function updateFleetList() {
    if (!gameState || !gameState.fleets) {
        fleetListDiv.innerHTML = '<h3>Your Fleets</h3><div style="color: #888;">No fleets</div>';
        return;
    }

    const myFleets = gameState.fleets.filter(f => f.owner === myPlayerName);

    fleetListDiv.innerHTML = '<h3>Your Fleets</h3>';

    if (myFleets.length === 0) {
        fleetListDiv.innerHTML += '<div style="color: #888;">No fleets</div>';
        return;
    }

    myFleets.forEach(fleet => {
        const fleetDiv = document.createElement('div');
        fleetDiv.style.cssText = `padding: 8px; margin: 4px 0; background: ${selectedFleetId == fleet.id ? '#1a4a3a' : '#2a2a2a'}; border-radius: 3px; cursor: pointer; border-left: 3px solid #4caf50;`;
        fleetDiv.onclick = () => handleSelection('fleet', fleet.id);

        fleetDiv.innerHTML = `
            <div style="font-weight: bold;">Fleet ${fleet.id}</div>
            <div style="font-size: 0.9em; color: #aaa;">
                Ships: ${fleet.ships || 0}<br>
                Location: World ${fleet.world}${fleet.moved ? ' (moved)' : ''}
            </div>
        `;

        fleetListDiv.appendChild(fleetDiv);
    });
}

function updateWorldList() {
    if (!gameState || !gameState.worlds) {
        worldListDiv.innerHTML = '<h3>Your Worlds</h3><div style="color: #888;">No worlds</div>';
        return;
    }

    const myWorlds = Object.values(gameState.worlds).filter(w => w.owner === myPlayerName);

    worldListDiv.innerHTML = '<h3>Your Worlds</h3>';

    if (myWorlds.length === 0) {
        worldListDiv.innerHTML += '<div style="color: #888;">No worlds</div>';
        return;
    }

    myWorlds.forEach(world => {
        const worldDiv = document.createElement('div');
        worldDiv.style.cssText = `padding: 8px; margin: 4px 0; background: ${selectedWorldId == world.id ? '#1a3a4a' : '#2a2a2a'}; border-radius: 3px; cursor: pointer; border-left: 3px solid #4da6ff;`;
        worldDiv.onclick = () => handleSelection('world', world.id);

        worldDiv.innerHTML = `
            <div style="font-weight: bold;">World ${world.id}</div>
            <div style="font-size: 0.9em; color: #aaa;">
                Pop: ${world.population}/${world.limit}<br>
                Ind: ${world.industry} | Metal: ${world.metal}<br>
                Defense: I${world.iships} P${world.pships}
            </div>
        `;

        worldListDiv.appendChild(worldDiv);
    });
}

function updateActionList() {
    if (!selectedWorldId && !selectedFleetId) {
        actionListDiv.innerHTML = '<div style="color: #888; padding: 10px;">Select a world or fleet to see actions</div>';
        return;
    }

    actionListDiv.innerHTML = '<h3>Quick Actions</h3>';

    if (selectedFleetId) {
        const fleet = gameState.fleets.find(f => f.id == selectedFleetId);
        if (fleet && fleet.owner === myPlayerName) {
            createActionButton('Move Fleet', () => {
                const dest = prompt('Enter destination world ID:');
                if (dest) {
                    commandInput.value = `F${fleet.id}W${dest}`;
                    sendCommand();
                }
            });

            createActionButton('Transfer Ships', () => {
                const amount = prompt('Enter amount to transfer:');
                const target = prompt('Enter target (I/P or F<id>):');
                if (amount && target) {
                    commandInput.value = `F${fleet.id}T${amount}${target}`;
                    sendCommand();
                }
            });

            createActionButton('Attack Fleet', () => {
                const target = prompt('Enter target fleet ID:');
                if (target) {
                    commandInput.value = `F${fleet.id}AF${target}`;
                    sendCommand();
                }
            });

            createActionButton('Ambush', () => {
                commandInput.value = `F${fleet.id}A`;
                sendCommand();
            });
        }
    }

    if (selectedWorldId) {
        const world = gameState.worlds[selectedWorldId];
        if (world && world.owner === myPlayerName) {
            createActionButton('Build on Fleet', () => {
                const fleetId = prompt('Enter fleet ID:');
                const amount = prompt('Enter amount to build:');
                if (fleetId && amount) {
                    commandInput.value = `W${world.id}B${amount}F${fleetId}`;
                    sendCommand();
                }
            });

            createActionButton('Build IShips', () => {
                const amount = prompt('Enter amount to build:');
                if (amount) {
                    commandInput.value = `W${world.id}B${amount}I`;
                    sendCommand();
                }
            });

            createActionButton('Build PShips', () => {
                const amount = prompt('Enter amount to build:');
                if (amount) {
                    commandInput.value = `W${world.id}B${amount}P`;
                    sendCommand();
                }
            });
        }
    }
}

function createActionButton(label, callback) {
    const btn = document.createElement('button');
    btn.textContent = label;
    btn.style.cssText = 'width: 100%; padding: 10px; margin: 5px 0; background: #4caf50; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 14px;';
    btn.onmouseover = () => btn.style.background = '#45a049';
    btn.onmouseout = () => btn.style.background = '#4caf50';
    btn.onclick = callback;
    actionListDiv.appendChild(btn);
}

function updateStatusPanel(worldId) {
    if (!worldId || !gameState || !gameState.worlds[worldId]) {
        statusPanel.innerHTML = '<div style="color: #888;">Hover over a world to see details</div>';
        return;
    }

    const world = gameState.worlds[worldId];

    let html = `<strong>World ${world.id}</strong> `;

    if (world.owner) {
        html += `<span style="color: ${world.owner === myPlayerName ? '#4da6ff' : '#ff5722'};">Owner: ${world.owner}</span> `;
    } else {
        html += `<span style="color: #888;">Unclaimed</span> `;
    }

    if (typeof world.population === 'number') {
        html += `| Pop: ${world.population}/${world.limit} | Ind: ${world.industry} | Metal: ${world.metal} | Mines: ${world.mines} | Defense: I${world.iships} P${world.pships}`;
    } else {
        html += `<span style="color: #888;">| No current intel</span>`;
    }

    statusPanel.innerHTML = html;
}

function updateWorldInfoSidebar() {
    if (!selectedWorldId || !gameState || !gameState.worlds[selectedWorldId]) {
        worldInfoDiv.innerHTML = '';
        return;
    }

    const world = gameState.worlds[selectedWorldId];

    let html = `<h3>World ${world.id} Details</h3>`;

    if (world.owner) {
        html += `<div style="color: ${world.owner === myPlayerName ? '#4da6ff' : '#ff5722'}; font-weight: bold;">Owner: ${world.owner}</div>`;
    } else {
        html += `<div style="color: #888;">Unclaimed</div>`;
    }

    if (typeof world.population === 'number') {
        html += `
            <div style="margin-top: 15px;">
                <h4>Resources</h4>
                <div>Population: ${world.population}/${world.limit}</div>
                <div>Industry: ${world.industry}</div>
                <div>Metal: ${world.metal}</div>
                <div>Mines: ${world.mines}</div>
                <div style="margin-top: 10px;">
                    <strong>Defenses</strong><br>
                    IShips: ${world.iships}<br>
                    PShips: ${world.pships}
                </div>
            </div>
        `;

        const maxBuild = Math.min(world.industry || 0, world.metal || 0, world.population || 0);
        if (maxBuild > 0 && world.owner === myPlayerName) {
            html += `<div style="margin-top: 10px; padding: 10px; background: #2a2a2a; border-radius: 3px;">
                <strong>Can build:</strong> ${maxBuild} ships this turn
            </div>`;
        }
    } else {
        html += `<div style="color: #888; margin-top: 10px;">No current visibility</div>`;
        if (world.turn_last_seen) {
            html += `<div style="font-size: 0.8em;">Last seen: Turn ${world.turn_last_seen}</div>`;
        }
    }

    if (world.connections && world.connections.length > 0) {
        html += `<div style="margin-top: 15px;">
            <h4>Connections</h4>
            <div style="display: flex; flex-wrap: wrap; gap: 5px;">`;

        world.connections.forEach(connId => {
            html += `<button style="padding: 5px 10px; background: #4da6ff; color: white; border: none; border-radius: 3px; cursor: pointer;" onclick="handleSelection('world', ${connId})">W${connId}</button>`;
        });

        html += `</div></div>`;
    }

    // Show fleets at this world
    if (gameState.fleets) {
        const fleetsHere = gameState.fleets.filter(f => f.world == world.id);
        if (fleetsHere.length > 0) {
            html += `<div style="margin-top: 15px;">
                <h4>Fleets in Orbit</h4>`;

            fleetsHere.forEach(fleet => {
                const isMine = fleet.owner === myPlayerName;
                html += `<div style="padding: 5px; margin: 3px 0; background: ${isMine ? '#1a4a3a' : '#4a1a1a'}; border-radius: 3px;">
                    <strong>Fleet ${fleet.id}</strong> (${fleet.owner})<br>
                    Ships: ${fleet.ships}${fleet.moved ? ' (moved)' : ''}
                </div>`;
            });

            html += `</div>`;
        }
    }

    worldInfoDiv.innerHTML = html;
}

function updateCommandHint() {
    const cmd = commandInput.value.trim().toUpperCase();

    if (cmd === '') {
        commandHintDiv.textContent = 'Examples: F1W5, W1B10F1, F1AF2, TURN';
        return;
    }

    if (cmd.startsWith('F') && cmd.includes('W')) {
        commandHintDiv.textContent = 'Move fleet to world';
    } else if (cmd.startsWith('W') && cmd.includes('B')) {
        commandHintDiv.textContent = 'Build ships (I/P/F<id>)';
    } else if (cmd.startsWith('F') && cmd.includes('T')) {
        commandHintDiv.textContent = 'Transfer ships to target';
    } else if (cmd.startsWith('F') && cmd.includes('AF')) {
        commandHintDiv.textContent = 'Attack fleet';
    } else if (cmd.startsWith('F') && cmd.endsWith('AP')) {
        commandHintDiv.textContent = 'Fire at population';
    } else if (cmd.startsWith('F') && cmd.endsWith('AI')) {
        commandHintDiv.textContent = 'Fire at industry';
    } else if (cmd.startsWith('F') && cmd.endsWith('A')) {
        commandHintDiv.textContent = 'Set ambush';
    } else if (cmd === 'TURN') {
        commandHintDiv.textContent = 'End your turn';
    } else {
        commandHintDiv.textContent = '';
    }
}

function getWorldPos(evt) {
    const rect = canvas.getBoundingClientRect();
    const screenX = evt.clientX - rect.left;
    const screenY = evt.clientY - rect.top;
    const x = (screenX - canvas.width / 2) / camera.zoom + camera.x;
    const y = (screenY - canvas.height / 2) / camera.zoom + camera.y;
    return { x, y };
}

canvas.addEventListener('mousedown', (e) => {
    isDragging = true;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
    dragStart = { x: e.clientX, y: e.clientY };
});

canvas.addEventListener('mouseup', (e) => {
    isDragging = false;
    const dist = Math.hypot(e.clientX - dragStart.x, e.clientY - dragStart.y);
    if (dist < CLICK_MAX_DISTANCE_PX) {
        const worldPos = getWorldPos(e);
        const found = findWorldAtPosition(worldPos);
        if (found) {
            handleSelection('world', found);
        }
    }
});

canvas.addEventListener('mouseleave', () => {
    isDragging = false;
});

canvas.addEventListener('mousemove', (e) => {
    if (isDragging) {
        const dx = e.clientX - lastMouseX;
        const dy = e.clientY - lastMouseY;
        camera.x -= dx / camera.zoom;
        camera.y -= dy / camera.zoom;
        lastMouseX = e.clientX;
        lastMouseY = e.clientY;
        renderGame();
    } else {
        const worldPos = getWorldPos(e);
        const found = findWorldAtPosition(worldPos);

        if (found !== hoveredWorldId) {
            hoveredWorldId = found;
            renderGame();
            updateStatusPanel(found);
        }
    }
});

function findWorldAtPosition(worldPos) {
    for (const worldId in worldPositions) {
        const pos = worldPositions[worldId];
        const dx = worldPos.x - pos.x;
        const dy = worldPos.y - pos.y;
        if (dx * dx + dy * dy < pos.radius * pos.radius) {
            return worldId;
        }
    }
    return null;
}

canvas.addEventListener('wheel', (e) => {
    e.preventDefault();
    const zoomSensitivity = 0.001;
    const delta = -e.deltaY * zoomSensitivity;
    const newZoom = clamp(camera.zoom + delta, CAMERA_ZOOM_MIN, CAMERA_ZOOM_MAX);

    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    const worldX = (mouseX - canvas.width / 2) / camera.zoom + camera.x;
    const worldY = (mouseY - canvas.height / 2) / camera.zoom + camera.y;

    camera.zoom = newZoom;
    camera.x = worldX - (mouseX - canvas.width / 2) / newZoom;
    camera.y = worldY - (mouseY - canvas.height / 2) / newZoom;

    renderGame();
}, { passive: false });

commandInput.addEventListener('input', updateCommandHint);

function sendCommand() {
    const command = commandInput.value;
    if (command && isSocketOpen()) {
        socket.send(JSON.stringify({ type: 'command', text: command }));
        log(`Sent: ${command}`);
        commandInput.value = '';
        commandHintDiv.textContent = '';
    }
}

function joinGame() {
    const name = playerNameInput.value.trim();
    const charType = characterTypeSelect.value;
    const scoreVote = scoreVoteInput.value;
    if (name && isSocketOpen()) {
        socket.send(JSON.stringify({
            type: 'command',
            text: `JOIN ${name} ${scoreVote} ${charType}`
        }));
    }
}

function endTurn() {
    if (isSocketOpen()) {
        socket.send(JSON.stringify({ type: 'command', text: 'TURN' }));
        log('Sent: TURN');
    }
}

sendBtn.addEventListener('click', sendCommand);
joinBtn.addEventListener('click', joinGame);
playerNameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') joinGame();
});
commandInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendCommand();
});

const controlsDiv = document.getElementById('controls');
if (!document.getElementById('end-turn-btn')) {
    const endTurnBtn = document.createElement('button');
    endTurnBtn.id = 'end-turn-btn';
    endTurnBtn.textContent = 'End Turn';
    endTurnBtn.style.backgroundColor = '#e91e63';
    endTurnBtn.style.marginLeft = '10px';
    endTurnBtn.onclick = endTurn;
    controlsDiv.appendChild(endTurnBtn);
}

// Initial resize
window.addEventListener('load', resizeCanvas);
window.addEventListener('resize', resizeCanvas);
connect();