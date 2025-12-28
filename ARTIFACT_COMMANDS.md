# Artifact Transfer Commands

## Command Format

All artifact commands use **"TA"** (Transfer Artifact) with the format:
```
<SOURCE>TA<ARTIFACT_ID><DESTINATION>
```

## Command Types

### 1. Attach Artifact from World to Fleet
**Format**: `W<worldId>TA<artifactId>F<fleetId>`

**Example**: `W10TA27F92`
- Transfer artifact 27 from world 10 to fleet 92

**Requirements**:
- Fleet must be at the world
- You must own the world
- You must own the fleet
- Artifact must be on the world

### 2. Detach Artifact from Fleet to World
**Format**: `F<fleetId>TA<artifactId>W`

**Example**: `F92TA27W`
- Transfer artifact 27 from fleet 92 to the world it's orbiting

**Requirements**:
- You must own the fleet
- Fleet must be at a world (not in transit)
- Artifact must be on the fleet

### 3. Transfer Artifact Between Fleets
**Format**: `F<sourceFleetId>TA<artifactId>F<targetFleetId>`

**Example**: `F92TA27F5`
- Transfer artifact 27 from fleet 92 to fleet 5

**Requirements**:
- Both fleets must be at the same world
- You must own both fleets
- Artifact must be on the source fleet

## Finding Artifact IDs

### On the Map
- **Worlds**: Gold badge shows count (e.g., ⊙3)
- **Fleets**: Gold badge shows count (e.g., gold circle with "2")

### In World Info Panel (click a world)
```
✨ Artifacts (3)
┌──────────────────────┐
│ A10  Ancient Relic   │  ← Artifact ID is A10
│ A23  Power Core      │  ← Artifact ID is A23
│ A156 Data Crystal    │  ← Artifact ID is A156
└──────────────────────┘
```

### In "My Worlds" Sidebar
- Hover over the ✨ icon to see artifact IDs
- Tooltip shows: "Artifacts: A10, A23, A156"

### In "My Fleets" Sidebar
- Hover over the ✨ icon to see artifact IDs
- Tooltip shows: "Artifacts: A10, A23"

## Step-by-Step Example

**Goal**: Attach artifact 27 from world 10 to fleet 92

1. **Click on world 10** to open the world info panel
2. **Find artifact 27** in the artifacts list:
   ```
   ✨ Artifacts (2)
   ┌──────────────────────┐
   │ A27  Mystery Box     │  ← This is the one!
   │ A35  Power Source    │
   └──────────────────────┘
   ```
3. **Verify fleet 92 is at world 10** (check "Fleets:" section in world info)
4. **Type the command**: `W10TA27F92`
5. **Submit** and verify: "Order queued: Transfer artifact 27 from world 10 to fleet 92"

## Common Mistakes

❌ **Wrong**: `F92AA27` (uses "AA" instead of "TA")
✅ **Right**: `W10TA27F92`

❌ **Wrong**: `F92TA27` (missing destination)
✅ **Right**: `F92TA27W` (to world) or `F92TA27F5` (to fleet 5)

❌ **Wrong**: `TA27F92` (missing source)
✅ **Right**: `W10TA27F92` (from world 10)

## Server-Side Validation

The server validates:
- ✅ Source exists (world or fleet)
- ✅ Destination exists (world or fleet)
- ✅ You own the source and destination
- ✅ Artifact exists on the source
- ✅ Fleets are at the same location
- ✅ Fleet is not in transit (for fleet commands)

If validation fails, you'll see an error message explaining the issue.
