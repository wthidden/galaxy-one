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

**Syntax:** `W<world_id>I<amount>L`

**Cost:** 5 industry + 5 metal per 1 limit increase (4 for Empire Builders)

**Examples:**
- `W3I2L` - Increase limit by 2 at world 3
- `W3I5L` - Increase limit by 5 at world 3

**UI Feedback:**
- 📈 Icon in queued orders (green border)
- Order text: "Increase population limit by 2 at W3"

**Validation:**
- World must be owned by you
- Requires 5 industry + 5 metal per increase (4+4 for Empire Builders)

---

### 3F. Build Industry

**Syntax:** `W<world_id>I<amount>I`

**Cost:** 5 industry + 5 metal per 1 industry (4 for Empire Builders)

**Examples:**
- `W3I2I` - Build 2 industry at world 3
- `W150I1I` - Build 1 industry at world 150

**UI Feedback:**
- 🏭 Icon in queued orders (green border)
- Order text: "Build 2 industry on W3"

**Validation:**
- World must be owned by you
- Empire Builders need 4 industry per build, others need 5
- Requires 5 metal per industry built

---

### 3G. Build Robots (Berserkers Only)

**Syntax:** `W<world_id>B<amount>R`

**Cost:** 1 industry = 2 robots

**Examples:**
- `W3B10R` - Build 20 robots (10 industry) at world 3
- `W3B5R` - Build 10 robots (5 industry) at world 3

**UI Feedback:**
- 🤖 Icon in queued orders (green border)
- Order text: "Build 10 robots on W3"

**Validation:**
- Only Berserkers can build robots
- Limited by industry available

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

**Syntax:** `F<fleet_id>A<target>` or `I<iship_count>A<target>` or `P<pship_count>A<target>`

**Targets:**
- `I` - Fire at ISHIPS (then industry if ISHIPS destroyed)
- `P` - Fire at PSHIPS (then population if PSHIPS destroyed)
- `H` - Fire at HOME fleets (to neutralize world)
- `C` - Fire at CONVERTS (Apostle converts on world)

**Examples:**
- `F5AI` - Fleet 5 fires at world ISHIPS/industry
- `F5AP` - Fleet 5 fires at world PSHIPS/population
- `F5AH` - Fleet 5 fires at homeworld fleets
- `I10AC` - 10 ISHIPS fire at converts
- `P10AC` - 10 PSHIPS fire at converts

**UI Feedback:**
- 💥 Icon in queued orders (red border)
- Crosshairs and target circles on map
- Target type labeled
- Order text: "F5 Fire at ISHIPS (then industry)"

**Validation:**
- Fleet must exist and be owned by you
- Fleet must have ships
- Cannot have other exclusive orders on same fleet

**Combat Resolution:**
- Ships fire at defensive ships first
- Remaining shots damage the specified target
- Damages your score if you kill population

**Target-Specific Behavior:**
- **I target**: Fires at ISHIPS, then remaining shots hit industry
- **P target**: Fires at PSHIPS, then remaining shots hit population
- **H target**: Fires at all fleets at homeworld to make it neutral
- **C target**: Fires at converts (reduces convert population)

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

## 11. CONDITIONAL FIRE - Defensive Fire

**Syntax:** `F<fleet_id>C<target>` or `F<fleet_id>CF<target_fleet_id>`

**Examples:**
- `F5CF10` - Fleet 5 conditional fires at fleet 10 (only if attacked)
- `F5CI` - Fleet 5 conditional fires at ISHIPS (only if attacked)

**UI Feedback:**
- 🛡️ Icon in queued orders (red border with shield)
- Order text: "F5 Conditional Fire at F10"

**Validation:**
- Fleet must exist and be owned by you
- Cannot have other exclusive orders (MOVE, FIRE, AMBUSH)
- Target validation same as regular FIRE

**Combat Resolution:**
- Fleet only fires if attacked first
- Used for defensive positioning
- Cannot be combined with MOVE orders

**Notes:**
- Defensive strategy: set conditional fire without committing to attack
- Good for border defense without appearing aggressive
- Executes during combat phase only if you're attacked

---

## 12. NO AMBUSH - Disable Ambush

**Syntax:** `Z` or `Z<world_id>`

**Examples:**
- `Z` - Don't ambush anyone, anywhere this turn
- `Z10` - Don't ambush at world 10

**UI Feedback:**
- 🚫 Icon in queued orders
- Order text: "Don't ambush anyone, anywhere" or "Don't ambush at W10"

**Validation:**
- World must exist if specified

**Notes:**
- Use `Z` to prevent automatic ambushing anywhere
- Use `Z#` to allow ambushes everywhere except one world
- Useful for diplomacy or selective engagement

---

## 13. PEACE STATUS - Fleet Combat Control

### 13A. At Peace

**Syntax:** `F<fleet_id>Q`

**Examples:**
- `F5Q` - Put fleet 5 at peace

**UI Feedback:**
- ☮️ Icon in queued orders
- Order text: "F5 at peace (won't participate in combat)"

**Validation:**
- Fleet must exist and be owned by you

**Effect:**
- Fleet won't participate in any combat
- Useful for safe passage or retreat
- Can move through hostile territory

### 13B. Not At Peace

**Syntax:** `F<fleet_id>X`

**Examples:**
- `F5X` - Put fleet 5 not at peace (will fight)

**UI Feedback:**
- ⚔️ Icon in queued orders
- Order text: "F5 not at peace (will participate in combat)"

**Validation:**
- Fleet must exist and be owned by you

**Effect:**
- Fleet will participate in combat normally
- Reverses peace status
- Default state for all fleets

---

## 14. GIFT COMMANDS - Transfer Ownership

### 14A. Gift Fleet

**Syntax:** `F<fleet_id>G=<player_name>`

**Examples:**
- `F5G=Alice` - Gift fleet 5 to player Alice
- `F10G=Bob` - Gift fleet 10 to player Bob

**UI Feedback:**
- 🎁 Icon in queued orders
- Order text: "Gift F5 to player 'Alice'"

**Validation:**
- Fleet must exist and be owned by you
- Target player must exist in game
- Cannot gift to yourself

**Effect:**
- Fleet transfers to target player immediately
- All ships and cargo transfer
- Strategic diplomacy or alliance support

### 14B. Gift World

**Syntax:** `W<world_id>G=<player_name>`

**Examples:**
- `W10G=Alice` - Gift world 10 to player Alice

**UI Feedback:**
- 🎁 Icon in queued orders
- Order text: "Gift W10 to player 'Alice'"

**Validation:**
- World must exist and be owned by you
- Cannot gift your homeworld
- Target player must exist in game
- Cannot gift to yourself

**Effect:**
- World and all resources transfer
- All industry, metal, population transfers
- ISHIPS and PSHIPS transfer
- Powerful diplomatic tool

---

## 15. PLANET BUSTER BOMB - Ultimate Weapon

### 15A. Build PBB

**Syntax:** `F<fleet_id>B`

**Examples:**
- `F5B` - Build Planet Buster Bomb on fleet 5

**Requirements:**
- Fleet must have 25+ ships
- Fleet cannot already have a PBB

**UI Feedback:**
- 💣 Icon in queued orders
- Order text: "Build Planet Buster Bomb on F5"

**Validation:**
- Fleet must exist and be owned by you
- Fleet must have at least 25 ships
- Fleet cannot already have a PBB

**Effect:**
- Fleet gains Planet Buster Bomb capability
- Can destroy entire worlds
- Major strategic weapon

### 15B. Drop PBB

**Syntax:** `F<fleet_id>D`

**Examples:**
- `F5D` - Drop PBB from fleet 5, destroying current world

**UI Feedback:**
- 💥 Icon in queued orders (red)
- Order text: "Drop Planet Buster Bomb from F5"

**Validation:**
- Fleet must have a PBB
- Cannot drop on homeworlds (protected)

**Effect:**
- Destroys the entire world
- All industry, metal, population destroyed
- World becomes uninhabitable
- Massive score penalty

**Notes:**
- Use sparingly - destroys strategic resources
- Cannot target homeworlds (game rule)
- PBB is consumed after use

---

## 16. ROBOT ATTACK - Berserker Special

**Syntax:** `F<fleet_id>R<amount>`

**Examples:**
- `F5R20` - Convert ships to 20 robots for attack

**Cost:** 1 ship = 2 robots

**UI Feedback:**
- 🤖⚔️ Icon in queued orders
- Order text: "Convert 20 robots from F5 for attack"

**Validation:**
- Only Berserkers can use this command
- Fleet must have enough ships

**Effect:**
- Ships convert to robots (1:2 ratio)
- Robots used for ground assault
- Berserker gets points for killing population

---

## 17. MIGRATE CONVERTS - Apostle Special

**Syntax:** `C<source_world_id>M<amount>W<dest_world_id>`

**Examples:**
- `C3M5W10` - Migrate 5 converts from world 3 to world 10

**UI Feedback:**
- ✝️👥 Icon in queued orders
- Order text: "Migrate 5 converts from W3 to W10"

**Validation:**
- Only Apostles can migrate converts
- World must be owned by you
- Worlds must be connected
- Must have enough converts

**Effect:**
- Transfers Apostle converts to connected world
- Can capture worlds with converts
- Spreads religious influence

---

## 18. DIPLOMACY COMMANDS

### 18A. Declare Ally

**Syntax:** `A=<player_name>`

**Examples:**
- `A=Alice` - Declare Alice as ally

**UI Feedback:**
- 🤝 Icon in queued orders
- Order text: "Declare 'Alice' as ally"

**Validation:**
- Player must exist
- Cannot declare yourself

**Effect:**
- Diplomatic status change
- May affect combat and movement
- Public declaration

### 18B. Declare Non-Ally

**Syntax:** `N=<player_name>`

**Examples:**
- `N=Bob` - Declare Bob as non-ally

**Effect:**
- Revokes ally status
- Returns to neutral status

### 18C. Declare Loader

**Syntax:** `L=<player_name>`

**Examples:**
- `L=Alice` - Allow Alice to load metal from your worlds

**Effect:**
- Allows specified player to load cargo from your worlds
- Economic cooperation
- Trust-based agreement

### 18D. Revoke Loader

**Syntax:** `X=<player_name>`

**Examples:**
- `X=Bob` - Revoke Bob's loader status

**Effect:**
- Player can no longer load from your worlds

### 18E. Declare Jihad (Apostle Only)

**Syntax:** `J=<player_name>`

**Examples:**
- `J=Alice` - Declare Jihad against Alice

**Validation:**
- Only Apostles can declare Jihad
- Cannot target yourself

**Effect:**
- Religious war declaration
- Converts fight with bonuses
- Major diplomatic action

---

## 19. TURN - End Your Turn

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

1. **DIPLOMACY** - All ally/loader/jihad declarations
2. **GIFT** - Fleet and world transfers
3. **TRANSFER** - All ship/cargo transfers execute
4. **BUILD** - All builds execute (ships, industry, limits, robots, PBB)
5. **MIGRATE** - All population migrations execute (including converts)
6. **FIRE** - All combat resolves (fire, conditional fire, robot attacks)
7. **AMBUSH** - Ambush flags are set
8. **PEACE STATUS** - At peace/not at peace flags updated
9. **MOVE** - All movements execute (may trigger ambushes)
10. **PBB DROP** - Planet Buster Bombs detonate
11. **Production** - Worlds produce metal and population grows
12. **Captures** - Empty fleets and undefended worlds change ownership

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
- ✝️👥 **Cyan border** - Migrate converts (Apostle)
- 📦 **Orange border** - Transfer orders
- ⚔️💥 **Red border** - Fire orders
- 🛡️ **Red border with shield** - Conditional fire
- 🎯 **Purple border** - Ambush orders
- 🚫 **Gray border** - No ambush
- ☮️ **White border** - At peace
- ⚔️ **Red border** - Not at peace
- 🎁 **Yellow border** - Gift orders
- 💣 **Red border** - Build PBB
- 💥 **Red border** - Drop PBB
- 🤖⚔️ **Red border** - Robot attack
- 🤝 **Blue border** - Diplomacy

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
   - Industry costs 5:5:5 industry+metal (4:4 for Empire Builders)
   - Population limit costs 5:5 industry+metal (4:4 for Empire Builders)
   - Robots cost 1 industry = 2 robots (Berserkers only)
7. **Exclusive orders** - Each fleet can only have one of: MOVE, FIRE, AMBUSH, or CONDITIONAL_FIRE per turn
8. **Transfer before moving** - Transfer orders execute before moves, so you can load a fleet then move it
9. **Migrate wisely** - Only way to increase population besides growth; gives visibility of destination
10. **Empire Builder advantage** - Needs only 4 industry (vs 5) for building industry and increasing limits
11. **Fire target types** - Use specific targets (I/P/H/C) to focus fire on ISHIPS, PSHIPS, home fleets, or converts
12. **Conditional fire for defense** - Set conditional fire to automatically respond if attacked without appearing aggressive
13. **Peace status for safe passage** - Put fleets at peace (FnnnQ) to move through hostile territory safely
14. **Gift strategically** - Use gifts to support allies or form partnerships
15. **PBB is ultimate weapon** - Planet Buster Bombs destroy worlds but cannot target homeworlds
16. **Character-specific commands**:
    - Berserkers: Build/attack with robots
    - Apostles: Migrate converts, declare Jihad
    - Merchants: 2x cargo capacity
    - Pirates: Plunder worlds
17. **Diplomacy matters** - Use ally/loader declarations to build trust and cooperation
18. **No ambush for peace** - Use Z or Z# to selectively disable ambushes for diplomatic purposes

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
