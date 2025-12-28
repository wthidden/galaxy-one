"""
Help content for the StarWeb game.
Provides command reference and game mechanics information with HTML formatting.
"""

HELP_TOPICS = {
    "commands": """
<div class="help-header">STARWEB COMMANDS</div>
<div class="help-section">
    <div class="help-category">
        <span class="help-label">BASIC</span>
        <code>HELP [topic]</code> Show help | <code>TURN</code> End turn<br>
        <code>JOIN &lt;name&gt; [type]</code> Join game<br>
        <code>SAY &lt;message&gt;</code> or <code>CHAT &lt;message&gt;</code> Send chat message
    </div>
    <div class="help-category">
        <span class="help-label">MOVE</span>
        <code>F5W10</code> Move to world | <code>F5W1W3W10</code> Multi-hop path
    </div>
    <div class="help-category">
        <span class="help-label">BUILD</span>
        <code>W3B25I</code> Industry | <code>W3B25P</code> PShips | <code>W3B10F7</code> Ships to fleet<br>
        <code>W3B5LIMIT</code> Population limit | <code>W3B10ROBOT</code> Convert to robots
    </div>
    <div class="help-category">
        <span class="help-label">TRANSFER</span>
        <code>F5T10I</code> Cargo→industry | <code>F5T10P</code> Cargo→population<br>
        <code>F5T10F7</code> Ships to fleet | <code>F5L</code> Load | <code>F5U</code> Unload
    </div>
    <div class="help-category">
        <span class="help-label">ARTIFACTS</span>
        <code>W10TA27F92</code> World→fleet | <code>F92TA27W</code> Fleet→world<br>
        <code>F92TA27F5</code> Fleet→fleet
    </div>
    <div class="help-category">
        <span class="help-label">COMBAT</span>
        <code>F5AF10</code> Fire at fleet | <code>F5AP</code> Fire at pop | <code>F5AI</code> Fire at industry<br>
        <code>F5A</code> Ambush mode
    </div>
</div>
<div class="help-footer">Type <code>HELP &lt;topic&gt;</code> for details: move, build, transfer, artifacts, combat, character</div>
""",

    "move": """
<div class="help-header">FLEET MOVEMENT</div>
<div class="help-section">
    <div class="help-example">
        <code>F5W10</code> <span class="help-desc">Move fleet 5 to world 10</span><br>
        <code>F5W1W3W10</code> <span class="help-desc">Multi-hop: move F5 through W1→W3→W10</span>
    </div>
    <div class="help-note">
        <strong>Requirements:</strong> Connected worlds, no existing MOVE/FIRE/AMBUSH order<br>
        <strong>Visual:</strong> Moving fleets show ➡️ in sidebar, animate on map<br>
        <strong>Note:</strong> Can be intercepted by ambushing fleets
    </div>
</div>
""",

    "build": """
<div class="help-header">BUILDING & PRODUCTION</div>
<div class="help-section">
    <div class="help-example">
        <code>W3B25I</code> <span class="help-desc">Build 25 industry (1 metal each)</span><br>
        <code>W3B25P</code> <span class="help-desc">Build 25 PShips (2 metal each)</span><br>
        <code>W3B10F7</code> <span class="help-desc">Build 10 ships to fleet 7 (2 metal each)</span><br>
        <code>W3B5LIMIT</code> <span class="help-desc">+5 population limit (10 metal each)</span><br>
        <code>W3B10ROBOT</code> <span class="help-desc">Convert 10 pop to robots (20 metal each)</span>
    </div>
    <div class="help-note">
        <strong>Production:</strong> Effective = min(Industry, Population)<br>
        <strong>Robots:</strong> Don't count against population limits
    </div>
</div>
""",

    "transfer": """
<div class="help-header">TRANSFERS & CARGO</div>
<div class="help-section">
    <div class="help-example">
        <code>F5T10F7</code> <span class="help-desc">Transfer 10 ships from F5 to F7 (cargo transfers proportionally)</span><br>
        <code>F5T10I</code> <span class="help-desc">Transfer 10 cargo to industry</span><br>
        <code>F5T10P</code> <span class="help-desc">Transfer 10 cargo to population</span><br>
        <code>F5L</code> <span class="help-desc">Load max cargo from world</span> | <code>F5L10</code> <span class="help-desc">Load 10 cargo</span><br>
        <code>F5U</code> <span class="help-desc">Unload all cargo to world</span> | <code>F5U10</code> <span class="help-desc">Unload 10 cargo</span>
    </div>
    <div class="help-note">
        <strong>Capacity:</strong> 1 cargo/ship (Merchants: 2 cargo/ship)<br>
        <strong>Note:</strong> Excess cargo jettisoned if target can't hold it
    </div>
</div>
""",

    "artifacts": """
<div class="help-header">ARTIFACTS</div>
<div class="help-section">
    <div class="help-intro">Powerful items with unique strategic advantages</div>
    <div class="help-example">
        <code>W10TA27F92</code> <span class="help-desc">Attach artifact 27 from world 10 to fleet 92</span><br>
        <code>F92TA27W</code> <span class="help-desc">Detach artifact 27 from fleet 92 to world</span><br>
        <code>F92TA27F5</code> <span class="help-desc">Transfer artifact 27 from fleet 92 to fleet 5</span>
    </div>
    <div class="help-note">
        <strong>Finding IDs:</strong> Click world→see ✨ Artifacts section→note ID (A10, A27, etc.)<br>
        <strong>Visual:</strong> Gold ⊙ badges on map show count, hover tooltips show IDs
    </div>
</div>
""",

    "combat": """
<div class="help-header">COMBAT</div>
<div class="help-section">
    <div class="help-example">
        <code>F5AF10</code> <span class="help-desc">Fire at enemy fleet 10</span><br>
        <code>F5AP</code> <span class="help-desc">Fire at world population</span><br>
        <code>F5AI</code> <span class="help-desc">Fire at world industry</span><br>
        <code>F5A</code> <span class="help-desc">Ambush mode (attack arriving fleets, get first strike)</span>
    </div>
    <div class="help-note">
        <strong>Exclusive:</strong> Only ONE of MOVE/FIRE/AMBUSH per fleet per turn<br>
        <strong>Mechanics:</strong> Damage based on ship count, IShips/PShips auto-defend
    </div>
</div>
""",

    "character": """
<div class="help-header">CHARACTER TYPES</div>
<div class="help-intro">Choose when joining: <code>JOIN Alice Empire Builder</code></div>
<div class="help-section">
    <div class="help-character">
        <span class="char-name">Empire Builder</span> Balanced, good for beginners (1 cargo/ship)
    </div>
    <div class="help-character">
        <span class="char-name">Merchant</span> 2x cargo capacity, resource control strategy
    </div>
    <div class="help-character">
        <span class="char-name">Pirate</span> Plunder bonus, aggressive raiding
    </div>
    <div class="help-character">
        <span class="char-name">Artifact Collector</span> Artifact bonuses, strategic control
    </div>
    <div class="help-character">
        <span class="char-name">Berserker</span> Combat bonus, military dominance
    </div>
    <div class="help-character">
        <span class="char-name">Apostle</span> Unique population (✝️), special mechanics
    </div>
</div>
<div class="help-note">
    <strong>Note:</strong> Cannot change after joining!
</div>
""",

    "main": """
<div class="help-header">STARWEB HELP</div>
<div class="help-intro">Welcome to StarWeb! Strategic space conquest.</div>
<div class="help-section">
    <div class="help-topics">
        <strong>HELP TOPICS:</strong> commands, move, build, transfer, artifacts, combat, character
    </div>
    <div class="help-category">
        <span class="help-label">QUICK START</span>
        1. <code>JOIN &lt;name&gt; &lt;type&gt;</code> Join game<br>
        2. Check sidebars for worlds/fleets<br>
        3. Click worlds for details<br>
        4. Issue orders (<code>F5W10</code>, <code>W3B25I</code>, etc.)<br>
        5. <code>TURN</code> when ready
    </div>
    <div class="help-category">
        <span class="help-label">INTERFACE</span>
        • Click worlds/fleets for info<br>
        • ⊙ badges = artifacts<br>
        • ⚔️ = conflict zones<br>
        • ➡️ = moving fleets<br>
        • Hover for tooltips
    </div>
    <div class="help-note">
        <strong>GAME FLOW:</strong> Issue orders → TURN → simultaneous execution → new turn
    </div>
</div>
"""
}

# Default help (when no topic specified)
HELP_TOPICS["help"] = HELP_TOPICS["main"]


def get_help(topic=None, context=None):
    """
    Get help content for a specific topic with optional context-sensitivity.

    Args:
        topic: Help topic (e.g., 'commands', 'move', 'build')
               If None, returns main help
        context: Optional context dict with:
               - 'selected_fleet': Fleet object if a fleet is selected
               - 'selected_world': World object if a world is selected
               - 'player': Player object for customization

    Returns:
        Help text string with HTML formatting
    """
    # If context provided and no specific topic, give contextual help
    if context and not topic:
        return get_contextual_help(context)

    if not topic:
        return HELP_TOPICS["main"]

    topic_lower = topic.lower()

    if topic_lower in HELP_TOPICS:
        return HELP_TOPICS[topic_lower]

    # If topic not found, suggest available topics
    available = ", ".join(sorted([t for t in HELP_TOPICS.keys() if t != "help"]))
    return f"""
<div class="help-header">UNKNOWN TOPIC</div>
<div class="help-section">
    <div class="help-error">Unknown help topic: <strong>{topic}</strong></div>
    <div class="help-note">
        <strong>Available topics:</strong> {available}<br>
        Type <code>HELP</code> for main help or <code>HELP &lt;topic&gt;</code> for specific help.
    </div>
</div>
"""


def get_contextual_help(context):
    """
    Get context-sensitive help based on what's selected or game state.

    Args:
        context: Dict with selected_fleet, selected_world, and/or player

    Returns:
        HTML help string customized to context
    """
    fleet = context.get('selected_fleet')
    world = context.get('selected_world')
    player = context.get('player')

    # Fleet selected - show fleet commands
    if fleet:
        fleet_id = fleet.get('id', '?')
        location = fleet.get('key', 'Unknown')
        ships = fleet.get('ships', 0)
        cargo = fleet.get('cargo', 0)
        max_cargo = ships * (2 if player and player.character_type == "Merchant" else 1)
        artifacts = fleet.get('artifacts', [])

        help_html = f"""
<div class="help-header">FLEET F{fleet_id} COMMANDS</div>
<div class="help-section">
    <div class="help-context">
        <strong>Location:</strong> {location} | <strong>Ships:</strong> {ships} | <strong>Cargo:</strong> {cargo}/{max_cargo}
        {f' | <strong>Artifacts:</strong> {len(artifacts)}' if artifacts else ''}
    </div>
    <div class="help-category">
        <span class="help-label">MOVEMENT</span>
        <code>F{fleet_id}W&lt;id&gt;</code> Move to connected world<br>
        <code>F{fleet_id}W&lt;id&gt;W&lt;id&gt;...</code> Multi-hop path
    </div>
"""

        if cargo > 0:
            help_html += f"""
    <div class="help-category">
        <span class="help-label">TRANSFER CARGO</span>
        <code>F{fleet_id}T{cargo}I</code> Convert all cargo to industry<br>
        <code>F{fleet_id}T{cargo}P</code> Convert all cargo to population<br>
        <code>F{fleet_id}T&lt;amt&gt;F&lt;id&gt;</code> Transfer ships to another fleet
    </div>
"""

        if ships > 0:
            help_html += f"""
    <div class="help-category">
        <span class="help-label">COMBAT</span>
        <code>F{fleet_id}AF&lt;id&gt;</code> Attack enemy fleet<br>
        <code>F{fleet_id}AP</code> Fire at population | <code>F{fleet_id}AI</code> Fire at industry<br>
        <code>F{fleet_id}A</code> Ambush mode (attack arriving fleets)
    </div>
"""

        help_html += f"""
    <div class="help-category">
        <span class="help-label">CARGO</span>
        <code>F{fleet_id}L</code> Load max cargo | <code>F{fleet_id}L&lt;amt&gt;</code> Load amount<br>
        <code>F{fleet_id}U</code> Unload all | <code>F{fleet_id}U&lt;amt&gt;</code> Unload amount
    </div>
"""

        if artifacts:
            art_ids = ", ".join([f"A{a.get('id', '?')}" for a in artifacts])
            help_html += f"""
    <div class="help-category">
        <span class="help-label">ARTIFACTS ({len(artifacts)})</span>
        {art_ids}<br>
        <code>F{fleet_id}TA&lt;id&gt;W</code> Detach to world<br>
        <code>F{fleet_id}TA&lt;id&gt;F&lt;id&gt;</code> Transfer to another fleet
    </div>
"""

        help_html += """
</div>
<div class="help-footer">Type <code>HELP &lt;topic&gt;</code> for more: move, transfer, artifacts, combat</div>
"""
        return help_html

    # World selected - show world commands
    elif world:
        world_id = world.get('id', '?')
        name = world.get('name', 'Unknown')
        population = world.get('population', 0)
        industry = world.get('industry', 0)
        key = world.get('key', 'Unknown')
        metal = world.get('metal', 0)
        artifacts = world.get('artifacts', [])

        help_html = f"""
<div class="help-header">WORLD W{world_id} ({name}) COMMANDS</div>
<div class="help-section">
    <div class="help-context">
        <strong>Location:</strong> {key} | 👥 {population} | 🏭 {industry} | 🔩 {metal}
        {f' | ✨ {len(artifacts)} artifacts' if artifacts else ''}
    </div>
    <div class="help-category">
        <span class="help-label">BUILD</span>
        <code>W{world_id}B&lt;amt&gt;I</code> Build industry (1 metal each)<br>
        <code>W{world_id}B&lt;amt&gt;P</code> Build PShips (2 metal each)<br>
        <code>W{world_id}B&lt;amt&gt;F&lt;id&gt;</code> Build ships to fleet (2 metal each)<br>
        <code>W{world_id}B&lt;amt&gt;LIMIT</code> Increase pop limit (10 metal each)<br>
        <code>W{world_id}B&lt;amt&gt;ROBOT</code> Convert pop to robots (20 metal each)
    </div>
"""

        if artifacts:
            art_ids = ", ".join([f"A{a.get('id', '?')}" for a in artifacts])
            help_html += f"""
    <div class="help-category">
        <span class="help-label">ARTIFACTS ({len(artifacts)})</span>
        {art_ids}<br>
        <code>W{world_id}TA&lt;id&gt;F&lt;id&gt;</code> Attach artifact to fleet
    </div>
"""

        help_html += """
</div>
<div class="help-footer">Type <code>HELP &lt;topic&gt;</code> for more: build, artifacts</div>
"""
        return help_html

    # No specific context - return main help
    return HELP_TOPICS["main"]
