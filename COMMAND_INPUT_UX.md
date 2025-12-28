# Command Input UX Guide

## Overview
The command input system now intelligently combines speed actions, sidebar clicks, and map clicks to build commands.

## How It Works

### Smart Context Detection
When you click on a fleet or world, the system analyzes the current command input and inserts the ID in the appropriate position.

### Building Commands with Clicks

#### Move Command (F156W123)
1. Click fleet 156 in sidebar → Input: `F156`
2. Click "Move" speed action → Input: `F156W`
3. Click world 123 on map → Input: `F156W123` ✅

**OR:**
1. Click fleet 156 in sidebar → Input: `F156`
2. Click world 123 on map → Input: `F156W123` ✅ (auto-detects move)

#### Multi-Hop Move (F156W123W45W67)
1. Start with `F156W123`
2. Click world 45 → Input: `F156W123W45`
3. Click world 67 → Input: `F156W123W45W67` ✅

#### Fleet-to-Fleet Transfer (F156T10F246)
1. Type `F156T10` (or use speed actions)
2. Click fleet 246 in sidebar → Input: `F156T10F246` ✅

#### Attack Fleet (F156AF246)
1. Type `F156AF` (or use speed actions)
2. Click fleet 246 in sidebar → Input: `F156AF246` ✅

#### Build on Fleet (W10B25F156)
1. Type `W10B25`
2. Click fleet 156 in sidebar → Input: `W10B25F156` ✅

#### Artifact Transfer Fleet-to-Fleet (F156TA3F246)
1. Type `F156TA3`
2. Click fleet 246 in sidebar → Input: `F156TA3F246` ✅

### Speed Actions
Speed actions provide quick templates:
- **Move**: Sets `F<selectedFleet>W` and waits for world click
- **Fire World**: Sets `F<selectedFleet>AP` for population
- **Fire Fleet**: Sets `F<selectedFleet>AF` and waits for fleet click
- **Ambush**: Sets `F<selectedFleet>A`
- **Build Industry**: Sets `W<selectedWorld>B10I` (amount is selected for easy editing)
- **Build Ships**: Sets `W<selectedWorld>B10I` (amount is selected for easy editing)
- **Transfer to Garrison**: Sets `F<selectedFleet>T10I` (amount is selected)

### Context-Aware Insertion

The system recognizes these patterns:

**Waiting for World:**
- `F156W` → Click world → `F156W123`
- `F156W10` → Click world → `F156W10W123` (multi-hop)
- `W10M5` → Click world → `W10M5W123` (migration destination)

**Waiting for Fleet:**
- `F156T10` → Click fleet → `F156T10F246` (transfer target)
- `F156AF` → Click fleet → `F156AF246` (fire target)
- `W10B25` → Click fleet → `W10B25F156` (build target)
- `F156TA3` → Click fleet → `F156TA3F246` (artifact transfer target)
- `W10TA3` → Click fleet → `W10TA3F156` (artifact from world to fleet)

**Starting New:**
- Empty input → Click fleet → `F<id>`
- Empty input → Click world → `W<id>`
- Completed command → Click fleet → `F<id>` (starts new)
- Completed command → Click world → `W<id>` (starts new)

### Selection Rules

**Fleet Selection:**
- Clicking a fleet in the sidebar selects it AND inserts into command if appropriate
- Can select multiple fleets in sequence (for source/target commands)

**World Selection:**
- Clicking a world on map or in sidebar selects it AND inserts into command if appropriate
- Can click multiple worlds in sequence (for multi-hop moves)

## Examples

### Transfer Ships Between Fleets
**Goal:** Transfer 5 ships from fleet 156 to fleet 246

**Method 1 (Type + Click):**
1. Type: `F156T5`
2. Click fleet 246 in sidebar
3. Result: `F156T5F246` ✅

**Method 2 (All Clicks):**
1. Click fleet 156 in sidebar → `F156`
2. Type: `T5`
3. Click fleet 246 in sidebar → `F156T5F246` ✅

### Attack Hostile Fleet
**Goal:** Fleet 10 attacks fleet 25

**Method:**
1. Click fleet 10 in sidebar → `F10`
2. Type: `AF`
3. Click fleet 25 in sidebar → `F10AF25` ✅

### Build Ships on Specific Fleet
**Goal:** Build 30 ships on fleet 7 at world 15

**Method:**
1. Type: `W15B30`
2. Click fleet 7 in sidebar → `W15B30F7` ✅

## Camera Auto-Focus

### Fleet Selection
When you select a fleet from the sidebar:
- **Centers**: Map centers on the world where the fleet is orbiting
- **Zooms Out**: Automatically zooms to show all connected worlds
- **Highlights**: The fleet's world is highlighted on the map

**Zoom Calculation:**
- Measures distances to all connected worlds
- Sets zoom level to show farthest connection within view
- Ensures comfortable viewing (2.5x the max connection distance)
- Clamps zoom between 0.3 and 1.0 for best experience

**Example:**
```
Fleet 156 is at World 10
World 10 connects to: W5, W23, W87, W45
→ Camera centers on W10
→ Zoom adjusts so all 4 connections are visible
```

### World Selection
When you select a world:
- **Centers**: Map centers on the selected world
- **Zoom**: Maintains current zoom level (use scroll wheel to adjust)

## Tips

1. **Speed Actions are Optional**: You can build most commands just by clicking and typing
2. **Order Matters**: The system understands command context, so click in logical order
3. **Edit Freely**: The smart insertion only applies to recognized patterns; you can always edit manually
4. **Visual Feedback**: Command hints show suggestions and validate as you type
5. **Selection Highlights**: Selected fleets/worlds are highlighted on the map and in sidebars
6. **Strategic View**: Selecting a fleet gives you immediate tactical context of nearby worlds

## Fixed Issues

✅ **No more "WW" bug**: Clicking world after speed action properly completes the command
✅ **Fleet-to-fleet commands work**: Can select second fleet for transfers and attacks
✅ **Smart context detection**: System recognizes partial commands and inserts appropriately
✅ **Multi-selection support**: Can select different fleets/worlds as needed for complex commands
✅ **Auto-focus on fleet selection**: Camera centers and zooms to show tactical situation
✅ **World highlighting**: Fleet's orbit world is highlighted when fleet is selected
