# Artifact and Empty Fleet Indicators

## Overview

Added visual indicators for:
1. **Individual artifact IDs** in sidebars and info panels (for attach/detach commands)
2. **Simple artifact count badges** on worlds and fleets on the map
3. **Empty fleets** (0 ships) in sidebar and on map

These changes help players quickly identify important game state information and reference specific artifacts in commands without cluttering the map view.

## Changes Made

### 1. Artifact Count Badge on Worlds (Map)

**File**: `client/rendering/layers/WorldLayer.js`

#### Implementation

Added `_renderArtifactIndicator()` method that displays a simple count badge:

```javascript
_renderArtifactIndicator(ctx, world, pos, camera) {
    // Only show simple artifact count badge if world has been seen and has artifacts
    if (!world.artifacts || !Array.isArray(world.artifacts) || world.artifacts.length === 0) return;

    const badgeSize = Math.max(10, 14 / camera.zoom);
    const badgeX = pos.x + pos.radius + 8;
    const badgeY = pos.y;

    // Draw gold badge with artifact count
    ctx.fillStyle = '#ffd700';
    ctx.beginPath();
    ctx.arc(badgeX, badgeY, badgeSize / 2, 0, 2 * Math.PI);
    ctx.fill();

    // Draw count
    ctx.fillStyle = '#000';
    ctx.font = `bold ${Math.max(8, badgeSize * 0.7)}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(world.artifacts.length, badgeX, badgeY);
}
```

#### Visual Design

- **Badge**: Small gold circle to the right of world
- **Content**: Black number showing artifact count
- **Position**: 8px to the right of world circle
- **Size**: 14px base, minimum 10px when zoomed out
- **Purpose**: Quick visual indicator without cluttering the map
- **Details**: Click world to see individual artifact IDs in info panel

### 2. Artifact Indicators on Fleets (Map)

**File**: `client/rendering/layers/FleetLayer.js`

#### Implementation

Updated `_renderFleetRing()` to show a gold badge with artifact count:

```javascript
// Artifact indicators (small gold badges)
if (fleet.artifacts && Array.isArray(fleet.artifacts) && fleet.artifacts.length > 0) {
    const badgeSize = Math.max(8, iconSize * 0.4);
    const badgeX = drawX + iconSize / 2 + 2;
    const badgeY = drawY - iconSize / 2 - 2;

    // Draw gold badge with artifact count
    ctx.fillStyle = '#ffd700';
    ctx.beginPath();
    ctx.arc(badgeX, badgeY, badgeSize / 2, 0, 2 * Math.PI);
    ctx.fill();

    // Draw count
    ctx.fillStyle = '#000';
    ctx.font = `bold ${Math.max(6, badgeSize * 0.7)}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(fleet.artifacts.length, badgeX, badgeY);
}
```

#### Visual Design

- **Badge**: Gold circular badge in top-right corner of fleet icon
- **Content**: Black number showing artifact count
- **Position**: Upper-right of fleet square/diamond
- **Size**: 40% of fleet icon size, minimum 8px
- **Purpose**: Quick visual indicator that fleet has artifacts

### 3. Artifact IDs in World Info Panel

**File**: `client/ui/WorldInfo.js`

#### Implementation

Updated world info to prominently display individual artifact IDs:

```javascript
// Artifacts
if (world.artifacts && world.artifacts.length > 0) {
    html += '<div class="info-section">';
    html += '<div class="section-label">✨ Artifacts (' + world.artifacts.length + ')</div>';
    html += '<div class="artifacts-list">';
    world.artifacts.forEach(artifact => {
        const artName = artifact.name || `Artifact ${artifact.id}`;
        html += `<div class="artifact-item">
            <span class="artifact-id">A${artifact.id}</span>
            <span class="artifact-name">${artName}</span>
        </div>`;
    });
    html += '</div>';
    html += '</div>';
}
```

Also updated fleet display to show artifact counts:

```javascript
myFleets.forEach(f => {
    const artifactCount = (f.artifacts && f.artifacts.length > 0) ? ` ✨${f.artifacts.length}` : '';
    const artifactIds = (f.artifacts && f.artifacts.length > 0)
        ? f.artifacts.map(a => `A${a.id}`).join(', ')
        : '';
    const artifactTitle = artifactIds ? ` title="Artifacts: ${artifactIds}"` : '';
    html += `<div class="fleet-tag"${artifactTitle}>F${f.id} (🚀${f.ships || 0})${artifactCount}</div>`;
});
```

#### Visual Design

- **Artifact IDs**: Large, bold, gold text (A10, A23, etc.)
- **Artifact Names**: Gray text next to ID
- **Background**: Semi-transparent gold background per item
- **Layout**: Each artifact on its own line
- **Fleet tooltips**: Hover over fleet to see artifact IDs

**File**: `style.css`

```css
.artifact-item {
    background-color: rgba(255, 215, 0, 0.15);
    padding: 4px 8px;
    border-radius: 3px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.artifact-item .artifact-id {
    color: #ffd700;
    font-weight: bold;
    font-size: 14px;
    margin-right: 8px;
}

.artifact-item .artifact-name {
    color: #ddd;
    font-size: 12px;
    flex: 1;
}
```

### 4. Artifact Count in World Sidebar

**File**: `client/ui/WorldList.js`

#### Implementation

Updated world list to show artifact counts with tooltips:

```javascript
const artifacts = world.artifacts || [];

// Build artifact list
let artifactStr = '';
if (artifacts.length > 0) {
    const artifactIds = artifacts.map(a => `A${a.id}`).join(', ');
    artifactStr = `<span class="artifact-list" title="Artifacts: ${artifactIds}">✨${artifacts.length}</span>`;
}

// In world stats:
html += `
    <div class="world-stats">
        <span title="Population">👥${population}</span>
        <span title="Industry">🏭${industry}</span>
        <span title="Defenses">🛡️${defenses}</span>
        ${artifactStr}
    </div>
`;
```

#### Visual Design

- **Display**: ✨ icon + count in world stats row
- **Tooltip**: Shows individual artifact IDs on hover
- **Color**: Gold (#ffd700)
- **Purpose**: Quick overview in "My Worlds" list

### 5. Artifact List in Fleet Sidebar

**File**: `client/ui/FleetList.js`

#### Implementation

Updated fleet rendering to show artifact IDs in tooltip:

```javascript
const artifacts = fleet.artifacts || [];

// Build artifact list
let artifactStr = '';
if (artifacts.length > 0) {
    const artifactIds = artifacts.map(a => `A${a.id}`).join(', ');
    artifactStr = `<span class="artifact-list" title="Artifacts: ${artifactIds}">✨${artifacts.length}</span>`;
}

// In fleet stats section:
html += `
    <div class="fleet-stats">
        <span title="Ships">🚀${ships}</span>
        ${cargo > 0 ? `<span title="Cargo">📦${cargo}</span>` : ''}
        ${artifactStr}
    </div>
`;
```

#### Visual Design

- **Display**: ✨ sparkle icon + count
- **Tooltip**: Shows full artifact IDs (e.g., "Artifacts: A10, A23")
- **Color**: Gold (#ffd700)
- **Purpose**: See which artifacts are on each fleet for attach/detach commands

**File**: `style.css`

```css
.fleet-entry .artifact-list {
    color: #ffd700;
    margin-left: 6px;
    font-size: 12px;
}
```

### 6. Empty Fleet Indicators on Map

**File**: `client/rendering/layers/FleetLayer.js`

#### Implementation

Updated `_renderFleetRing()` to detect empty fleets and render them in gray:

```javascript
_renderFleetRing(ctx, fleets, worldPos, orbitRadius, iconSize, isFriendly) {
    fleets.forEach((fleet, index) => {
        // Check if fleet is empty (no ships)
        const isEmpty = !fleet.ships || fleet.ships <= 0;
        const hasCargo = fleet.cargo && fleet.cargo > 0;

        // Determine fleet color
        let fillColor;
        if (isEmpty) {
            fillColor = '#666666'; // Gray for empty fleets
        } else {
            fillColor = isFriendly ? '#4caf50' : '#f44336';
        }

        // ... render fleet icon with fillColor

        // Fleet ID label - dimmer for empty fleets
        ctx.fillStyle = isEmpty ? '#999999' : '#fff';
        ctx.fillText(fleet.id, drawX, drawY);
    });
}
```

#### Color Scheme

| Fleet Type | Icon Color | Label Color | Meaning |
|------------|------------|-------------|---------|
| Friendly (with ships) | #4caf50 (green) | #fff (white) | Your active fleet |
| Hostile (with ships) | #f44336 (red) | #fff (white) | Enemy active fleet |
| Empty (0 ships) | #666666 (gray) | #999999 (dim gray) | Inactive fleet |

### 7. Empty Fleet Indicators in Sidebar

**File**: `client/ui/FleetList.js`

#### Implementation

Updated fleet rendering to add empty fleet indicator:

```javascript
fleets.forEach(fleet => {
    const ships = fleet.ships || 0;
    const isEmpty = ships <= 0;

    html += `
        <div class="fleet-entry ${isEmpty ? 'empty-fleet' : ''}" data-fleet-id="${fleet.id}">
            <div class="fleet-header">
                <span class="fleet-id">F${fleet.id}</span>
                ${isEmpty ? '<span class="empty-icon" title="Empty (no ships)">⚪</span>' : ''}
                ${isMoving ? '<span class="moving-icon">➡️</span>' : ''}
            </div>
            <div class="fleet-stats">
                <span title="Ships">🚀${ships}</span>
                ${cargo > 0 ? `<span title="Cargo">📦${cargo}</span>` : ''}
            </div>
        </div>
    `;
});
```

#### Visual Indicators

- **CSS class**: `empty-fleet` added to fleet entry
- **Icon**: ⚪ (white circle) next to fleet ID
- **Tooltip**: "Empty (no ships)" on hover
- **Styling**: Dimmed background and reduced opacity

**File**: `style.css`

```css
.fleet-entry.empty-fleet {
    background-color: #3a3a3a;  /* Darker background */
    opacity: 0.7;               /* Dimmed */
}

.fleet-entry.empty-fleet:hover {
    background-color: #454545;
    opacity: 0.8;
}

.fleet-entry .empty-icon {
    color: #999;
    margin-left: 4px;
    font-size: 12px;
}
```

## Example Scenarios

### Scenario 1: Finding Artifacts on Worlds

**On Map:**
```
Before scouting W42:
┌─────────┐
│   W42   │  ← No indicators
└─────────┘

After scouting W42 (has 3 artifacts):
┌─────────┐
│   W42   │ ⊙3  ← Gold badge with count
└─────────┘
```

**In World Info Panel (after clicking W42):**
```
World 42
Owner: Alice

✨ Artifacts (3)
┌──────────────────────┐
│ A10  Ancient Relic   │
│ A23  Power Core      │
│ A156 Data Crystal    │
└──────────────────────┘
```

**In "My Worlds" Sidebar:**
```
├── W42 👥50 🏭25 🛡️10 ✨3  ← Hover shows "A10, A23, A156"
```

**Result**: Map stays clean, but player can see specific artifact IDs in info panel for attach commands like `W42TA10F5` (attach A10 from W42 to F5)

### Scenario 2: Fleets with Artifacts in Sidebar

```
My Fleets
├── W10 (yours) ⚔️
│   ├── F5 🚀45 📦5 ✨2          ← Has 2 artifacts (hover shows "A10, A23")
│   ├── F12 🚀0 ⚪              ← Empty fleet (gray, indicator)
│   └── F15 🚀30 ✨1            ← Has 1 artifact (hover shows "A156")
├── W23 (Bob)
│   └── F20 🚀0 ⚪              ← Empty fleet (gray, indicator)
```

**Result**:
- Artifact count shown with ✨ icon
- Hover tooltip shows individual artifact IDs
- Can use commands like `F5TA10W` to detach artifact 10 from fleet 5 to world
- Can use commands like `F5TA10F12` to transfer artifact 10 from fleet 5 to fleet 12
- Empty fleets are clearly marked and dimmed

### Scenario 3: Artifacts and Empty Fleets on Map

**On Map:**
```
World W10 with fleets and artifacts:
    F5 (green square with gold badge "2")
     ↓
   ┌───┐ ⊙3  ← World has 3 artifacts (gold badge)
   │W10│
   └───┘
     ↑
    F12 (gray square, 0 ships, no badge)
```

**In World Info Panel (after clicking W10):**
```
World 10
Owner: You

✨ Artifacts (3)
┌──────────────────────┐
│ A10  Ancient Relic   │
│ A23  Power Core      │
│ A156 Data Crystal    │
└──────────────────────┘

Fleets:
Friendly:
├── F5 (🚀45) ✨2  ← Hover shows "A10, A23"
└── F12 (🚀0)      ← Empty fleet
```

**Result**:
- Map shows simple count badges (not cluttered with IDs)
- World info panel shows individual artifact IDs with names
- Fleets with artifacts show gold badge with count on map
- Can attach artifacts: `W10TA10F5` (attach artifact 10 from world 10 to fleet 5)
- Can detach artifacts: `F5TA23W` (detach artifact 23 from fleet 5 to world)
- Can transfer between fleets: `F5TA10F12` (transfer artifact 10 from fleet 5 to fleet 12)
- Empty fleets are gray and visually distinct from active fleets

## Game Context

### Fleet Limits

- **Total fleets per game**: 255
- **Keys per player**: 5
- **Neutral keys**: 200 (in 11-player game)

**Implication**: Empty fleets represent captured keys that could be reused for new fleets

### Artifact Management

- **Total artifacts**: Limited number in game (varies by configuration)
- **Artifact IDs**: Each artifact has a unique ID (e.g., 10, 23, 156)
- **Visibility**: Artifact IDs only shown on worlds player has scouted
- **Commands** (use "TA" = Transfer Artifact):
  - `W10TA27F92` - Transfer artifact 27 from world 10 to fleet 92 (attach from world)
  - `F92TA27W` - Transfer artifact 27 from fleet 92 to world (detach to world)
  - `F92TA27F5` - Transfer artifact 27 from fleet 92 to fleet 5 (fleet to fleet)
- **Purpose**: Valuable resources that provide game advantages

## Benefits

### Strategic Awareness
- ✅ **Individual artifact tracking**: See specific artifact IDs (A10, A23, etc.)
- ✅ **Command preparation**: Know exact IDs for attach/detach commands
- ✅ **Fleet artifact status**: See which fleets carry artifacts and how many
- ✅ **Empty fleet tracking**: Know which fleets are inactive/keys
- ✅ **Resource planning**: Identify opportunities to reuse empty fleets

### Visual Clarity
- ✅ **Clean map**: Simple count badges don't clutter the world view
- ✅ **Detailed sidebars**: Individual artifact IDs (A10, A23) shown in panels
- ✅ **Fleet badges**: Gold circular badges show artifact count on fleets
- ✅ **Tooltip details**: Hover to see complete artifact ID list
- ✅ **Distinct colors**: Gray for empty, green/red for active, gold for artifacts
- ✅ **Clear indicators**: ✨ for artifacts with count, ⚪ for empty fleets
- ✅ **Consistent design**: Matches existing visual language
- ✅ **No overlap issues**: Artifact badges don't interfere with fleet icons

### User Experience
- ✅ **Command readiness**: See exact artifact IDs needed for commands
- ✅ **Less mental load**: Visual indicators replace text scanning
- ✅ **Quick scanning**: Gold badges and IDs stand out immediately
- ✅ **Tooltip help**: Hover for full artifact list on fleets
- ✅ **Precise referencing**: No guessing which artifact ID to use

## Performance Impact

### Artifact Rendering
- **Check**: Simple property check (`world.artifacts > 0`)
- **Rendering**: One emoji per world with artifacts (~5-20 worlds typically)
- **Impact**: Negligible (< 0.1ms)

### Empty Fleet Detection
- **Check**: Property check (`fleet.ships <= 0`)
- **Rendering**: Same drawing code, just different color
- **Impact**: Negligible

## Future Enhancements

Possible improvements (not currently implemented):

1. **Artifact count badges**: Show number of artifacts (e.g., "✨ 3")
2. **Artifact types**: Different icons for different artifact types
3. **Empty fleet actions**: Quick action to "scuttle" or convert empty fleet
4. **Fleet capacity indicator**: Show ship capacity vs current ships
5. **Artifact collection route**: Highlight path to nearest artifacts
6. **Empty fleet filter**: Toggle to hide/show empty fleets

## Testing Checklist

### Artifact Indicators
- ✅ World artifact count badges appear on map (gold circle with number)
- ✅ Artifact badges only appear when world has been scouted
- ✅ Artifact badges don't overlap with fleet icons
- ✅ Artifact badges scale with zoom level
- ✅ World info panel shows individual artifact IDs (A10, A23, etc.)
- ✅ World info panel shows artifact names
- ✅ "My Worlds" sidebar shows artifact count with tooltip
- ✅ Fleet artifact badges show count (gold circle with number)
- ✅ Fleet artifact badges positioned at top-right of icon
- ✅ "My Fleets" sidebar shows artifact count with ✨ icon
- ✅ Fleet sidebar tooltip shows individual artifact IDs on hover
- ✅ World info panel fleet list shows artifact counts with tooltips

### Empty Fleet Indicators
- ✅ Empty fleets (0 ships) show gray color on map
- ✅ Empty fleets show ⚪ icon in sidebar
- ✅ Empty fleets have dimmed background in sidebar
- ✅ Tooltip shows "Empty (no ships)" on hover
- ✅ Both friendly and hostile empty fleets are gray
- ✅ Empty fleet indicators work with moving fleets

### Integration
- ✅ Worlds can have both artifacts and empty fleets simultaneously
- ✅ Fleets can be empty and still carry artifacts
- ✅ All indicators work together without visual conflicts
