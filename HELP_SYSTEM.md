# Help System Documentation

## Overview

The StarWeb game now includes a comprehensive in-game help system accessible via the `HELP` command or the **?** button in the UI.

## Features

### Command-Based Help
Players can type `HELP` or `HELP <topic>` in the command input to get detailed information about:
- All available commands
- Specific game mechanics
- Character types
- Combat system
- Artifact management

### Help Button
A **?** button is located next to the Send button in the command input area. Clicking it sends the `HELP` command automatically.

## Available Help Topics

### Main Help (`HELP` or `?`)
Shows:
- Welcome message
- List of all help topics
- Quick start guide
- Game flow explanation
- Interface tips

### Commands (`HELP commands`)
Complete command reference including:
- Basic commands (HELP, TURN, JOIN)
- Fleet movement
- Building
- Transfers
- Artifacts
- Combat

### Movement (`HELP move`)
Detailed information about:
- Basic movement (F5W10)
- Multi-hop paths (F5W1W3W10)
- Requirements
- Visual indicators

### Building (`HELP build`)
Building and production mechanics:
- Industry (W3B25I)
- PShips (W3B25P)
- Ships to fleet (W3B10F7)
- Population limit (W3B5LIMIT)
- Robot conversion (W3B10ROBOT)
- Production formulas

### Transfer (`HELP transfer`)
Transfer and cargo management:
- Ship transfers (F5T10F7)
- Cargo to industry (F5T10I)
- Cargo to population (F5T10P)
- Load cargo (F5L)
- Unload cargo (F5U)
- Capacity mechanics

### Artifacts (`HELP artifacts`)
Artifact system:
- What artifacts are
- How to find them
- Attach from world (W10TA27F92)
- Detach to world (F92TA27W)
- Transfer between fleets (F92TA27F5)
- Visual indicators

### Combat (`HELP combat`)
Combat mechanics:
- Fire at fleet (F5AF10)
- Fire at population (F5AP)
- Fire at industry (F5AI)
- Ambush mode (F5A)
- Exclusive orders
- Combat calculations

### Character Types (`HELP character`)
Character classes:
- Empire Builder (balanced)
- Merchant (2x cargo)
- Pirate (plunder bonus)
- Artifact Collector (artifact bonuses)
- Berserker (combat bonus)
- Apostle (unique population)

## Implementation

### Server-Side

**File**: `server/game/help_content.py`
- Contains all help text organized by topic
- `get_help(topic)` function returns formatted help text
- Supports multi-word topics

**File**: `server/game/command_handlers.py`
- `handle_help(player, parts)` function processes HELP commands
- Available to all players (even before joining)
- Sends help text as info message

### Client-Side

**File**: `index.html`
- Added `?` help button next to Send button
- Updated placeholder to mention HELP command

**File**: `style.css`
- Styled help button with gray background (#6c757d)
- Hover effect for better UX

**File**: `client/main.js`
- Help button click handler sends "HELP" command
- Uses existing WebSocket command infrastructure

## Usage Examples

### Getting General Help
```
HELP
```
or click the **?** button

Result: Shows main help screen with topic list and quick start guide

### Getting Command Reference
```
HELP commands
```

Result: Complete command syntax reference

### Getting Specific Topic Help
```
HELP artifacts
```

Result: Detailed artifact system explanation with examples

### Shorthand
```
?
```

Result: Same as `HELP` (shows main help)

## Help Text Format

Help text uses:
- **Box drawing characters** for visual structure
- **Section headers** with `═══` separators
- **Examples** with actual command syntax
- **Requirements** for each command
- **Notes** for important details

Example format:
```
═══════════════════════════════════════════════════════
                    TOPIC NAME
═══════════════════════════════════════════════════════

SECTION 1
---------
Description...

Example: F5W10
  - Explanation

Requirements:
  - Requirement 1
  - Requirement 2

SECTION 2
---------
...
═══════════════════════════════════════════════════════
```

## Adding New Help Topics

To add a new help topic:

1. **Edit** `server/game/help_content.py`
2. **Add entry** to `HELP_TOPICS` dictionary:
   ```python
   "newtopic": """
   ═══════════════════════════════════════════════════════
                       NEW TOPIC
   ═══════════════════════════════════════════════════════

   Your content here...

   ═══════════════════════════════════════════════════════
   """
   ```
3. **Update main help** to list the new topic
4. **Test** with `HELP newtopic`

## Benefits

### For New Players
- ✅ Quick reference without leaving the game
- ✅ Examples for every command type
- ✅ Clear explanations of game mechanics
- ✅ Character type comparison

### For Experienced Players
- ✅ Command syntax reminder
- ✅ Artifact command format reference
- ✅ Combat mechanics details
- ✅ Production formulas

### For Development
- ✅ Single source of truth for command docs
- ✅ Easy to update and maintain
- ✅ Consistent formatting
- ✅ Extensible topic system

## Future Enhancements

Possible improvements:
1. **Interactive help** - Clickable command examples that fill the input
2. **Search function** - `HELP SEARCH <keyword>`
3. **Context-sensitive help** - Different help based on selected fleet/world
4. **Help history** - Recently viewed topics
5. **Tooltips** - Inline help for UI elements
6. **Tutorial mode** - Step-by-step guided tour
7. **Video tutorials** - Embedded video guides
8. **Help panel** - Dedicated sidebar panel instead of event log

## Testing

To test the help system:

1. **Start the game**: Launch server and client
2. **Before joining**: Type `HELP` - should work
3. **Click help button**: Should send HELP command
4. **Try each topic**:
   - `HELP commands`
   - `HELP move`
   - `HELP build`
   - `HELP transfer`
   - `HELP artifacts`
   - `HELP combat`
   - `HELP character`
5. **Try invalid topic**: `HELP invalid` - should show available topics
6. **Check formatting**: Help text should display properly in event log

## Notes

- Help is available **before** joining the game
- Help can be accessed via command or UI button
- All help text is formatted for monospace display
- Help topics are case-insensitive
- Unknown topics suggest valid alternatives
