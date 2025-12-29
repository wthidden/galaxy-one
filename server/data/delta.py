"""
Delta calculation for efficient state updates.
"""


def calculate_state_delta(old_state: dict, new_state: dict) -> dict:
    """
    Calculate what changed between two states.

    Args:
        old_state: Previous state snapshot
        new_state: Current state snapshot

    Returns:
        Dict containing only changed fields, or empty dict if no changes
    """
    delta = {}

    # Check top-level simple fields
    for key in ["score", "game_turn", "players_ready", "total_players"]:
        if old_state.get(key) != new_state.get(key):
            delta[key] = new_state[key]

    # Check orders
    if old_state.get("orders") != new_state.get("orders"):
        delta["orders"] = new_state["orders"]

    # Check worlds - only include changed worlds
    old_worlds = old_state.get("worlds", {})
    new_worlds = new_state.get("worlds", {})

    changed_worlds = {}
    for wid, world_data in new_worlds.items():
        if wid not in old_worlds or old_worlds[wid] != world_data:
            changed_worlds[wid] = world_data

    # Check for removed worlds
    removed_worlds = []
    for wid in old_worlds:
        if wid not in new_worlds:
            removed_worlds.append(wid)

    if changed_worlds:
        delta["worlds"] = changed_worlds
    if removed_worlds:
        delta["removed_worlds"] = removed_worlds

    # Check fleets - only include changed fleets
    old_fleets = {f["id"]: f for f in old_state.get("fleets", [])}
    new_fleets = {f["id"]: f for f in new_state.get("fleets", [])}

    changed_fleets = []
    for fid, fleet_data in new_fleets.items():
        if fid not in old_fleets or old_fleets[fid] != fleet_data:
            changed_fleets.append(fleet_data)

    # Check for removed fleets
    removed_fleet_ids = []
    for fid in old_fleets:
        if fid not in new_fleets:
            removed_fleet_ids.append(fid)

    if changed_fleets:
        delta["fleets"] = changed_fleets
    if removed_fleet_ids:
        delta["removed_fleets"] = removed_fleet_ids

    return delta if delta else {}
