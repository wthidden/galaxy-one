# Hover Tooltips and Fleet Rendering Fixes

## Issues Fixed

### 1. Hover Tooltips Not Working
**Problem**: Hovering over worlds and fleets didn't show any information in the status panel.

**Root Cause**:
- Only worlds were being detected on mousemove
- No fleet hit detection implemented
- Status panel was never updated with hover information

**Solution**:
- Added `findFleetAtScreen(x, y)` method to Renderer
- Updated mousemove handler to detect both fleets and worlds
- Prioritize fleet detection (fleets are smaller, more specific targets)
- Added status panel update functions for worlds and fleets

### 2. Fleet Rendering Overlap
**Problem**: Fleets overlapped with world defense rings (IShip/PShip rings) and artifact badges, making fleet numbers hard to read.

**Root Cause**:
- Friendly fleets positioned at `radius + 5` (same as defense ring!)
- Hostile fleets at `radius + 15` (close to artifact badges at `radius + 8`)

**Solution**:
- Moved friendly fleets to `radius + 12` (clear of defense ring at `radius + 5`)
- Moved hostile fleets to `radius + 22` (clear of artifacts at `radius + 8`)
- Updated both FleetLayer rendering AND hit detection to use same orbits

## Files Modified

### 1. `/home/whidden/Projects/starweb/client/rendering/Renderer.js`

**Added `findFleetAtScreen(x, y)` method:**
- Checks moving fleets first (triangle ships in transit)
- Then checks stationary fleets around worlds
- Uses correct orbit radii (12 for friendly, 22 for hostile)
- Returns fleet ID if mouse is over a fleet icon

```javascript
findFleetAtScreen(screenX, screenY) {
    // Convert screen to world coordinates
    // Check moving fleets (more prominent)
    // Check stationary fleets at both orbit radii
    // Return fleet ID or null
}
```

### 2. `/home/whidden/Projects/starweb/client/rendering/layers/FleetLayer.js`

**Updated orbit radii:**
```javascript
// OLD - overlapped with defense ring
worldPos.radius + 5   // Friendly fleets
worldPos.radius + 15  // Hostile fleets

// NEW - clear spacing
worldPos.radius + 12  // Friendly fleets (clear of defense at +5)
worldPos.radius + 22  // Hostile fleets (clear of artifacts at +8)
```

### 3. `/home/whidden/Projects/starweb/client/main.js`

**Updated mousemove handler:**
```javascript
canvas.addEventListener('mousemove', (e) => {
    if (dragging) {
        // handle drag
    } else {
        // Check fleet first (more specific)
        const fleetId = renderer.findFleetAtScreen(x, y);
        if (fleetId) {
            updateStatusPanelForFleet(fleetId);
        } else {
            // Check world
            const worldId = renderer.findWorldAtScreen(x, y);
            if (worldId) {
                updateStatusPanelForWorld(worldId);
            } else {
                clearStatusPanel();
            }
        }
    }
});
```

**Added status panel update functions:**

#### `updateStatusPanelForWorld(worldId)`
Shows:
- World ID, name, owner
- Population, industry, metal
- Defense ships (IShips, PShips)
- Artifact count

Example: `W5 Alpha (Alice) | 👥 150 | 🏭 75 | 🔩 500 | 🛡️ I:10 P:5 | ✨ 2`

#### `updateStatusPanelForFleet(fleetId)`
Shows:
- Fleet ID, owner
- Location world name
- Ships, cargo (for friendly fleets)
- Artifact count
- Status (moving, ambushing)

Example: `F12 (Alice) at Alpha | 🚀 23 | 📦 15 | ✨ 1 | ➡️ Moving`

#### `clearStatusPanel()`
Resets to default message: "Hover over a world or fleet to see details"

### 4. `/home/whidden/Projects/starweb/style.css`

**Enhanced status panel styling:**
```css
#status-panel {
    background-color: #2d2d2d;
    border: 1px solid #4da6ff;  /* Blue border */
    padding: 12px;
    min-height: 40px;
    font-size: 14px;
    color: #eee;
    border-radius: 4px;
    line-height: 1.6;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

#status-panel strong {
    color: #4da6ff;  /* Blue text for IDs/names */
    font-weight: 600;
}
```

## Visual Layout

### World with Fleets
```
         Hostile Fleet (F20)  ← radius + 22
              ↓

         Friendly Fleet (F5)  ← radius + 12
              ↓

       Artifact Badge (⊙2)   ← radius + 8
            ↓

     Defense Ring (cyan)     ← radius + 5
          ↓

    ═══════════════          ← radius (world)
    ║   World 3   ║
    ═══════════════
```

### Before Fix
```
Defense Ring ─┐
Friendly Fleet├─ OVERLAP! 😵
              ┘
└─ Both at radius + 5
```

### After Fix
```
Defense Ring ───── radius + 5
                   (gap)
Friendly Fleet ─── radius + 12 ✓
                   (gap)
Hostile Fleet ──── radius + 22 ✓
```

## Testing

### Hover Tooltips
1. Hover over a world → status panel shows world details
2. Hover over your fleet → status panel shows fleet details (ships, cargo, etc.)
3. Hover over enemy fleet → status panel shows fleet ID, owner, location, ships
4. Hover over moving fleet → status panel shows fleet in transit
5. Move mouse off canvas → status panel clears to default message

### Fleet Rendering
1. Worlds with IShips/PShips → defense ring at radius+5
2. Friendly fleets → clear circle at radius+12, no overlap
3. Hostile fleets → farther out at radius+22
4. Artifact badges → at radius+8, between defense and friendly fleets
5. All fleet numbers readable and clickable
6. Multiple fleets distributed evenly around world

### Status Panel Display

**World hover:**
```
W3 Alpha (Alice) | 👥 150 | 🏭 75 | 🔩 500 | 🛡️ I:10 P:5 | ✨ 2
```

**Friendly fleet hover:**
```
F5 (Alice) at Alpha | 🚀 23 | 📦 15 | ✨ 1
```

**Enemy fleet hover:**
```
F20 (Bob) at Beta | 🚀 15
```

**Moving fleet hover:**
```
F12 (Alice) at Alpha | 🚀 30 | ➡️ Moving
```

**Ambushing fleet hover:**
```
F7 (Alice) at Gamma | 🚀 25 | ⚔️ Ambushing
```

## Benefits

### User Experience
✅ **Instant information** - Hover shows details without clicking
✅ **Clear visual feedback** - Status panel updates in real-time
✅ **Readable fleet numbers** - No more overlap with rings/badges
✅ **Better spatial organization** - Clear visual hierarchy

### Technical
✅ **Accurate hit detection** - Fleet hover detection matches rendering
✅ **Consistent spacing** - Same orbit radii for rendering and detection
✅ **Optimized checks** - Fleets checked before worlds (more specific)
✅ **Clean code** - Separate status update functions for maintainability

## Implementation Details

### Fleet Hit Detection Algorithm
1. Convert screen coordinates to world coordinates
2. Check moving fleets first (in transit, more visible)
3. For each stationary world:
   - Separate friendly (closer) from hostile (farther) fleets
   - Check friendly orbit at radius+12
   - Check hostile orbit at radius+22
4. Use distance formula: `dx*dx + dy*dy <= iconSize*iconSize`
5. Return first matching fleet ID

### Orbit Radius Calculations
```
World radius: 20 (variable based on zoom)

Defense ring:    radius + 5  = 25
Artifact badge:  radius + 8  = 28
Friendly fleet:  radius + 12 = 32  ← 7px gap from defenses
Hostile fleet:   radius + 22 = 42  ← 10px gap from friendly
```

### Status Panel Priority
1. **Fleet hover** (highest priority - most specific)
2. **World hover** (if no fleet under mouse)
3. **Clear/default** (if nothing under mouse)

## Future Enhancements

### Potential Improvements
- **Rich tooltips**: Show full fleet/world stats in popup
- **Tooltip delay**: Brief delay before showing to avoid flicker
- **Keyboard shortcuts**: Show tooltip for selected fleet/world
- **Compare mode**: Shift+hover to compare two fleets/worlds
- **History**: Remember last hovered items

### Advanced Features
- **Path preview**: Hover fleet shows possible movement paths
- **Attack range**: Hover fleet highlights attackable targets
- **Trade routes**: Hover world shows cargo flows
- **Diplomacy info**: Show relationships in hover tooltip

## Summary

Both issues completely resolved:
- ✅ Hover tooltips now work for both worlds and fleets
- ✅ Fleet rendering no longer overlaps with defense rings or artifacts
- ✅ Status panel shows rich, contextual information
- ✅ Visual layout is clean and readable
- ✅ Hit detection matches rendering perfectly

Players can now easily see details by hovering, and fleet numbers are always readable!
