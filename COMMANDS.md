# StarWeb Commands Reference

This document lists all supported commands in the StarWeb game, their syntax, and visual feedback.

## Command Format

All commands are case-insensitive and follow these patterns:

---

## 1. JOIN - Join the Game

**Syntax:** `JOIN <name> [score_vote] [character_type]`

**Examples:**
- `JOIN Alice` - Join with default settings
- `JOIN Bob 8000` - Join and vote for 8000 end score
- `JOIN Carol 8000 Merchant` - Join as Merchant character type

**Character Types:**
- Empire Builder
- Merchant
- Pirate
- Artifact Collector
- Berserker
- Apostle

**UI Feedback:**
- Welcome message in event log
- Your name appears in scoreboard
- Homeworld appears on map

---

## 2. MOVE - Move Fleet

**Syntax:** `F<fleet_id>W<world_id>[W<world_id>...]`

**Examples:**
- `F5W10` - Move fleet 5 to world 10
- `F5W1W3W10` - Move fleet 5 via path: 1 → 3 → 10

**UI Feedback:**
- 🚀 Icon in queued orders (blue border)
- Blue dashed arrow on map from origin to destination
- Animated triangle shows fleet moving along path
- Order text: "Move F5 -> W10"

**Validation:**
- Fleet must exist and be owned by you
- Worlds must be connected
- Cannot have other exclusive orders (FIRE, AMBUSH) on same fleet

---

## 3. BUILD - Build Ships and Infrastructure

### 3A. Build IShips (Defensive Ships)

**Syntax:** `W<world_id>B<amount>I`

**Cost:** 1 industry + 1 metal + 1 population = 1 IShip

**Examples:**
- `W3B25I` - Build 25 IShips at world 3
- `W150B10I` - Build 10 IShips at world 150

**UI Feedback:**
- 🔵 Icon in queued orders (green border)
- Construction icon on map at the world
- Order text: "Build 25 IShips at W3"

**Validation:**
- World must be owned by you
- Limited by min(industry, metal, population)

---

### 3B. Build PShips (Population Defense Ships)

**Syntax:** `W<world_id>B<amount>P`

**Cost:** 1 industry + 1 metal + 1 population = 1 PShip

**Examples:**
- `W3B10P` - Build 10 PShips at world 3
- `W150B10P` - Build 10 PShips at world 150

**UI Feedback:**
- 🟢 Icon in queued orders (green border)
- Construction icon on map at the world
- Order text: "Build 10 PShips at W3"

**Validation:**
- World must be owned by you
- Limited by min(industry, metal, population)

---

### 3C. Build Ships into Fleet

**Syntax:** `W<world_id>B<amount>F<fleet_id>`

**Cost:** 1 industry + 1 metal + 1 population = 1 ship

**Examples:**
- `W3B15F7` - Build 15 ships into fleet 7 at world 3

**UI Feedback:**
- 🏗️ Icon in queued orders (green border)
- Order text: "Build 15 F7 at W3"

**Validation:**
- World must be owned by you
- Fleet must be at the same world
- Fleet must be owned by you

---

### 3D. Build Industry

**Syntax:** `W<world_id>B<amount>INDUSTRY` or `W<world_id>B<amount>IND`

**Cost:** 5 industry + 5 metal + 5 population = 1 industry (4 industry for Empire Builders)

**Examples:**
- `W3B2INDUSTRY` - Build 2 industry at world 3
- `W3B1IND` - Build 1 industry at world 3

**UI Feedback:**
- 🏭 Icon in queued orders (green border)
- Order text: "Build 2 Industry at W3"

**Validation:**
- World must be owned by you
- Empire Builders need 4 industry per build, others need 5
- Requires 5 metal and 5 population per industry built

---

### 3E. Increase Population Limit

**Syntax:** `W<world_id>B<amount>LIMIT` or `W<world_id>B<amount>L`

**Cost:** 5 industry per 1 limit increase (4 for Empire Builders)

**Examples:**
- `W3B2LIMIT` - Increase limit by 2 at world 3
- `W3B5L` - Increase limit by 5 at world 3

**UI Feedback:**
- 📈 Icon in queued orders (green border)
- Order text: "Build 2 Pop Limit at W3"

**Validation:**
- World must be owned by you
- Empire Builders need 4 industry per limit, others need 5

---

### 3F. Build Robots (Berserkers Only)

**Syntax:** `W<world_id>B<amount>ROBOT` or `W<world_id>B<amount>R`

**Cost:** 1 industry + 1 metal = 2 robots

**Examples:**
- `W3B10ROBOT` - Build 20 robots (10 industry) at world 3
- `W3B5R` - Build 10 robots (5 industry) at world 3

**UI Feedback:**
- 🤖 Icon in queued orders (green border)
- Order text: "Build 20 Robots at W3"

**Validation:**
- Only Berserkers can build robots
- World must have robot population (cannot build robots at human worlds)
- Limited by min(industry, metal)

**Notes:**
- Berserkers get points for killing population with robots
- Robots count as population for running industry

---

## 4. TRANSFER - Transfer Cargo

**Syntax:** `F<fleet_id>T<amount><target>`

**Targets:**
- `I` - Transfer to world IShips
- `P` - Transfer to world PShips
- `F<fleet_id>` - Transfer to another fleet

**Examples:**
- `F5T10I` - Transfer 10 ships from fleet 5 to world IShips
- `F5T10P` - Transfer 10 ships from fleet 5 to world PShips
- `F5T10F7` - Transfer 10 ships from fleet 5 to fleet 7

**UI Feedback:**
- 📦 Icon in queued orders (orange border)
- Package icon on map at fleet location
- Amount displayed below icon
- Order text: "Transfer 10 from F5 to I"

**Validation:**
- Fleet must exist and be owned by you
- Fleet must have enough ships to transfer
- For world transfers (I/P), you must own the world
- For fleet transfers, target fleet must be at same location

---

## 5. LOAD - Load Cargo onto Fleet

**Syntax:** `F<fleet_id>L[amount]`

**Examples:**
- `F5L` - Load maximum cargo onto fleet 5
- `F5L10` - Load 10 population onto fleet 5

**Cargo Capacity:**
- **Regular players**: 1 population per ship
- **Merchants**: 2 population per ship (double capacity)

**UI Feedback:**
- 📥 Icon in queued orders (cyan border)
- Load icon on map at fleet location
- Order text: "F5 Load Max" or "F5 Load 10"

**Validation:**
- Fleet must exist and be owned by you
- World must be owned by you
- Limited by: min(available cargo space, world population)

**Notes:**
- Cargo is population being transported by the fleet
- Loaded population is removed from the world
- Use UNLOAD to offload cargo at destination
- Merchants can carry twice as much (2 pop per ship vs 1 pop per ship)

---

## 6. UNLOAD - Unload Cargo from Fleet

**Syntax:** `F<fleet_id>U[amount]`

**Examples:**
- `F5U` - Unload all cargo from fleet 5
- `F5U10` - Unload 10 population from fleet 5

**UI Feedback:**
- 📤 Icon in queued orders (cyan border)
- Unload icon on map at fleet location
- Order text: "F5 Unload All" or "F5 Unload 10"

**Validation:**
- Fleet must exist and be owned by you
- World must be owned by you
- Fleet must have cargo to unload
- Limited by: world's remaining population capacity (limit - current population)

**Notes:**
- Unloaded population is added to the world
- Cannot exceed world's population limit
- Use LOAD/UNLOAD to transport population between worlds via fleets

---

## 7. MIGRATE - Move Population

**Syntax:** `W<world_id>M<amount>W<dest_world_id>`

**Cost:** 1 industry + 1 metal = move 1 population

**Examples:**
- `W3M5W10` - Migrate 5 population from world 3 to world 10
- `W150M10W151` - Migrate 10 population from world 150 to 151

**UI Feedback:**
- 👥 Icon in queued orders (cyan border)
- Cyan dashed arrow on map from origin to destination
- Population icon and amount at midpoint
- Order text: "Migrate 5 population from W3 to W10"

**Validation:**
- World must be owned by you
- Destination must be connected (adjacent via gate)
- Limited by min(industry, metal, population)

**Notes:**
- This is the ONLY way to increase population at a world besides natural growth
- Migrating gives you visibility of the destination world
- Can only migrate to ONE world from any given world per turn
- Cannot give away world or fire with IShips/PShips on same turn you migrate
- You CAN migrate TO a world from all its adjacent worlds
- If population alternates (not enough to run both mines and industry), migration still works

**Special Cases:**
- **Converts**: Special order needed (not yet implemented)
- **Robots (Berserkers)**: Migrating robots to a human world kills humans and gives points
- **Capturing**: Migrating converts or robots can capture worlds if you meet requirements

---

## 8. FIRE AT WORLD - Attack World Installations

**Syntax:** `F<fleet_id>A<target>`

**Targets:**
- `P` - Fire at population
- `I` - Fire at industry

**Examples:**
- `F5AP` - Fleet 5 fires at world population
- `F5AI` - Fleet 5 fires at world industry

**UI Feedback:**
- 💥 Icon in queued orders (red border)
- Crosshairs and target circles on map
- Target type (P or I) labeled
- Order text: "F5 Fire at World P"

**Validation:**
- Fleet must exist and be owned by you
- Fleet must have ships
- Cannot have other exclusive orders on same fleet

**Combat Resolution:**
- Ships fire at defensive ships first (PShips for population, IShips for industry)
- Remaining shots damage population or industry
- Damages your score if you kill population

---

## 9. FIRE AT FLEET - Attack Enemy Fleet

**Syntax:** `F<fleet_id>AF<target_fleet_id>`

**Examples:**
- `F5AF10` - Fleet 5 fires at fleet 10

**UI Feedback:**
- ⚔️ Icon in queued orders (red border)
- Combat icon on map
- Order text: "F5 Fire at F10"

**Validation:**
- Both fleets must exist
- Attacking fleet must be owned by you
- Both fleets must be at same world
- Cannot have other exclusive orders on attacking fleet

**Combat Resolution:**
- Each side's ships fire at opponent
- Casualties calculated: ceil(enemy_ships / 2) per side
- Both fleets take damage simultaneously

---

## 10. AMBUSH - Set Fleet to Ambush

**Syntax:** `F<fleet_id>A`

**Examples:**
- `F5A` - Fleet 5 sets ambush

**UI Feedback:**
- 🎯 Icon in queued orders (purple border)
- Pulsing purple circle on map at fleet location
- Order text: "F5 Ambush"

**Validation:**
- Fleet must exist and be owned by you
- Cannot have other exclusive orders on same fleet

**Ambush Resolution:**
- Fleet waits for enemy fleets to arrive
- When enemy fleet moves to this world, ambush triggers
- Ambushing fleet gets 2x attack bonus
- Enemy takes damage but ambusher doesn't
- Stops enemy fleet immediately (doesn't complete multi-hop moves)

---

## 11. TURN - End Your Turn

**Syntax:** `TURN`

**UI Feedback:**
- "End Turn" button shows remaining players
- Tooltip shows who hasn't ended their turn yet
- Checkmarks appear next to ready players in scoreboard
- Message: "You have ended your turn. Waiting for others..."

**When Everyone is Ready:**
- Turn processes immediately (don't wait for timer)
- All orders execute
- New turn begins
- Timer resets

---

## Order Execution Priority

When the turn processes, orders execute in this order:

1. **TRANSFER** - All transfers execute first
2. **BUILD** - All builds execute (ships, industry, limits, robots)
3. **MIGRATE** - All population migrations execute
4. **FIRE** - All combat resolves
5. **AMBUSH** - Ambush flags are set
6. **MOVE** - All movements execute (may trigger ambushes)
7. **Production** - Worlds produce metal and population grows
8. **Captures** - Empty fleets and undefended worlds change ownership

---

## Visual Legend

### Queued Orders Panel
- 🚀 **Blue border** - Move orders
- 🔵 **Green border** - Build IShips
- 🟢 **Green border** - Build PShips
- 🏭 **Green border** - Build Industry
- 📈 **Green border** - Increase Population Limit
- 🤖 **Green border** - Build Robots
- 🏗️ **Green border** - Build to Fleet
- 👥 **Cyan border** - Migrate population
- 📦 **Orange border** - Transfer orders
- ⚔️💥 **Red border** - Fire orders
- 🎯 **Purple border** - Ambush orders

### Map Indicators
- **Blue dashed arrow** - Planned fleet movement
- **Animated triangle** - Fleet in motion
- **Cyan dashed arrow + 👥** - Population migration with amount
- **Pulsing purple circle** - Fleet on ambush
- **Crosshairs + target** - Fire at world order
- **⚔️ icon** - Fire at fleet order
- **🏗️ icon + badge** - Build order with amount
- **📦 icon + number** - Transfer order with amount

### Color Coding
- **Yellow** - Fleet references (F5)
- **Blue** - World references (W10)
- **Green** - Amounts and build targets
- **Orange** - Resource types (I, P)

---

## Command Parser Features

The command parser provides:

1. **Auto-completion** - Shows available fleets/worlds as you type
2. **Validation** - Real-time error checking
3. **Suggestions** - Helpful hints when commands are invalid
4. **History** - Arrow keys to recall previous commands
5. **Tab completion** - Tab to accept suggestions

### Keyboard Shortcuts
- **↑ / ↓** - Navigate command history
- **Tab** - Accept current suggestion
- **Esc** - Close suggestions
- **Enter** - Send command

---

## Tips

1. **Queue multiple orders** - You can queue many orders before ending your turn
2. **Cancel orders** - Click the ✕ button next to any queued order to cancel it
3. **Check ownership** - Validation checks ensure you own what you're commanding
4. **Plan paths** - Move commands can specify multi-world paths
5. **Watch for ambushes** - Look for pulsing purple circles on enemy worlds
6. **Build strategically**:
   - IShips/PShips cost 1:1:1 (industry:metal:population)
   - Industry costs 5:5:5 (4:5:5 for Empire Builders)
   - Population limit costs only industry (5 per limit, 4 for Empire Builders)
   - Robots cost 1:1 and produce 2 robots (Berserkers only)
7. **Exclusive orders** - Each fleet can only have one of: MOVE, FIRE, or AMBUSH per turn
8. **Transfer before moving** - Transfer orders execute before moves, so you can load a fleet then move it
9. **Migrate wisely** - Only way to increase population besides growth; gives visibility of destination
10. **Empire Builder advantage** - Needs only 4 industry (vs 5) for building industry and increasing limits

---

## Error Messages

Common errors and what they mean:

- **"Fleet already has an exclusive order"** - Can't have MOVE + FIRE, MOVE + AMBUSH, or FIRE + AMBUSH on same fleet
- **"Invalid fleet"** - Fleet doesn't exist or you don't own it
- **"Invalid world"** - World doesn't exist or you don't own it
- **"Both fleets must be at the same world"** - For transfers and firing between fleets
- **"Not enough resources"** - Build requires more industry/metal/population than available
- **"Not enough ships"** - Transfer requires more ships than fleet has

---

## Advanced Tactics

### Convoy System
1. Build ships at homeworld: `W1B50F10`
2. Move loaded fleet: `F10W5`
3. Transfer to destination: `F10T50I`

### Ambush Defense
1. Set ambush: `F5A`
2. Enemy fleet moving to your world gets hit with 2x damage
3. Their movement stops immediately

### Coordinated Attack
1. Multiple fleets fire at same target
2. All fire orders execute simultaneously
3. Can overwhelm defenses quickly

### Resource Chain
1. Transfer ships to world IShips: `F5T10I`
2. Build more at that world: `W3B20I`
3. Move reinforcements: `F5W10`
