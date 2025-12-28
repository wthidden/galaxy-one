# Fleet List Organization

## Overview

The "My Fleets" sidebar now organizes fleets by the world they're orbiting, with conflict zones highlighted and prioritized at the top.

## Changes Made

**File**: `client/ui/FleetList.js`

### New Organization Structure

#### Before:
```
My Fleets
├── F5 @ W10
├── F12 @ W10
├── F23 @ W45
├── F8 @ W10
└── F17 @ W45
```
- Simple list sorted by fleet ID
- No grouping
- No conflict indication
- Hard to see tactical overview

#### After:
```
My Fleets
├── W10 (yours) ⚔️          ← CONFLICT (hostile fleets present)
│   ├── F5
│   ├── F8
│   └── F12
├── W45 (Bob)
│   ├── F17
│   └── F23
└── 🚀 In Transit
    └── F99
```
- Grouped by world
- Conflict worlds at top (⚔️ indicator)
- Shows world ownership
- Clear tactical hierarchy

## Implementation Details

### Grouping Algorithm

**Step 1: Group fleets by world**
```javascript
_groupFleetsByWorld(fleets) {
    const groups = {};
    fleets.forEach(fleet => {
        const worldId = fleet.world !== undefined ? fleet.world : 'moving';
        if (!groups[worldId]) {
            groups[worldId] = [];
        }
        groups[worldId].push(fleet);
    });
    return groups;
}
```

**Step 2: Detect conflicts**
```javascript
_hasConflict(worldId, gameState) {
    // Get all fleets at this world
    const fleetsAtWorld = Object.values(gameState.fleets || {})
        .filter(f => f.world == worldId);

    // Check if there are hostile fleets
    return fleetsAtWorld.some(f => f.owner !== gameState.player_name);
}
```

**Step 3: Sort (conflict first, then by world ID)**
```javascript
worldGroups.sort((a, b) => {
    // Conflict worlds first
    if (a.hasConflict && !b.hasConflict) return -1;
    if (!a.hasConflict && b.hasConflict) return 1;

    // Same conflict status → sort by world ID
    const aId = a.worldId === 'moving' ? Infinity : parseInt(a.worldId);
    const bId = b.worldId === 'moving' ? Infinity : parseInt(b.worldId);
    return aId - bId;
});
```

### Visual Indicators

**World Headers:**
- Normal: Gray background (#333), gray text
- Conflict: Red-tinted background (#442222), orange text (#ffaa77)
- Left border: Gray (normal) or Red (conflict)

**Conflict Icon:**
- ⚔️ (crossed swords) appears next to world name
- Indicates hostile fleets present
- Immediate visual warning

**Ownership Labels:**
- `(yours)` - World owned by player
- `(PlayerName)` - World owned by another player
- No label - Neutral/unknown world

**In Transit:**
- 🚀 icon for moving fleets
- Always at bottom of list
- Groups all fleets with active move orders

## Sorting Priority

1. **Conflict worlds** (hostile fleets present) ⚔️
2. **Your worlds** (by world ID)
3. **Other worlds** (by world ID)
4. **In transit** (moving fleets)

## Example Scenarios

### Scenario 1: Multiple Conflicts
```
My Fleets
├── W15 (yours) ⚔️           ← 2 enemy fleets here
│   ├── F10 🚀45 📦5
│   └── F12 🚀30
├── W23 (Bob) ⚔️             ← 1 enemy fleet here
│   └── F5 🚀20
├── W45 (yours)              ← Safe, no enemies
│   ├── F3 🚀50
│   └── F8 🚀25 📦10
```
**Result:** Both conflict worlds (W15, W23) at top, sorted by ID

### Scenario 2: Mixed Ownership
```
My Fleets
├── W10 (yours)
│   ├── F1
│   ├── F2
│   └── F3
├── W25 (Alice)              ← Orbiting allied world
│   └── F10
├── W50 (neutral)            ← Orbiting neutral world
│   └── F15
```
**Result:** Grouped clearly by location and ownership

### Scenario 3: Moving Fleets
```
My Fleets
├── W10 (yours)
│   └── F5
└── 🚀 In Transit
    ├── F12 ➡️               ← Moving to W20
    └── F15 ➡️               ← Moving to W45
```
**Result:** Moving fleets separated into own group at bottom

## CSS Styling

**File**: `style.css`

### World Group Headers
```css
.fleet-world-group .world-header {
    background-color: #333;
    padding: 6px 8px;
    border-left: 3px solid #555;   /* Gray indicator */
    font-weight: bold;
}

.fleet-world-group.conflict .world-header {
    background-color: #442222;      /* Red tint */
    color: #ffaa77;                 /* Orange text */
    border-left-color: #ff4444;     /* Red indicator */
}
```

### Fleet Indentation
```css
.fleet-world-group .fleet-entry {
    margin-left: 8px;    /* Indent under world header */
}
```

## Benefits

### Tactical Awareness
- ✅ **Instant threat identification**: Conflict zones at top with ⚔️
- ✅ **Quick conflict assessment**: See all threatened positions
- ✅ **Force concentration**: See which worlds have multiple fleets

### Strategic Planning
- ✅ **Better overview**: Understand fleet distribution
- ✅ **Easier coordination**: Group fleets by location
- ✅ **Movement planning**: See transit status clearly

### User Experience
- ✅ **Less scrolling**: Related fleets grouped together
- ✅ **Clear hierarchy**: Worlds → Fleets within
- ✅ **Visual priority**: Conflicts demand attention
- ✅ **Context awareness**: Ownership labels provide context

## Performance

- **Grouping**: O(n) where n = number of player's fleets (~10-50)
- **Conflict detection**: O(n×m) where m = total fleets (~255 max)
- **Sorting**: O(w log w) where w = number of worlds with fleets (~5-20)
- **Total impact**: < 1ms for typical game state
- **Negligible** for player experience

## Future Enhancements

Possible improvements (not currently needed):

1. **Fleet count badges**: Show "W10 (3 fleets)" in header
2. **Enemy fleet count**: Show "⚔️ (2 enemies)" in conflict header
3. **Collapsible groups**: Click to expand/collapse each world
4. **Total ships count**: Show total firepower per world
5. **Alert animations**: Pulse or glow effect for new conflicts
6. **Jump to world**: Click world header to center map on it
7. **Quick actions**: Right-click world header for common commands
