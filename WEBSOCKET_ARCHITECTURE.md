# WebSocket Architecture

## Overview

Clean separation of concerns for WebSocket management, integrating with the event bus system.

## Architecture Diagram

```
Client WebSocket
       ↓
[websocket_handler.py] ← Main entry point
       ↓
       ├→ [connection_manager.py] ← Manage connections
       │    - Register/unregister
       │    - Track players
       │    - Broadcast
       │
       ├→ [message_router.py] ← Route incoming messages
       │    - Parse JSON
       │    - Dispatch to handlers
       │
       └→ [message_sender.py] ← Send outgoing messages
            - Full updates
            - Delta updates
            - Timer ticks
            - Events, errors, info
            - Animations
            - Chat

[Event Bus] ← Pub/sub communication
    ↓
[events/handlers.py] ← React to game events
    - Send animations
    - Notify players
    - Broadcast updates
```

## Components

### 1. WebSocket Handler (`websocket_handler.py`)

**Purpose**: Main coordinator for WebSocket operations

**Responsibilities**:
- Handle connection lifecycle
- Coordinate between components
- Provide high-level operations (broadcast, send_update_to_all)

**Key Methods**:
```python
async def handle_connection(websocket)
async def broadcast_to_all(message, exclude_players)
async def send_update_to_all(force_full=False)
async def send_timer_tick_to_all()
```

### 2. Connection Manager (`connection_manager.py`)

**Purpose**: Track and manage WebSocket connections

**Responsibilities**:
- Register new connections
- Unregister disconnected clients
- Map websockets ↔ players
- Safe message sending with error handling

**Key Methods**:
```python
async def register(websocket) -> Player
async def unregister(websocket)
def get_player(websocket) -> Player
def get_all_players() -> list[Player]
async def broadcast(message, exclude)
```

### 3. Message Router (`message_router.py`)

**Purpose**: Route incoming messages to appropriate handlers

**Responsibilities**:
- Parse JSON messages
- Extract message type
- Dispatch to registered handlers
- Handle errors gracefully

**Key Methods**:
```python
def register_handler(message_type, handler)
async def route(player, raw_message)
def has_handler(message_type) -> bool
```

**Usage Example**:
```python
router = get_message_router()

async def handle_command(player, data):
    command_text = data.get("text")
    # Process command...

router.register_handler("command", handle_command)
```

### 4. Message Sender (`message_sender.py`)

**Purpose**: Send various message types to clients

**Responsibilities**:
- Build game state for players
- Calculate deltas
- Format messages properly
- Handle all outgoing message types

**Key Methods**:
```python
async def send_welcome(player)
async def send_full_update(player)
async def send_delta_update(player)
async def send_timer_tick(player)
async def send_info(player, message)
async def send_error(player, message)
async def send_event(player, message, event_type)
async def send_animation(player, animation_data)
async def send_chat(player, from_player, message, channel)
async def send_alliance_update(player, alliance_data)
```

### 5. Event Handlers (`events/handlers.py`)

**Purpose**: React to game events and notify players

**Responsibilities**:
- Subscribe to event bus
- Send appropriate messages to affected players
- Trigger animations
- Broadcast important events

**Handlers**:
```python
async def on_fleet_moved(event)       # Send movement animations
async def on_combat(event)            # Notify combatants
async def on_world_captured(event)    # Notify owner changes
async def on_production(event)        # Log production
async def on_player_joined(event)     # Broadcast player count
async def on_turn_processed(event)    # Send full updates
```

## Message Flow Examples

### Incoming Message Flow

```
Client sends: {"type": "command", "text": "F5W10"}
       ↓
WebSocketHandler.handle_connection()
       ↓
MessageRouter.route(player, raw_message)
       ↓
Parse JSON → Extract type="command"
       ↓
Call registered command handler
       ↓
Process command, validate, queue order
       ↓
Send response via MessageSender
```

### Outgoing Update Flow

```
Turn processes → Fleets move
       ↓
Publish FleetMovedEvent to event bus
       ↓
on_fleet_moved() handler receives event
       ↓
Find players who can observe movement
       ↓
MessageSender.send_animation() to each observer
       ↓
WebSocket sends JSON to client
```

### Delta Update Flow

```
Timer tick or game state change
       ↓
WebSocketHandler.send_update_to_all()
       ↓
MessageSender.send_delta_update(player)
       ↓
Build current state
Compare with player.last_state_snapshot
Calculate delta
       ↓
Send only changes to client
Update snapshot for next time
```

## Integration with Event Bus

### Event Publishers (Game Logic)
```python
from server.events.event_bus import get_event_bus
from server.events.event_types import FleetMovedEvent

event_bus = get_event_bus()

# When fleet moves
event = FleetMovedEvent(
    fleet_id=5,
    owner_id=player.id,
    owner_name=player.name,
    from_world=1,
    to_world=10,
    path=[1, 5, 10],
    ships=50,
    game_turn=game_turn
)
await event_bus.publish(event)
```

### Event Subscribers (WebSocket Handlers)
```python
# In events/handlers.py
@event_bus.subscribe("FLEET_MOVED")
async def on_fleet_moved(event):
    # Send animation to observers
    ws_handler = get_websocket_handler()
    sender = ws_handler.message_sender

    for observer in observers:
        await sender.send_animation(observer, {
            "animation_type": "fleet_movement",
            "fleet_id": event.fleet_id,
            "from_world": event.from_world,
            "to_world": event.to_world,
            "path": event.path,
            "duration": 2000
        })
```

## Benefits

### Separation of Concerns
✅ Connection management separate from message logic
✅ Incoming/outgoing message handling separate
✅ Event-driven updates don't pollute game logic

### Extensibility
✅ Easy to add new message types (register handler)
✅ Easy to add new event handlers (subscribe)
✅ Easy to add new message formats (add sender method)

### Maintainability
✅ Each component has clear responsibility
✅ Easy to test individual components
✅ Changes to one component don't affect others

### Performance
✅ Delta updates reduce bandwidth
✅ Timer ticks are lightweight
✅ Broadcasts are async and concurrent

### Robustness
✅ Error handling at each layer
✅ Safe message sending with exception catching
✅ Clean connection cleanup

## Usage in Main Server

```python
from server.websocket_handler import get_websocket_handler
from server.message_router import get_message_router
from server.events.handlers import register_all_handlers
import websockets

# Initialize
ws_handler = get_websocket_handler()
router = get_message_router()

# Register message handlers
async def handle_command(player, data):
    # Process command
    pass

router.register_handler("command", handle_command)

# Register event handlers
register_all_handlers()

# Start WebSocket server
async def main():
    async with websockets.serve(ws_handler.handle_connection, "0.0.0.0", 8765):
        await asyncio.Future()
```

## Adding New Features

### Adding Chat System
```python
# 1. Create message handler
async def handle_chat(player, data):
    message = data.get("message")
    to_player = data.get("to")

    # Send to recipient
    recipient = game_state.get_player_by_name(to_player)
    if recipient:
        await sender.send_chat(recipient, player.name, message, "private")

# 2. Register handler
router.register_handler("chat", handle_chat)

# 3. Client sends:
# {"type": "chat", "to": "Alice", "message": "Hello!"}
```

### Adding Alliance Updates
```python
# 1. Create event
class AllianceFormedEvent(GameEvent):
    def __init__(self, alliance_id, members, ...):
        ...

# 2. Create handler
async def on_alliance_formed(event):
    for member_name in event.members:
        member = game_state.get_player_by_name(member_name)
        await sender.send_alliance_update(member, {
            "alliance_id": event.alliance_id,
            "members": event.members
        })

# 3. Register handler
event_bus.subscribe("ALLIANCE_FORMED", on_alliance_formed)
```

## Testing

Each component can be tested independently:

```python
# Test connection manager
manager = ConnectionManager()
player = await manager.register(mock_websocket)
assert manager.get_connection_count() == 1

# Test message router
router = MessageRouter()
handler_called = False

async def test_handler(player, data):
    global handler_called
    handler_called = True

router.register_handler("test", test_handler)
await router.route(player, '{"type": "test"}')
assert handler_called

# Test message sender
sender = MessageSender()
await sender.send_info(player, "Test message")
```

## Next Steps

1. ✅ Connection management - DONE
2. ✅ Message routing - DONE
3. ✅ Message sending - DONE
4. ✅ Event handlers - DONE
5. 🔄 Integrate with existing server.py
6. ⏭️ Add more message handlers (chat, diplomacy, etc.)
7. ⏭️ Add more event types as needed
