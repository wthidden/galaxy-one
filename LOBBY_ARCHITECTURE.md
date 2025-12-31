# Lobby & Multi-Game Architecture Plan

## Overview
Transform StarWeb from single-game to multi-game architecture with authentication and lobby system.

## Current State
- Single game instance
- Players JOIN directly with `JOIN <name> [character_type]`
- No authentication
- No game selection

## Target State
- Multiple concurrent games
- Player accounts with authentication
- Lobby screen for game selection/creation
- Players can participate in multiple games

---

## Architecture Changes

### 1. Authentication System

**Player Accounts**
```python
class PlayerAccount:
    id: str (UUID)
    username: str (unique, 3-20 chars)
    password_hash: str (bcrypt)
    email: str (optional)
    created_at: datetime
    last_login: datetime
```

**Authentication Flow**
1. Client connects to websocket
2. Client sends LOGIN or SIGNUP message
3. Server validates credentials
4. Server returns auth token + player_id
5. Client stores token, transitions to lobby

**Security**
- Passwords hashed with bcrypt
- Session tokens (JWT or UUID-based)
- Token expiration (7 days)
- Rate limiting on auth attempts

### 2. Multi-Game Architecture

**Game Manager**
```python
class GameManager:
    games: Dict[str, Game]  # game_id -> Game

    def create_game(name, max_players, settings) -> Game
    def get_game(game_id) -> Game
    def list_games() -> List[Game]
    def delete_game(game_id)
```

**Game Model**
```python
class Game:
    id: str (UUID)
    name: str
    status: str  # "waiting", "active", "completed"
    created_at: datetime
    created_by: str (player_id)
    max_players: int (default 6)
    current_turn: int
    turn_end_time: float

    # Game settings
    map_size: int
    starting_resources: dict

    # The actual game state
    game_state: GameState

    # Player membership
    players: Dict[str, PlayerInGame]  # player_id -> PlayerInGame
```

**PlayerInGame**
```python
class PlayerInGame:
    player_id: str
    player_name: str  # in-game name
    character_type: str
    character_name: str (in-game display)
    joined_at: datetime
    last_active: datetime
    is_ready: bool  # for turn processing
    websocket: WebSocket
```

### 3. Message Routing

**Current**: All messages go to single game
**New**: Messages routed to specific game

```python
Message format:
{
    "type": "...",
    "game_id": "...",  # Required for game commands
    "data": {...}
}
```

**Message Types**
- **AUTH**: `LOGIN`, `SIGNUP`, `LOGOUT`
- **LOBBY**: `LIST_GAMES`, `CREATE_GAME`, `JOIN_GAME`, `LEAVE_GAME`
- **GAME**: All existing commands (MOVE, BUILD, etc.) - now include game_id

### 4. Persistence Changes

**Current**: Single `game_state.json`
**New**: Multiple files
- `accounts.json` - Player accounts
- `games/` directory
  - `{game_id}.json` - Individual game states
- `sessions.json` - Active sessions (or use Redis)

**Database Schema** (if using SQLite/PostgreSQL)
```sql
-- Player accounts
CREATE TABLE players (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Games
CREATE TABLE games (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    created_by TEXT REFERENCES players(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    current_turn INTEGER DEFAULT 0,
    max_players INTEGER DEFAULT 6,
    settings JSON
);

-- Player-Game membership
CREATE TABLE game_players (
    player_id TEXT REFERENCES players(id),
    game_id TEXT REFERENCES games(id),
    character_type TEXT NOT NULL,
    character_name TEXT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP,
    PRIMARY KEY (player_id, game_id)
);

-- Sessions (or use Redis)
CREATE TABLE sessions (
    token TEXT PRIMARY KEY,
    player_id TEXT REFERENCES players(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
```

---

## UI Changes

### 1. New Screens

**Login Screen** (`client/screens/LoginScreen.js`)
```
┌─────────────────────────────────┐
│         STARWEB                 │
│                                 │
│  Username: [____________]       │
│  Password: [____________]       │
│                                 │
│    [Login]  [Sign Up]          │
└─────────────────────────────────┘
```

**Lobby Screen** (`client/screens/LobbyScreen.js`)
```
┌────────────────────────────────────────────────────────────┐
│  STARWEB LOBBY                        Player: Alice  [Logout]
├────────────────────────────────────────────────────────────┤
│                                                             │
│  My Games                                   [Create Game]  │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Game Name      Turn  Players  Status     [Enter]     │ │
│  │────────────────────────────────────────────────────  │ │
│  │ Alpha Sector    12    4/6     Active    [Enter >]   │ │
│  │ Beta Quadrant   5     3/6     Active    [Enter >]   │ │
│  │ New Stars       0     1/6     Waiting   [Enter >]   │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  Available Games to Join                                   │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Game Name      Turn  Players  Status     [Join]      │ │
│  │────────────────────────────────────────────────────  │ │
│  │ Gamma Wars      8     5/6     Active    [Join >]    │ │
│  │ Delta Empire    2     2/6     Waiting   [Join >]    │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  Game Details: Alpha Sector                                │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Turn: 12          Created: 2 days ago                │ │
│  │ Players: 4/6      Status: Active                     │ │
│  │                                                       │ │
│  │ Scoreboard:                                          │ │
│  │   1. Alice (Berserker)        245 pts               │ │
│  │   2. Bob (Empire Builder)     198 pts               │ │
│  │   3. Carol (Merchant)         156 pts               │ │
│  │   4. Dave (Pirate)            142 pts               │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

**Create Game Modal**
```
┌─────────────────────────────────┐
│   Create New Game               │
├─────────────────────────────────┤
│                                 │
│  Game Name: [____________]      │
│                                 │
│  Max Players: [6 ▼]            │
│                                 │
│  Map Size: [100 ▼]             │
│                                 │
│  Your Character:                │
│    ( ) Empire Builder           │
│    ( ) Merchant                 │
│    ( ) Pirate                   │
│    ( ) Artifact Collector       │
│    ( ) Berserker                │
│    ( ) Apostle                  │
│                                 │
│  Character Name: [________]     │
│                                 │
│    [Cancel]  [Create]          │
└─────────────────────────────────┘
```

### 2. Screen Flow

```
App.js
  ├─ LoginScreen (if not authenticated)
  ├─ LobbyScreen (if authenticated, no game selected)
  └─ GameScreen (if authenticated + game selected)
       └─ Existing game UI
```

### 3. State Management

```javascript
// App-level state
{
    auth: {
        isAuthenticated: bool,
        playerId: string,
        username: string,
        token: string
    },

    lobby: {
        myGames: Array<GameInfo>,
        availableGames: Array<GameInfo>,
        selectedGame: GameInfo | null
    },

    currentGame: {
        gameId: string,
        gameState: {...},  // Existing game state
        ...
    }
}
```

---

## Implementation Phases

### Phase 1: Authentication Backend (Priority: HIGH)
**Files to create/modify:**
- `server/auth/` (new directory)
  - `auth_manager.py` - Authentication logic
  - `password_utils.py` - Hashing/verification
  - `session_manager.py` - Token management
- `server/persistence/accounts.py` - Account storage
- Modify: `server/server.py` - Add auth message handlers

**Tasks:**
1. Create PlayerAccount model
2. Implement password hashing (bcrypt)
3. Create signup/login handlers
4. Session token generation/validation
5. Store accounts to disk (JSON for now)

### Phase 2: Multi-Game Backend (Priority: HIGH)
**Files to create/modify:**
- `server/game_manager.py` - Manages multiple games
- `server/game_instance.py` - Wrapper for Game + GameState
- Modify: `server/game/state.py` - Make GameState instance-scoped
- Modify: `server/server.py` - Route messages to correct game
- Modify: `server/persistence/` - Save/load multiple games

**Tasks:**
1. Create GameManager class
2. Create Game model
3. Update message routing
4. Update persistence for multi-game
5. Handle game creation/joining/leaving

### Phase 3: Lobby Backend (Priority: MEDIUM)
**Files to create/modify:**
- `server/lobby/` (new directory)
  - `lobby_manager.py` - Lobby operations
  - `lobby_handlers.py` - Message handlers
- Modify: `server/server.py` - Add lobby endpoints

**Tasks:**
1. LIST_GAMES handler
2. CREATE_GAME handler
3. JOIN_GAME handler
4. LEAVE_GAME handler
5. GET_GAME_INFO handler

### Phase 4: Login UI (Priority: HIGH)
**Files to create:**
- `client/screens/LoginScreen.js`
- `client/auth/AuthManager.js`

**Tasks:**
1. Create login form UI
2. Create signup form UI
3. Implement auth message sending
4. Store auth token in localStorage
5. Handle auth errors

### Phase 5: Lobby UI (Priority: MEDIUM)
**Files to create:**
- `client/screens/LobbyScreen.js`
- `client/lobby/GameList.js`
- `client/lobby/GameDetails.js`
- `client/lobby/CreateGameModal.js`

**Tasks:**
1. Game list display (my games)
2. Game list display (available games)
3. Game details panel
4. Create game modal
5. Join/Enter game actions

### Phase 6: Integration (Priority: HIGH)
**Files to modify:**
- `client/main.js` - Screen routing
- `client/App.js` - State management
- `index.html` - Include new screen files

**Tasks:**
1. App-level state management
2. Screen routing logic
3. WebSocket reconnection handling
4. Game switching without full reload

### Phase 7: Testing & Polish (Priority: MEDIUM)
**Tasks:**
1. Test auth flow (signup, login, logout)
2. Test game creation and joining
3. Test multi-game scenarios
4. Error handling and validation
5. UI polish and responsive design

---

## Migration Strategy

### For Existing Players
- Auto-create accounts for existing players
- Migrate existing game to "Legacy Game"
- Generate temp passwords, email to players

### Backward Compatibility
- Keep existing JOIN command for testing
- Support both old and new flows during transition
- Deprecation warnings in old flow

---

## Security Considerations

1. **Password Security**
   - bcrypt with salt rounds >= 10
   - Minimum password length: 8 characters
   - No password stored in plain text

2. **Session Security**
   - Tokens expire after 7 days
   - Invalidate on logout
   - HTTPS in production

3. **Input Validation**
   - Username: alphanumeric + underscore, 3-20 chars
   - Prevent SQL injection (use parameterized queries)
   - Rate limit auth attempts

4. **Data Privacy**
   - Player emails not shared
   - Game visibility controls (public/private games)

---

## Future Enhancements

1. **Game Settings**
   - Custom map sizes
   - Victory conditions
   - Time limits
   - Private games (invite-only)

2. **Social Features**
   - Friend lists
   - Game invites
   - Chat in lobby

3. **Statistics**
   - Win/loss records
   - Total games played
   - Average score
   - Achievements

4. **Game Replays**
   - View completed games
   - Turn-by-turn playback

5. **Admin Panel**
   - Manage games
   - Manage players
   - View statistics
