# StarWeb Player Manual

**Last Updated: December 2025**

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [User Interface](#user-interface)
   - [Keyboard Shortcuts](#keyboard-shortcuts)
4. [Game Concepts](#game-concepts)
5. [Commands Reference](#commands-reference)
6. [Game Mechanics](#game-mechanics)
7. [Character Types](#character-types)
8. [Victory Conditions](#victory-conditions)
9. [Tips & Strategy](#tips--strategy)

---

## Introduction

**StarWeb** is a multiplayer space strategy game where you command fleets, conquer worlds, and compete for galactic dominance. Build your empire through exploration, industry, combat, and artifact collection.

### Core Gameplay
- **Turn-based**: All players submit orders each turn
- **Real-time**: Turns advance on a timer or when all players are ready
- **Strategic**: Balance expansion, economy, military, and exploration
- **Competitive**: First player to reach the target score wins
- **Asymmetric**: Each of the 6 character types has different victory conditions and special powers!

---

## Getting Started

### Joining a Game

**Command Format:** `JOIN <name> [turn_timer_minutes] [character_type]`

**Examples:**
```
JOIN Alice EmpireBuilder               - Use defaults (60 min timer)
JOIN Bob 30 Pirate                     - 30 minute preferred turn time
JOIN Carol 120 ArtifactCollector       - 2 hour preferred turn time
```

**Parameters:**
- `name`: Your player name
- `turn_timer_minutes` (optional): Your preferred minimum time between turns (5-1440 minutes, default: 60)
  - The actual turn duration will be the **average** of all players' preferences
  - Or turns advance when all players press TURN (whichever comes first)
- `character_type` (optional): One of: Empire Builder, Merchant, Pirate, ArtifactCollector, Berserker, Apostle (default: EmpireBuilder)

### First Steps

When you join, you'll start with:
- **1 Home World** (numbered world, not named)
- **Initial resources** on your home world
- **5 Fleets** at your home world
- **Connected worlds** to explore

**Your first turn should focus on:**
1. Survey your home world's resources
2. Check connected worlds
3. Build industry or ships
4. Explore nearby worlds

---

## User Interface

### Screen Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Header: Character Badge | Resource HUD | Timer | Audio | Status │
├──────────┬──────────────────────────┬─────────────────────────┤
│          │                          │                         │
│ Left     │   Canvas (Map View)      │ Right                   │
│ Sidebar  │                          │ Sidebar                 │
│          │                          │                         │
│ • Score  ├──────────────────────────┤ • Orders                │
│ • Worlds │   Event Log              │ • Selection             │
│ • Fleets │                          │   Info                  │
│          │                          │                         │
├──────────┴──────────────────────────┴─────────────────────────┤
│ Command Input | Help | Manual | Bug Report | Send             │
└─────────────────────────────────────────────────────────────────┘
```

### Header

**Character Ability Badge** (Left)
- Shows your character type with emoji icon
- Hover to see your special abilities in a tooltip
- Persistent reminder of your character bonuses
- Example: 🏭 Empire Builder

**Resource Summary HUD** (Center-Left)
- Real-time totals across all your worlds
- 👥 Total Population
- 🏭 Total Industry
- ⚙️ Total Metal
- 🚀 Total Ships (includes fleet ships + world defenses)
- Updates automatically as you build, move, or capture

**Turn Timer** (Center)
- Current turn number
- Time remaining until next turn
- Players ready count (e.g., "3/5 ready")

**Header Controls** (Right)
- 🔊 Audio toggle button
- 🚪 Logout button
- Connection status indicator

### Left Sidebar

**Scoreboard**
- Shows all players and their scores
- Your position highlighted

**My Worlds**
- Lists worlds based on selected filter
- **Filter buttons**: Mine (default) | All | Neutral | Enemy
- **Keyboard shortcuts**: Press 1-4 to switch filters quickly
- Shows population, industry, defenses (I#/P# format)
- 🔑 icon marks your homeworld
- Enemy/neutral worlds show owner badges
- Click to select and view details

**My Fleets**
- Lists fleets based on selected filter
- **Filter buttons**: Mine (default) | All
- Grouped by location
- Shows ships, cargo, artifacts
- Enemy fleets show owner badges
- Conflict indicator ⚔️ for hostile fleets present

### Center Panel

**Canvas (Map)**
- Visual representation of the galaxy
- Worlds shown as circles
- Fleets shown as squares/diamonds around worlds
- Lines connect accessible worlds
- **Controls:**
  - **Drag**: Click and drag to pan
  - **Scroll**: Zoom in/out
  - **Click world**: Select world
  - **Hover**: Show quick details in status bar

**Event Log**
- Battle results
- Resource production
- System messages
- Color-coded by importance

### Right Sidebar

**Orders This Turn**
- Shows your queued commands
- Can cancel orders before submitting turn
- Click X to remove an order

**Selection Info**
- **World Info**: Resources, defenses, fleets, artifacts
- **Fleet Info**: Ships, cargo, artifacts, location
- Shows relevant quick commands

### Status Panel

Located just below the header, shows:
- **Hovering over world**: Resources, population, defenses
- **Hovering over fleet**: Owner, ships, cargo, status

### Command Input

At the bottom:
- Type commands directly
- Auto-complete suggestions appear
- **?** button for help
- **📖** button to download manual
- **🐛** button to report bugs
- **Send** to execute command
- Press **Enter** to send command
- Press **↑** and **↓** to navigate command history

### Keyboard Shortcuts

Press **H** or **?** during gameplay to see the shortcuts reference modal.

**Navigation**
- `/` - Focus command input
- `ESC` - Clear command input
- `↑` `↓` - Navigate command history

**Game Actions**
- `T` - End turn (submit TURN command)
- `H` or `?` - Show keyboard shortcuts modal
- `M` - Download manual
- `A` - Toggle audio on/off

**World Filters** (switch what the "My Worlds" list displays)
- `1` - My worlds (default)
- `2` - All known worlds
- `3` - Neutral worlds only
- `4` - Enemy worlds only

**Mouse Controls**
- **Click** world or fleet - Select it
- **Drag** canvas - Pan the map
- **Scroll** - Zoom in/out
- **Hover** - Show quick info in status panel

---

## Game Concepts

### Worlds

Worlds are planets you can control and develop.

#### World Properties
- **Population** 👥: Workers for production
- **Industry** 🏭: Production capacity
- **Metal** 🔩: Raw materials for building
- **Mines** ⛏️: Generate metal each turn
- **Limit**: Maximum population
- **IShips** 🔵: Interdictor ships (defense)
- **PShips** 🟢: Patrol ships (defense)

#### World Types
- **Home Worlds**: Starting planets (Alpha, Beta, Gamma, etc.)
- **Colonized**: Worlds you've captured
- **Neutral**: Unowned worlds ready to colonize
- **Enemy**: Controlled by opponents
- **⚫ Black Holes**: Dangerous voids that destroy ships

#### Black Holes

**WARNING: Black holes are extremely dangerous!**

A few worlds on the map are black holes. These cosmic voids have special properties:

**Effects:**
- ⚫ **Ships are destroyed** - All ships moving into or through a black hole are instantly destroyed
- 🔑 **Fleet keys respawn** - The fleet key reappears at a random location in the galaxy
- ✨ **Artifacts preserved** - Any artifacts on the destroyed fleet respawn with the key
- 📦 **Cargo lost** - All cargo is destroyed

**Detection:**
- **Probe to reveal** - Use `F#P#` or `I#P#`/`P#P#` to probe adjacent worlds
- **Visual appearance** - Black holes appear as dark voids with purple accretion disks on the map
- **Selection info** - Clicking a black hole shows a warning message

**Protection:**
- **Homeworlds safe** - You will never start adjacent to a black hole
- **One-way trip** - Once ships enter, they cannot escape

**Strategic Use:**
- **Dispose of bad artifacts** - Intentionally fly a fleet with unwanted artifacts into a black hole
- **Trap detection** - Probe suspicious worlds before moving valuable fleets
- **Avoid pathfinding** - Don't create movement paths that go through black holes

**Example:**
```
Probe of W42: ⚫ BLACK HOLE DETECTED! ⚫ Ships entering this world will be DESTROYED!
```

#### Population Types
- **Human** 👥: Standard population
- **Robot** 🤖: Created by Berserker plundering
- **Apostle** ✝️: Special population type

### Fleets

Fleets are groups of spaceships under your command.

#### Fleet Properties
- **Ships** 🚀: Number of ships (attack/defense strength)
- **Cargo** 📦: Industrial goods for building
- **Artifacts** ✨: Special items that boost score
- **Location**: World where fleet is stationed

#### Fleet States
- **Stationary**: Orbiting a world (square icon)
- **Cargo loaded**: Diamond icon (📦)
- **Moving**: In transit between worlds (triangle)
- **Ambushing** ⚔️: Waiting to attack arriving fleets
- **Empty**: No ships (⚪ gray)

#### Fleet Types
- **Friendly** (green): Your fleets, orbit close to world
- **Hostile** (red): Enemy fleets, orbit farther out

### Resources

#### Metal 🔩
- Mined from worlds with mines ⛏️
- Used to build: ships, industry, mines, defenses
- Stored at worlds

#### Industry 🏭
- Production capacity
- Requires population to operate
- Converts metal into ships/cargo

#### Cargo 📦
- Produced by industry
- Loaded onto fleets
- Used to build at remote worlds

#### Effective Production
- **Effective Population** = min(population, industry)
  - You need workers to run factories
- **Effective Industry** = min(industry, population)
  - Factories need workers

### Artifacts

Special items that:
- **Grant bonus points** toward victory
- Can be found on worlds
- Can be transferred between fleets
- **Commands:**
  - `LOAD F# A#` - Load artifact onto fleet
  - `UNLOAD F# A#` - Unload artifact from fleet

### Connections

Worlds are connected by hyperspace lanes:
- Fleets can only move between connected worlds
- Shown as lines on the map
- View connections by clicking a world

---

## Commands Reference

### Basic Commands

#### HELP [topic]
Get help information
```
HELP              - Show all commands
HELP commands     - List available commands
HELP F5           - Help for specific fleet
HELP W3           - Help for specific world
```

#### TURN
End your turn and mark yourself ready
```
TURN
```

### Fleet Movement

#### F#W# - Move Fleet to World
Move a fleet to a connected world
```
F5W10             - Move Fleet 5 to World 10
```
- Only works for connected worlds
- Fleet must have ships
- Fleet marked as "moving"

### Building Commands

#### W#B#I - Build Industry
Build industry at a world (costs metal)
```
W3B25I            - Build 25 industry at World 3
```

#### W#B#M - Build Mines
Build mines at a world (costs metal)
```
W3B10M            - Build 10 mines at World 3
```

#### W#B#S - Build Ships
Build ships using industry
```
W5B50S            - Build 50 ships at World 5
```

#### W#B#P - Build Population
Grow population (costs industry)
```
W5B100P           - Build 100 population at World 5
```

#### W#B#I# - Build IShips (Defense)
Build interdictor ships
```
W3B20I5           - Build 20 IShips at World 3 (costs 5 metal each)
```

#### W#B#P# - Build PShips (Defense)
Build patrol ships
```
W3B15P3           - Build 15 PShips at World 3 (costs 3 metal each)
```

### Cargo Commands

#### F#LW# - Load Cargo
Load cargo from world onto fleet
```
F5LW3             - Fleet 5 loads cargo from World 3
F5L50W3           - Fleet 5 loads 50 cargo from World 3
```

#### F#UW# - Unload Cargo
Unload cargo from fleet to world
```
F5UW3             - Fleet 5 unloads all cargo to World 3
F5U30W3           - Fleet 5 unloads 30 cargo to World 3
```

#### F#B#S - Build Ships (using fleet cargo)
Build ships at remote world using cargo
```
F5B40S            - Fleet 5 builds 40 ships (uses cargo)
```

### Artifact Commands

#### LOAD F# A#
Load artifact from world onto fleet
```
LOAD F5 A1        - Load Artifact 1 onto Fleet 5
```

#### UNLOAD F# A#
Unload artifact from fleet to world
```
UNLOAD F5 A1      - Unload Artifact 1 from Fleet 5
```

### Combat Commands

#### F#AF# - Fire at Fleet
Attack another fleet
```
F5AF12            - Fleet 5 attacks Fleet 12
```
- Target must be at same world
- Combat occurs during turn processing

#### F#AP - Fire at Population
Bombard planet population
```
F5AP              - Fleet 5 bombards population
```

#### F#AI - Fire at Industry
Bombard planet industry
```
F5AI              - Fleet 5 bombards industry
```

#### F#AM - Fire at Mines
Bombard planet mines
```
F5AM              - Fleet 5 bombards mines
```

#### F#AW# - Fire at World (general bombardment)
Attack a world's resources
```
F5AW3             - Fleet 5 bombards World 3
```

#### F#AMBUSH
Set fleet to ambush mode
```
F5AMBUSH          - Fleet 5 waits to ambush arriving fleets
```
- Attacks fleets that arrive at the world
- Exclusive with MOVE/FIRE

### Transfer Commands

#### F#T#F# - Transfer Ships
Transfer ships between fleets
```
F5T20F8           - Transfer 20 ships from Fleet 5 to Fleet 8
```
- Both fleets must be at same world
- Source must have enough ships

### Advanced Commands

#### CANCEL #
Cancel a queued order
```
CANCEL 1          - Cancel order #1
CANCEL 3          - Cancel order #3
```

#### SCUTTLE F#
Destroy a fleet
```
SCUTTLE F5        - Destroy Fleet 5
```

---

## Game Mechanics

### Turn Sequence

1. **Order Submission**: Players enter commands
2. **Ready Up**: Players mark turn ready (or timer expires based on average player preference)
3. **Resolution**: Server processes all orders in priority order:
   - Unloading
   - Ship transfers
   - Building
   - Loading
   - Combat (firing/ambushing)
   - Movement
   - **World Capture** (happens immediately - same turn as arrival!)
   - Fleet captures
   - Production
4. **Updates**: Clients receive new game state
5. **Next Turn**: Cycle repeats

### World Capture Rules

**Capture happens IMMEDIATELY when:**
- You are the only player with ships (not at peace) at the world
- The world has no enemy defensive ships (iships/pships)
- The world has non-zero population

**Defensive Ships Block Capture:**
- Worlds with iships or pships cannot be captured by mere fleet presence
- You must destroy all defensive ships first
- Owner retains the world as long as they have iships/pships, even with no fleets

**Building Defenses Claims Worlds:**
- Building iships or pships on a neutral world **immediately** claims it
- Ownership persists as long as defenses remain

### Combat

#### Fleet vs Fleet
- **Attacker fires first**
- Damage = ships in attacking fleet
- Target loses ships equal to damage
- If target survives, they counter-attack
- Combat continues until one side destroyed

#### Fleet vs World
- Fleet bombards world resources
- Defenses (IShips, PShips) fight back
- Damage distributed across targets
- Population, industry, mines can be destroyed

#### Ambush
- Ambushing fleet attacks arriving fleets
- Surprise attack bonus
- Defending fleet cannot move after ambush

### Production

Each turn, worlds produce:
- **Metal**: Mines generate metal
- **Ships**: Industry converts metal to ships
- **Cargo**: Industry creates cargo
- **Population**: Natural growth (if below limit)

**Production Formulas:**
- Metal production = Mines × base_rate
- Ship production = min(Industry, Population) ÷ ship_cost
- Effective workers = min(Population, Industry)

### Scoring

Points awarded for:
- **Worlds owned**: Points per world
- **Population**: Points per citizen
- **Industry**: Points per factory
- **Fleets**: Points per ship
- **Artifacts**: Bonus points per artifact (highest value)
- **Kills**: Points for destroying enemy assets

**First to target score wins!**

### Special Mechanics

#### Plundering
- Berserker character can plunder worlds
- Converts population to robots
- Steals resources

#### Planet Buster Bomb 💣
- Devastating weapon
- Destroys entire world
- Major strategic impact
- Visible on fleet: `💣 PBB`

---

## Character Types

**Important**: Each character type has different victory conditions and scoring methods!

### Empire Builder
**Objective**: Control the most territory and resources

**Victory Points:**
- **1 point per turn** for each 10 population you control
- **1 point per turn** for each industry you control
- **1 point per turn** for each mine you control

**Special Power**: Build industry more efficiently (4 industry or 4 IShips instead of 5/6)

**Playstyle**: Expansion and development
- Focus on capturing and building worlds
- Maximize population, industry, and mines
- **Strategy**: Rapid expansion, strong infrastructure

### Merchant
**Objective**: Dominate trade and commerce

**Victory Points:**
- **8 points** for each metal unloaded on another player's world (limited by their industry × 2)
- **10/8/5/3/1 points** for unloading consumer goods on worlds (decreasing each time)

**Special Power**: Ships carry **2 cargo each** instead of 1 (other players only carry 1)

**Playstyle**: Economic powerhouse
- Trade with other players for points
- Focus on cargo production and delivery
- **Strategy**: Build industry, produce metal/cargo, establish trade routes

### Pirate
**Objective**: Plunder and capture

**Victory Points:**
- **50/40/30/20/10 points** for plundering a world (first through fifth time)
- **3 points per turn** for each key (fleet) you own

**Special Power**: **Auto-capture** enemy fleets when you outnumber them 3:1 at a world

**Playstyle**: Raiding and harassment
- Capture worlds and plunder them
- Build large fleets to capture enemy ships
- **Strategy**: Hit-and-run attacks, accumulate keys, maximize ship count

### Artifact Collector
**Objective**: Collect rare artifacts

**Victory Points:**
- **Points for each artifact** you own (varies by artifact)
- **500 bonus points** for each "museum world" with 10+ artifacts

**Special Power**:
- No penalty for plastic artifacts
- Transfer artifacts between fleets directly
- Others can give you artifacts

**Playstyle**: Artifact hunting
- Explore to find artifacts
- Build museums (10+ artifacts on one world)
- **Strategy**: Find and protect artifacts, defend key worlds

### Berserker
**Objective**: Destroy all life

**Victory Points:**
- **2 points** for each population you kill
- **5 points per turn** for each robot-populated world
- **2 points** for each ship you destroy
- **200 points** for using a Planet Buster Bomb (plus population killed)

**Special Power**: Convert ships to robots for ground assault, capture worlds with robots

**Playstyle**: Aggressive conquest
- Constant warfare and destruction
- Robot invasions
- **Strategy**: Kill population, drop robots, use PBBs

### Apostle
**Objective**: Convert the galaxy to your beliefs

**Victory Points:**
- **5 points per turn** for each world you control
- **1 point per turn** for each 10 converts in the universe
- **5 additional points** for worlds completely populated by converts
- **1 point** for each martyr (convert killed by others)

**Special Power**:
- Ships and converts can convert population (10% chance each)
- Capture worlds by full conversion
- Can declare Jihad (holy war) against one player

**Playstyle**: Conversion and expansion
- Spread converts throughout the galaxy
- Build fully-converted worlds
- **Strategy**: Position fleets to convert, defend converts, use Jihad strategically

---

## Victory Conditions

### How to Win
**First player to reach the target score wins!**
- Default: 8000 points
- Set during game join
- Track progress on scoreboard

**Important**: Each character type scores points differently! See [Character Types](#character-types) for details.

### Scoring By Character Type

| Character Type | Primary Scoring Method |
|----------------|------------------------|
| **Empire Builder** | 1 pt/turn per 10 pop, 1 pt/turn per industry/mine |
| **Merchant** | 8 pts per metal traded, 10/8/5/3/1 pts for consumer goods |
| **Pirate** | 50/40/30/20/10 pts for plundering, 3 pts/turn per fleet |
| **Artifact Collector** | Points per artifact, 500 pt museum bonuses |
| **Berserker** | 2 pts per population killed, 5 pts/turn per robot world, 200 pts per PBB |
| **Apostle** | 5 pts/turn per world, 1 pt/turn per 10 converts |

### Strategy Based on Character Type

**Empire Builder**: Expand rapidly, build infrastructure everywhere, maximize total resources

**Merchant**: Establish trade routes, produce cargo, unload on other players' worlds with industry

**Pirate**: Capture worlds, plunder repeatedly, build massive fleets to auto-capture enemies

**Artifact Collector**: Explore aggressively, find all artifacts, create museum worlds (10+ artifacts)

**Berserker**: Constant warfare, kill population, drop robots, use PBBs on high-pop worlds

**Apostle**: Position fleets to convert, create fully-converted worlds, use Jihad against leader

### Endgame Strategy
As you approach victory:
- **Know your scoring**: Focus on actions that give YOUR character type points
- **Protect key assets**: Don't lose high-value targets
- **Deny opponents**: Attack based on their scoring method (e.g., kill Merchant's trade partners)
- **Calculate victory path**: Know exactly how many more points you need
- **Watch the leader**: Attack whoever is closest to winning

---

## Tips & Strategy

### Early Game (Turns 1-10)

**Priorities:**
1. **Scout your neighborhood**: Move fleets to explore
2. **Build industry**: Foundation for long-term growth
3. **Secure nearby worlds**: Easy expansion targets
4. **Establish production**: Balance mines, industry, ships

**Common Mistakes:**
- ❌ Over-building military early
- ❌ Neglecting scouting
- ❌ Spreading too thin
- ✅ Focus on 2-3 core worlds

### Mid Game (Turns 11-30)

**Priorities:**
1. **Expand borders**: Claim unclaimed worlds
2. **Build strong fleets**: Prepare for conflict
3. **Secure artifacts**: Major score boost
4. **Economic infrastructure**: Mines + industry

**Key Decisions:**
- When to start conflict?
- Which neighbors to fight?
- Which artifacts to prioritize?
- How many fleets to maintain?

### Late Game (Turns 30+)

**Priorities:**
1. **Calculate victory path**: Know what you need to win
2. **Deny opponent victory**: Attack leaders
3. **Protect assets**: Defend worlds with defenses
4. **Concentrate force**: Don't split fleets

**Winning Moves:**
- Capture high-population worlds
- Steal artifacts from opponents
- Eliminate weak players for quick points
- Form temporary alliances against leader

### Combat Tips

**Attacking:**
- Scout first (see enemy defenses)
- Bring overwhelming force (2x ships)
- Target artifacts (high value)
- Bombard industry (cripple production)

**Defending:**
- Build IShips/PShips at key worlds
- Keep reserve fleets nearby
- Use ambush for arriving enemies
- Don't let fleets get isolated

### Economic Tips

**Production Efficiency:**
- Balance population & industry
- Don't overbuild (population > industry wastes workers)
- Mines on metal-rich worlds
- Cargo for remote building

**Resource Management:**
- Keep metal reserves for emergencies
- Produce cargo for flexibility
- Don't let resources sit idle
- Transfer ships between fleets as needed

### Fleet Management

**Fleet Composition:**
- **Large fleets**: Powerful but slow to build
- **Small fleets**: Flexible but weak
- **Cargo fleets**: Transport building materials
- **Scout fleets**: Small ships for exploration

**Movement:**
- Plan routes ahead (connections only)
- Don't leave fleets exposed
- Use ambush at choke points
- Retreat when outmatched

### Information Warfare

**What you can see:**
- Worlds with your fleets
- Enemy fleet sizes
- Movement patterns
- Artifact locations

**What they can't see:**
- Your cargo amounts
- Your exact build plans
- Artifacts on your fleets
- Planet buster bombs

**Use this to your advantage!**

---

## Quick Reference Card

### Most Common Commands
```
F5W10             Move fleet 5 to world 10
W3B25I            Build 25 industry at world 3
W3B50S            Build 50 ships at world 3
F5LW3             Load cargo from world 3 onto fleet 5
F5UW3             Unload cargo to world 3
F5AF12            Fleet 5 attacks fleet 12
LOAD F5 A1        Load artifact 1 onto fleet 5
TURN              End your turn
HELP              Show help
```

### Keyboard Shortcuts
- **Click world**: Select and view info
- **Click fleet**: Select and view info
- **Drag canvas**: Pan camera
- **Scroll**: Zoom in/out
- **Hover**: Quick stats in status bar

### Critical Rules
- ✅ Fleets can only move to connected worlds
- ✅ MOVE, FIRE, and AMBUSH are mutually exclusive
- ✅ You need metal to build
- ✅ Effective production = min(population, industry)
- ✅ Artifacts on fleets are hidden from enemies
- ✅ First to target score wins

---

## Getting Help

### In-Game Help
```
HELP              - All commands
HELP commands     - Command list
HELP F5           - Fleet-specific help
HELP W3           - World-specific help
```

### UI Features
- **? button**: Opens help
- **Hover tooltips**: Quick stats
- **Selection info**: Detailed stats and suggested commands
- **Event log**: Combat results and system messages

### Community
- Report bugs: https://github.com/anthropics/claude-code/issues
- Game feedback: Use GitHub issues

---

## Appendix: Complete Command List

| Command | Format | Description |
|---------|--------|-------------|
| HELP | `HELP [topic]` | Show help |
| TURN | `TURN` | End turn |
| MOVE | `F#W#` | Move fleet to world |
| BUILD INDUSTRY | `W#B#I` | Build industry |
| BUILD MINES | `W#B#M` | Build mines |
| BUILD SHIPS | `W#B#S` | Build ships at world |
| BUILD POPULATION | `W#B#P` | Grow population |
| BUILD ISHIPS | `W#B#I#` | Build interdictor ships |
| BUILD PSHIPS | `W#B#P#` | Build patrol ships |
| LOAD CARGO | `F#LW#` or `F#L#W#` | Load cargo |
| UNLOAD CARGO | `F#UW#` or `F#U#W#` | Unload cargo |
| BUILD (CARGO) | `F#B#S` | Build ships using cargo |
| LOAD ARTIFACT | `LOAD F# A#` | Load artifact |
| UNLOAD ARTIFACT | `UNLOAD F# A#` | Unload artifact |
| FIRE FLEET | `F#AF#` | Attack fleet |
| FIRE POPULATION | `F#AP` | Bombard population |
| FIRE INDUSTRY | `F#AI` | Bombard industry |
| FIRE MINES | `F#AM` | Bombard mines |
| FIRE WORLD | `F#AW#` | Bombard world |
| AMBUSH | `F#AMBUSH` | Set ambush |
| TRANSFER | `F#T#F#` | Transfer ships |
| CANCEL | `CANCEL #` | Cancel order |
| SCUTTLE | `SCUTTLE F#` | Destroy fleet |

---

## Revision History

### December 2025 Update

**New Features:**

1. **Game State Persistence**
   - Server now saves game state to disk after each turn
   - Games automatically resume from last state on server restart
   - Graceful shutdown with state preservation (no data loss)
   - Backup system (.json.bak) for save file safety

2. **Player Reconnection**
   - Players can rejoin existing games without creating duplicate homeworlds
   - Server tracks persistent player data by name
   - Reconnecting players restore their fleets, worlds, and resources
   - Prevents accidental multi-account abuse

3. **Player Manual Download**
   - Added 📖 button to download this manual from the game UI
   - Players can access full documentation anytime
   - Manual served as markdown file for offline reading

4. **Character-Specific Scoring System**
   - Empire Builder: Corrected to 1 pt per 10 population (was 1 per 1), added 1 pt per mine
   - Pirate: Added 3 points per key owned
   - Artifact Collector: Implemented full artifact scoring (30 pts Ancient/Pyramid, 90 pts Ancient Pyramid, 15 pts others)
   - All character types now have proper scoring matching official StarWeb rules

5. **World Capture Mechanics**
   - World capture now happens **immediately** when fleet arrives (same turn)
   - Removed 1-turn delay for capturing neutral/undefended worlds
   - Defensive ships (iships/pships) still prevent capture
   - Zero population worlds cannot be owned

6. **Artifact Transfer System**
   - Fixed TRANSFER_ARTIFACT command to work with fleet presence
   - LOAD/UNLOAD artifacts now work when you have a fleet at the world (not just ownership)
   - Improved artifact access rules

7. **Turn Timer System**
   - Players can now specify preferred minimum turn time when joining
   - Format: `JOIN <name> [minutes] [character_type]`
   - Average of all players' preferences used as actual turn duration
   - Default: 60 minutes if not specified
   - Range: 5-1440 minutes (5 min to 24 hours)

8. **Homeworld Improvements**
   - Homeworlds are now guaranteed to be at least 1 hop apart
   - Artifacts are never placed on starting homeworlds (relocated to neutral worlds)
   - Homeworlds marked with 🔑 icon in world list

9. **Defense Display Format**
   - Defense display now shows `I#/P#` format (e.g., "I5/P3")
   - Real-time updates when iships/pships change
   - More informative tooltip: "Defenses (Industry Ships/Population Ships)"

10. **Chat System**
    - Added player-to-player chat functionality
    - Admin message system with auto-collapse banner
    - Message notifications in event log

11. **UI Improvements**
    - Multi-hop movement suggestions show only connected worlds
    - Visual path tracking for complex move commands
    - Reduced command suggestions dropdown size (60% smaller)
    - Improved admin banner with auto-collapse (10 seconds)

**Bug Fixes:**
- Fixed world ownership mechanics with defensive ships
- Fixed building defenses on neutral worlds (now claims world immediately)
- Corrected command access checks for LOAD/UNLOAD/TRANSFER_ARTIFACT
- Improved connection-aware pathfinding for multi-hop moves
- Fixed manual download route (nginx configuration)

### Initial Release
- Core game mechanics
- Basic UI
- Fleet and world management
- Combat system
- 6 character types

---

**Good luck, Commander! May your fleets be victorious and your empire eternal! 🚀✨**
