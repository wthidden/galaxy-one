# Help System Improvements

## Overview

The help system has been significantly enhanced with:
1. **HTML formatting** - Rich, styled help text with colors, sections, and better readability
2. **Context-sensitive help** - Get specific help for your fleets and worlds
3. **Better visual hierarchy** - Clear sections, color-coded categories, and command examples

## Features

### 1. HTML-Formatted Help

Help content now uses HTML for better presentation:

- **Color-coded sections**: Categories, examples, and notes have distinct colors
- **Styled headers**: Clear visual hierarchy with blue headers and borders
- **Code highlighting**: Command examples in monospace with blue highlighting
- **Organized layout**: Categories, examples, and notes are visually distinct

### 2. Context-Sensitive Help

Get specific help for your assets:

#### Fleet-Specific Help
```
HELP F5
```

Shows:
- Fleet's current location, ships, cargo, artifacts
- Relevant commands for that specific fleet (using fleet ID in examples)
- Only shows sections that apply (e.g., TRANSFER CARGO only if fleet has cargo)
- Lists artifacts attached to the fleet

Example output:
```
FLEET F5 COMMANDS
Location: Alpha | Ships: 23 | Cargo: 15/23 | Artifacts: 2

MOVEMENT
  F5W<id> - Move to connected world
  F5W<id>W<id>... - Multi-hop path

TRANSFER CARGO
  F5T15I - Convert all cargo to industry
  F5T15P - Convert all cargo to population
  F5T<amt>F<id> - Transfer ships to another fleet

COMBAT
  F5AF<id> - Attack enemy fleet
  F5AP - Fire at population | F5AI - Fire at industry
  F5A - Ambush mode (attack arriving fleets)

CARGO
  F5L - Load max cargo | F5L<amt> - Load amount
  F5U - Unload all | F5U<amt> - Unload amount

ARTIFACTS (2)
  A27, A45
  F5TA<id>W - Detach to world
  F5TA<id>F<id> - Transfer to another fleet
```

#### World-Specific Help
```
HELP W3
```

Shows:
- World's resources (population, industry, metal)
- Build commands specific to that world
- Artifacts at the world

Example output:
```
WORLD W3 (Alpha) COMMANDS
Location: Alpha | 👥 150 | 🏭 75 | 🔩 500 | ✨ 1 artifact

BUILD
  W3B<amt>I - Build industry (1 metal each)
  W3B<amt>P - Build PShips (2 metal each)
  W3B<amt>F<id> - Build ships to fleet (2 metal each)
  W3B<amt>LIMIT - Increase pop limit (10 metal each)
  W3B<amt>ROBOT - Convert pop to robots (20 metal each)

ARTIFACTS (1)
  A10
  W3TA<id>F<id> - Attach artifact to fleet
```

### 3. Traditional Topic-Based Help

Still works as before:

```
HELP              - Main help screen
HELP commands     - Command reference
HELP move         - Fleet movement details
HELP build        - Building & production
HELP transfer     - Cargo & transfers
HELP artifacts    - Artifact management
HELP combat       - Combat mechanics
HELP character    - Character types
```

## Usage Examples

### Getting Started
```
HELP              → Welcome screen + quick start
? button          → Same as HELP
```

### Learning Commands
```
HELP commands     → All commands reference
HELP move         → Movement mechanics
HELP build        → Building options
```

### Fleet Help
```
HELP F1           → Commands for fleet 1
HELP F92          → Commands for fleet 92
```

### World Help
```
HELP W1           → Commands for world 1
HELP W10          → Commands for world 10
```

## Visual Styling

### Color Scheme
- **Blue (#4da6ff)**: Headers, code, links
- **Gold (#ffd700)**: Category labels
- **Yellow (#ffc107)**: Important notes
- **Gray (#bbb/#888)**: Descriptions, footer text
- **Red (#f44336)**: Errors

### Sections
- **Header**: Bold blue title with underline
- **Category**: Gold label + command examples
- **Example**: Dark background with command + description
- **Note**: Yellow-highlighted box for important info
- **Footer**: Gray italics for additional topics

### Code Elements
- Monospace font (Courier New)
- Blue color (#4da6ff)
- Dark background
- Padding for readability

## Technical Details

### Server-Side Changes

#### `/server/game/help_content.py`
- Converted all help topics to HTML format
- Added `get_contextual_help(context)` function
- Modified `get_help(topic, context)` to support context parameter
- Fleet and world help generation with dynamic content

#### `/server/game/command_handlers.py`
- `handle_help()` now parses "HELP F5" and "HELP W3" syntax
- Extracts fleet/world from player's assets
- Builds context dict with fleet/world details
- Sends help as event message (supports HTML) instead of info message

### Client-Side Changes

#### `/home/whidden/Projects/starweb/style.css`
- Added comprehensive help styling classes
- `.event-help` - container for help messages
- `.help-header`, `.help-section`, `.help-category` - structure
- `.help-example`, `.help-note`, `.help-context` - content types
- Color scheme matches game UI

#### Message Handler
- Help messages sent as `event` type (uses innerHTML)
- Supports full HTML rendering in event log
- Existing markdown parser works alongside HTML

## Command Parsing

The help command now supports three formats:

1. **No argument**: `HELP` → Main help
2. **Topic argument**: `HELP move` → Topic-specific help
3. **Fleet/World argument**: `HELP F5` or `HELP W3` → Contextual help

### Parsing Logic
```python
if arg.startswith('F') and arg[1:].isdigit():
    # Fleet help - extract fleet ID, find fleet, build context
elif arg.startswith('W') and arg[1:].isdigit():
    # World help - extract world ID, find world, build context
else:
    # Topic help - treat as regular topic string
```

## Benefits

### For New Players
- **Easier to learn**: Visual formatting makes content scannable
- **Less overwhelming**: Context-sensitive help shows only relevant commands
- **Quick reference**: Color-coded sections easy to navigate

### For Experienced Players
- **Faster command lookup**: `HELP F5` instantly shows that fleet's commands
- **No guessing IDs**: Help shows current values (ships, cargo, artifacts)
- **Efficient workflow**: See available options without switching to docs

### For Development
- **Maintainable**: HTML content easier to update than ASCII art
- **Extensible**: Easy to add new help topics or sections
- **Consistent**: CSS ensures uniform styling across all help

## Future Enhancements

### Potential Improvements
1. **Client-side context detection**: Automatically detect selected fleet/world
2. **Interactive help**: Clickable command examples to auto-fill input
3. **Search functionality**: `HELP search <term>` to find commands
4. **Help hints**: Show relevant help when hovering UI elements
5. **Tutorial mode**: Step-by-step interactive guides for new players

### Advanced Features
- **History integration**: "Help on last command" feature
- **Error-triggered help**: Auto-show relevant help on command errors
- **Contextual tooltips**: Hover fleet/world to see quick command reference
- **Command builder UI**: Visual interface based on help content

## Testing

### Test Cases

1. **Basic help**: `HELP` should show main welcome screen
2. **Topic help**: `HELP move` should show movement details
3. **Fleet help**: `HELP F5` should show fleet 5's specific commands
4. **World help**: `HELP W3` should show world 3's specific commands
5. **Invalid topic**: `HELP invalid` should suggest available topics
6. **Invalid fleet**: `HELP F999` should fail gracefully
7. **HTML rendering**: All help should display with proper styling
8. **? button**: Should work same as `HELP` command

### Visual Testing

Check event log for:
- ✅ Blue headers with underlines
- ✅ Gold category labels
- ✅ Monospace blue code snippets
- ✅ Yellow-highlighted notes
- ✅ Proper spacing and alignment
- ✅ Readable text colors
- ✅ Consistent styling

## Documentation

### For Users
Include in game documentation:
- `HELP` - General help and topics
- `HELP <topic>` - Specific topic (move, build, etc.)
- `HELP F<id>` - Commands for specific fleet
- `HELP W<id>` - Commands for specific world
- `?` button - Quick help access

### For Developers
- Help content in `/server/game/help_content.py`
- Styling in `/home/whidden/Projects/starweb/style.css`
- Handler in `/server/game/command_handlers.py`
- HTML rendered via event messages in MessageHandler

## Summary

The enhanced help system provides:
- ✅ **Better formatting** - HTML with colors, sections, visual hierarchy
- ✅ **Context-sensitivity** - Fleet/world-specific command help
- ✅ **Improved UX** - Easier to learn, faster to reference
- ✅ **Maintainability** - Clean HTML structure, CSS styling
- ✅ **Extensibility** - Easy to add new help topics and features

Players can now get exactly the help they need, when they need it, in a visually appealing format.
