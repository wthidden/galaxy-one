# StarWeb Architecture Refactor Plan

## Overview
Refactor from monolithic to modular architecture supporting:
- Dynamic client updates (movement animations, real-time events)
- Player communications (chat, diplomacy)
- Advanced visualizations (alliances, timeseries, movement paths)
- Easy feature extensions (cargo, apostles, robots)

---

## Backend Architecture

### Proposed Structure
```
server/
├── main.py                 # Entry point, server initialization
├── websocket_handler.py    # WebSocket connection management
├── game/
│   ├── state.py           # GameState class, world/fleet/player data
│   ├── turn_processor.py  # Turn execution logic
│   ├── commands.py        # Command parsing and validation
│   ├── mechanics/
│   │   ├── combat.py      # Combat resolution
│   │   ├── movement.py    # Fleet movement, paths
│   │   ├── production.py  # Economic production
│   │   ├── cargo.py       # Cargo mechanics (future)
│   │   ├── apostles.py    # Apostle mechanics (future)
│   │   └── robots.py      # Robot mechanics (future)
│   └── alliances.py       # Alliance management
├── events/
│   ├── event_bus.py       # Pub/sub event system
│   ├── event_types.py     # Event type definitions
│   └── handlers.py        # Event handlers
├── messaging/
│   ├── message_router.py  # Route messages to players
│   ├── chat.py            # Chat system
│   └── diplomacy.py       # Diplomatic messages
└── data/
    ├── delta.py           # Delta calculation
    ├── serializer.py      # State serialization
    └── visibility.py      # Fog of war, visibility rules
```

### Key Backend Patterns

#### 1. Event-Driven Architecture
```python
# Instead of:
await send_event(player, "Fleet moved")

# Use event bus:
event_bus.publish(Event(
    type="FLEET_MOVED",
    fleet_id=5,
    from_world=1,
    to_world=2,
    player=player,
    timestamp=game_turn
))

# Handlers subscribe:
@event_bus.subscribe("FLEET_MOVED")
async def broadcast_movement(event):
    for p in get_observers(event.from_world, event.to_world):
        await send_delta(p, {"fleets": [...]})
```

#### 2. Command Pattern
```python
class Command:
    def validate(self, player, game_state): pass
    def execute(self, game_state): pass
    def to_order(self): pass

class MoveFleetCommand(Command):
    def __init__(self, fleet_id, path):
        self.fleet_id = fleet_id
        self.path = path
```

#### 3. State Management
```python
class GameState:
    def __init__(self):
        self.worlds = WorldCollection()
        self.fleets = FleetCollection()
        self.players = PlayerCollection()
        self.alliances = AllianceManager()
        self.history = TurnHistory()

    def snapshot(self): pass
    def get_visible_state(self, player): pass
    def apply_delta(self, delta): pass
```

---

## Frontend Architecture

### Proposed Structure
```
client/
├── main.js                 # Entry point, initialization
├── network/
│   ├── websocket.js       # WebSocket connection
│   ├── message_handler.js # Message routing
│   └── state_sync.js      # State synchronization
├── state/
│   ├── game_state.js      # Client-side state management
│   ├── state_manager.js   # Merge deltas, maintain history
│   └── cache.js           # Asset caching
├── rendering/
│   ├── renderer.js        # Main render loop
│   ├── camera.js          # Camera/viewport management
│   ├── layers/
│   │   ├── layer_manager.js    # Layer system
│   │   ├── background_layer.js
│   │   ├── connection_layer.js
│   │   ├── world_layer.js
│   │   ├── fleet_layer.js
│   │   ├── overlay_layer.js    # Generic overlay base
│   │   ├── alliance_overlay.js
│   │   ├── history_overlay.js
│   │   └── movement_overlay.js
│   └── animations/
│       ├── animator.js         # Animation engine
│       ├── fleet_movement.js   # Ship movement animations
│       └── effects.js          # Combat, explosions, etc.
├── ui/
│   ├── ui_manager.js      # Coordinate all UI
│   ├── panels/
│   │   ├── status_panel.js
│   │   ├── sidebar_panel.js
│   │   ├── command_panel.js
│   │   └── chat_panel.js
│   └── controls/
│       ├── world_selector.js
│       ├── fleet_selector.js
│       └── overlay_controls.js
└── utils/
    ├── layout.js          # World positioning
    └── helpers.js         # Utility functions
```

### Key Frontend Patterns

#### 1. Layer System
```javascript
class LayerManager {
    constructor(canvas) {
        this.layers = [];
        this.overlays = new Map();
    }

    addLayer(layer) { this.layers.push(layer); }

    toggleOverlay(name, enabled) {
        if (enabled) {
            this.overlays.set(name, new OVERLAY_TYPES[name]());
        } else {
            this.overlays.delete(name);
        }
    }

    render(ctx, camera, gameState) {
        // Render base layers
        this.layers.forEach(l => l.render(ctx, camera, gameState));

        // Render active overlays
        this.overlays.forEach(o => o.render(ctx, camera, gameState));
    }
}

// Usage:
layerManager.toggleOverlay('alliance', true);
layerManager.toggleOverlay('history', true);
```

#### 2. Animation System
```javascript
class Animator {
    constructor() {
        this.animations = [];
    }

    add(animation) {
        this.animations.push(animation);
    }

    update(dt) {
        this.animations = this.animations.filter(anim => {
            anim.update(dt);
            return !anim.isComplete();
        });
    }

    render(ctx) {
        this.animations.forEach(a => a.render(ctx));
    }
}

class FleetMovementAnimation {
    constructor(fleet, fromPos, toPos, duration) {
        this.fleet = fleet;
        this.from = fromPos;
        this.to = toPos;
        this.duration = duration;
        this.elapsed = 0;
    }

    update(dt) {
        this.elapsed += dt;
    }

    render(ctx) {
        const t = this.elapsed / this.duration;
        const x = lerp(this.from.x, this.to.x, t);
        const y = lerp(this.from.y, this.to.y, t);
        // Draw fleet at interpolated position
    }
}
```

#### 3. State Management
```javascript
class GameStateManager {
    constructor() {
        this.current = null;
        this.history = [];
        this.listeners = new Map();
    }

    applyFullUpdate(state) {
        this.current = state;
        this.notifyListeners('full-update');
    }

    applyDelta(delta) {
        mergeDelta(this.current, delta);
        this.notifyListeners('delta-update', delta);
    }

    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    notifyListeners(event, data) {
        (this.listeners.get(event) || []).forEach(cb => cb(data));
    }
}

// Usage:
stateManager.on('delta-update', (delta) => {
    if (delta.fleets) {
        animateFleetChanges(delta.fleets);
    }
});
```

---

## Communication Protocol Extensions

### New Message Types

#### Server → Client
```javascript
// Movement animation trigger
{
    type: "animate_movement",
    fleet_id: 5,
    path: [1, 2, 3],
    duration: 2000  // ms
}

// Player message
{
    type: "player_message",
    from: "Alice",
    to: "Bob",
    content: "Peace?",
    channel: "private"
}

// Alliance update
{
    type: "alliance_update",
    alliance_id: 1,
    members: ["Alice", "Bob"],
    worlds: [1, 2, 3, 5, 8]
}

// Historical data for visualization
{
    type: "history_snapshot",
    turn: 10,
    player_territories: {
        "Alice": [1, 2, 3],
        "Bob": [5, 8, 13]
    }
}
```

#### Client → Server
```javascript
// Chat message
{
    type: "chat",
    to: "Bob",  // or "all" for public
    message: "Hello!"
}

// Request overlay data
{
    type: "request_data",
    data_type: "alliance_map",
    params: {}
}

// Request historical data
{
    type: "request_history",
    turns: [1, 2, 3, 4, 5]
}
```

---

## Feature Extensions

### 1. Movement Animation
```javascript
// When server sends movement order execution:
{
    type: "fleet_moving",
    fleet_id: 5,
    from_world: 1,
    to_world: 5,
    path: [1, 3, 5],
    eta_turns: 2
}

// Client creates animation:
animator.add(new FleetMovementAnimation(fleet, path, duration));
```

### 2. Alliance Overlay
```javascript
class AllianceOverlay extends Overlay {
    render(ctx, camera, gameState) {
        const alliances = gameState.alliances;

        alliances.forEach(alliance => {
            const color = alliance.color;
            alliance.worlds.forEach(worldId => {
                // Draw colored border around allied worlds
                drawAllianceBorder(worldId, color);
            });

            // Draw lines connecting alliance members' homeworlds
            drawAllianceConnections(alliance.members);
        });
    }
}
```

### 3. History Timeseries Overlay
```javascript
class HistoryOverlay extends Overlay {
    constructor() {
        this.selectedTurn = null;
        this.historyData = null;
    }

    render(ctx, camera, gameState) {
        if (!this.historyData) return;

        // Show world ownership at selected historical turn
        const snapshot = this.historyData[this.selectedTurn];

        Object.keys(snapshot.worlds).forEach(worldId => {
            const historicalOwner = snapshot.worlds[worldId].owner;
            const currentOwner = gameState.worlds[worldId].owner;

            if (historicalOwner !== currentOwner) {
                // Highlight world that changed ownership
                drawOwnershipChange(worldId, historicalOwner, currentOwner);
            }
        });
    }
}
```

### 4. Cargo/Apostles/Robots
```python
# Backend - easy to add new mechanics
class CargoMechanic:
    def load(self, fleet, world, amount): pass
    def unload(self, fleet, world, amount): pass

class ApostleMechanic:
    def convert_population(self, apostle, world): pass
    def spread_faith(self, apostle): pass

class RobotMechanic:
    def automate_production(self, robot, world): pass
    def execute_ai_orders(self, robot): pass
```

---

## Migration Path

### Phase 1: Backend Refactor
1. Extract game logic into separate modules
2. Implement event bus
3. Add command pattern
4. Create alliance system

### Phase 2: Frontend Refactor
1. Split into modules
2. Implement layer system
3. Add animation engine
4. Create state manager

### Phase 3: New Features
1. Player messaging
2. Alliance overlay
3. Movement animations
4. History visualization

### Phase 4: Advanced Mechanics
1. Cargo system
2. Apostles
3. Robots
4. Real-time combat

---

## Benefits

✅ **Maintainability**: Each feature in its own module
✅ **Extensibility**: Add new mechanics without touching core code
✅ **Testability**: Each component can be tested independently
✅ **Performance**: Targeted updates, efficient rendering
✅ **Scalability**: Event-driven architecture handles complex interactions
✅ **Clarity**: Clear separation of concerns

---

## Next Steps

Would you like me to:
1. Start with backend refactor (event bus, modular structure)?
2. Start with frontend refactor (layer system, animations)?
3. Implement a specific feature first (e.g., alliance overlay)?
4. Create a hybrid approach (refactor as we add features)?
