import asyncio
import websockets
import json
import random
import http.server
import socketserver
import threading
import os
import math
import re
import time
from typing import Type

# Game Constants
MAP_SIZE = 255
INITIAL_TURN_DURATION = 180  # 3 minutes
MAX_TURN_DURATION = 480      # 8 minutes

# Homeworld Starting Conditions
HOMEWORLD_POPULATION = 50
HOMEWORLD_INDUSTRY = 30
HOMEWORLD_METAL = 30
HOMEWORLD_MINES = 2
HOMEWORLD_ISHIPS = 1
HOMEWORLD_PSHIPS = 1
HOMEWORLD_STARTING_SHIPS = 10

game_turn = 0
current_turn_duration = INITIAL_TURN_DURATION
turn_end_time = 0
players_ready = set()

CHARACTER_TYPES = ["Empire Builder", "Merchant", "Pirate", "Artifact Collector", "Berserker", "Apostle"]

# Orders that cannot coexist for a single fleet in a single turn
EXCLUSIVE_ORDER_TYPES = {"MOVE", "FIRE", "AMBUSH"}


class Artifact:
    def __init__(self, artifact_id, name):
        self.id = artifact_id
        self.name = name

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class World:
    def __init__(self, world_id):
        self.id = world_id
        self.connections = []
        self.owner = None
        self.industry = 0
        self.metal = 0
        self.mines = 0
        self.population = 0
        self.limit = 0
        self.iships = 0
        self.pships = 0
        self.fleets = []
        self.artifacts = []
        self.key = False  # True if this is a player's homeworld
        self.population_type = "human"  # "human", "robot", "apostle"
        self.plundered = False  # True if world has been plundered this turn
        self.planet_buster = False  # True if planet buster bomb has been dropped

    def to_dict(self, viewer=None, turn_last_seen=None):
        data = {
            "id": self.id,
            "connections": self.connections,
            "turn_last_seen": turn_last_seen
        }

        data["owner"] = self.owner.name if self.owner else None

        is_visible_now = False
        if viewer:
            if self.owner == viewer:
                is_visible_now = True
            else:
                for f in self.fleets:
                    if f.owner == viewer:
                        is_visible_now = True
                        break

        if is_visible_now:
            data.update({
                "industry": self.industry,
                "metal": self.metal,
                "mines": self.mines,
                "population": self.population,
                "limit": self.limit,
                "iships": self.iships,
                "pships": self.pships,
                "key": self.key,  # Homeworld marker
                "population_type": self.population_type,  # "human", "robot", "apostle"
                "plundered": self.plundered,  # Plundered status
                "planet_buster": self.planet_buster,  # Planet buster bomb status
                "fleets": [f.id for f in self.fleets],
                "artifacts": [a.to_dict() for a in self.artifacts]
            })
        else:
            data.update({
                "industry": "?", "metal": "?", "mines": "?",
                "population": "?", "limit": "?", "iships": "?", "pships": "?",
                "fleets": [],
                "artifacts": []
            })

        return data


class Fleet:
    def __init__(self, fleet_id, owner, world):
        self.id = fleet_id
        self.owner = owner
        self.world = world
        self.ships = 0
        self.cargo = 0
        self.moved = False
        self.is_ambushing = False
        self.artifacts = []
        world.fleets.append(self)

    def to_dict(self, viewer=None):
        data = {
            "id": self.id,
            "owner": self.owner.name if self.owner else "[Neutral]",
            "world": self.world.id,
            "moved": self.moved,
            "is_ambushing": self.is_ambushing,
            "artifacts": [a.to_dict() for a in self.artifacts]
        }

        if viewer == self.owner:
            data["ships"] = self.ships
            data["cargo"] = self.cargo
        else:
            data["ships"] = self.ships
            data["cargo"] = "?"

        return data


class Player:
    def __init__(self, player_id, name, websocket):
        self.id = player_id
        self.name = name
        self.websocket = websocket
        self.score = 0
        self.character_type = "Empire Builder"
        self.fleets = []
        self.worlds = []
        self.known_worlds = {}
        self.orders = []
        self.last_state_snapshot = None  # Track last sent state for delta calculation


# Game State
worlds = {}
fleets = {}
artifacts = {}
players = {}
next_player_id = 1


def init_game():
    global worlds, fleets, artifacts, turn_end_time

    for i in range(1, MAP_SIZE + 1):
        w = World(i)
        w.industry = random.randint(0, 10)
        w.mines = random.randint(0, 10)
        w.limit = random.randint(10, 50)
        w.population = random.randint(0, w.limit)
        worlds[i] = w

    for i in range(1, MAP_SIZE + 1):
        num_connections = random.randint(2, 4)
        while len(worlds[i].connections) < num_connections:
            target = random.randint(1, MAP_SIZE)
            if target != i and target not in worlds[i].connections:
                worlds[i].connections.append(target)
                worlds[target].connections.append(i)

    for i in range(1, 256):
        w = worlds[random.randint(1, MAP_SIZE)]
        f = Fleet(i, None, w)
        fleets[i] = f

    aid = 1
    types = [
        "Platinum", "Ancient", "Vegan", "Blessed", "Arcturian",
        "Silver", "Titanium", "Gold", "Radiant", "Plastic"
    ]
    items = [
        "Lodestar", "Pyramid", "Stardust", "Shekel", "Crown",
        "Sword", "Moonstone", "Sepulchre", "Sphinx"
    ]

    for t in types:
        for item in items:
            name = f"{t} {item}"
            a = Artifact(aid, name)
            artifacts[aid] = a
            aid += 1
            w = worlds[random.randint(1, MAP_SIZE)]
            w.artifacts.append(a)

    specials = [
        "Treasure of Polaris", "Slippers of Venus", "Radioactive Isotope",
        "Lesser of Two Evils", "Black Box"
    ]
    for i in range(1, 6):
        specials.append(f"Nebula Scroll {i}")

    for name in specials:
        a = Artifact(aid, name)
        artifacts[aid] = a
        aid += 1
        w = worlds[random.randint(1, MAP_SIZE)]
        w.artifacts.append(a)

    turn_end_time = time.time() + current_turn_duration
    print(f"Game initialized: Turn {game_turn}, first turn will process in {current_turn_duration}s")


init_game()
print("Server starting...")


async def register(websocket):
    global next_player_id
    player_id = next_player_id
    next_player_id += 1

    name = f"Player_{player_id}"
    player = Player(player_id, name, websocket)
    players[websocket] = player

    await websocket.send(json.dumps({
        "type": "welcome",
        "id": player.id,
        "name": player.name
    }))


async def join_game(player, name, char_type):
    player.name = name
    if char_type in CHARACTER_TYPES:
        player.character_type = char_type
    else:
        player.character_type = "Empire Builder"

    candidates = [w for w in worlds.values() if w.owner is None]
    if candidates:
        start_world = random.choice(candidates)
    else:
        start_world = worlds[random.randint(1, MAP_SIZE)]

    if start_world.owner:
        start_world.owner.worlds.remove(start_world)

    # Relocate any existing neutral fleets from the start world
    existing_fleets = [f for f in start_world.fleets if f.owner is None]
    for f in existing_fleets:
        start_world.fleets.remove(f)
        new_world = worlds[random.randint(1, MAP_SIZE)]
        while new_world == start_world:
            new_world = worlds[random.randint(1, MAP_SIZE)]
        f.world = new_world
        new_world.fleets.append(f)

    # Standardize homeworld stats
    start_world.owner = player
    start_world.population = HOMEWORLD_POPULATION
    start_world.industry = HOMEWORLD_INDUSTRY
    start_world.metal = HOMEWORLD_METAL
    start_world.mines = HOMEWORLD_MINES
    start_world.iships = HOMEWORLD_ISHIPS
    start_world.pships = HOMEWORLD_PSHIPS
    start_world.key = True  # Mark as homeworld
    player.worlds.append(start_world)

    player.known_worlds[start_world.id] = game_turn
    for neighbor in start_world.connections:
        player.known_worlds[neighbor] = game_turn

    neutral_keys = [
        f for f in fleets.values()
        if f.owner is None and f.world != start_world
    ]

    if len(neutral_keys) >= 5:
        keys_to_assign = random.sample(neutral_keys, 5)
    else:
        keys_to_assign = neutral_keys

    for f in keys_to_assign:
        f.world.fleets.remove(f)
        f.world = start_world
        start_world.fleets.append(f)
        f.owner = player
        player.fleets.append(f)
        f.ships = HOMEWORLD_STARTING_SHIPS

    await send_info(
        player,
        f"Welcome, {name}! You are a {player.character_type} "
        f"starting at World {start_world.id}."
    )

    # Broadcast update to ALL players to update player count
    for p in players.values():
        await send_update(p)


async def unregister(websocket):
    if websocket in players:
        del players[websocket]
    if websocket in players_ready:
        players_ready.remove(websocket)

    # Broadcast update to remaining players
    for p in players.values():
        await send_update(p)


def format_order(order):
    type = order["type"]
    if type == "MOVE":
        return f"Move F{order['fleet_id']} -> W{order['path'][-1]}"
    elif type == "BUILD":
        target_type = order["target_type"]
        amt = order["amount"]
        wid = order["world_id"]

        if order.get("target_id"):
            target = f"F{order['target_id']}"
        elif target_type == "I":
            target = "IShips"
        elif target_type == "P":
            target = "PShips"
        elif target_type == "INDUSTRY":
            target = "Industry"
        elif target_type == "LIMIT":
            target = "Pop Limit"
        elif target_type == "ROBOT":
            target = "Robots"
        else:
            target = target_type

        return f"Build {amt} {target} at W{wid}"
    elif type == "MIGRATE":
        return (
            f"Migrate {order['amount']} population from "
            f"W{order['world_id']} to W{order['dest_world']}"
        )
    elif type == "TRANSFER":
        target = (
            f"F{order['target_id']}"
            if order["target_id"]
            else order["target_type"]
        )
        return (
            f"Transfer {order['amount']} from "
            f"F{order['fleet_id']} to {target}"
        )
    elif type == "LOAD":
        amt = order['amount']
        if amt is None:
            return f"F{order['fleet_id']} Load Max"
        else:
            return f"F{order['fleet_id']} Load {amt}"
    elif type == "UNLOAD":
        amt = order['amount']
        if amt is None:
            return f"F{order['fleet_id']} Unload All"
        else:
            return f"F{order['fleet_id']} Unload {amt}"
    elif type == "FIRE":
        target = (
            f"F{order['target_id']}"
            if order.get("target_id")
            else f"World {order['sub_target']}"
        )
        return f"F{order['fleet_id']} Fire at {target}"
    elif type == "AMBUSH":
        return f"F{order['fleet_id']} Ambush"
    return "Unknown Order"


async def send_update(player, force_full=False):
    visible_worlds = {}

    presence_worlds = set()
    for w in player.worlds:
        presence_worlds.add(w.id)
    for f in player.fleets:
        presence_worlds.add(f.world.id)

    for wid in presence_worlds:
        player.known_worlds[wid] = game_turn
        for n in worlds[wid].connections:
            if n not in player.known_worlds:
                player.known_worlds[n] = game_turn

    for wid, turn in player.known_worlds.items():
        visible_worlds[wid] = worlds[wid].to_dict(
            viewer=player,
            turn_last_seen=turn
        )

    visible_fleets = []
    for f in fleets.values():
        if f.owner == player or f.world.id in presence_worlds:
            visible_fleets.append(f.to_dict(viewer=player))

    time_remaining = max(0, int(turn_end_time - time.time()))
    formatted_orders = [format_order(o) for o in player.orders]

    # Build player list with ready status
    players_list = []
    for p in players.values():
        players_list.append({
            "name": p.name,
            "score": p.score,
            "character_type": p.character_type,
            "ready": p.websocket in players_ready
        })

    current_state = {
        "worlds": visible_worlds,
        "fleets": visible_fleets,
        "player_name": player.name,
        "character_type": player.character_type,
        "score": player.score,
        "game_turn": game_turn,
        "time_remaining": time_remaining,
        "players_ready": len(players_ready),
        "total_players": len(players),
        "players": players_list,
        "orders": formatted_orders
    }

    # Send full update if forced, first update, or no previous snapshot
    if force_full or player.last_state_snapshot is None:
        await player.websocket.send(json.dumps({"type": "update", "state": current_state}))
        player.last_state_snapshot = current_state
    else:
        # Calculate delta
        delta = calculate_state_delta(player.last_state_snapshot, current_state)
        if delta:
            await player.websocket.send(json.dumps({"type": "delta", "changes": delta}))
        player.last_state_snapshot = current_state


def calculate_state_delta(old_state, new_state):
    """Calculate what changed between two states."""
    delta = {}

    # Check top-level simple fields
    for key in ["score", "game_turn", "players_ready", "total_players"]:
        if old_state.get(key) != new_state.get(key):
            delta[key] = new_state[key]

    # Check orders
    if old_state.get("orders") != new_state.get("orders"):
        delta["orders"] = new_state["orders"]

    # Check players list (includes ready status)
    if old_state.get("players") != new_state.get("players"):
        delta["players"] = new_state["players"]

    # Check worlds - only include changed worlds
    old_worlds = old_state.get("worlds", {})
    new_worlds = new_state.get("worlds", {})

    changed_worlds = {}
    for wid, world_data in new_worlds.items():
        if wid not in old_worlds or old_worlds[wid] != world_data:
            changed_worlds[wid] = world_data

    # Check for removed worlds
    for wid in old_worlds:
        if wid not in new_worlds:
            if "removed_worlds" not in delta:
                delta["removed_worlds"] = []
            delta["removed_worlds"].append(wid)

    if changed_worlds:
        delta["worlds"] = changed_worlds

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

    return delta if delta else None


async def send_error(player, message):
    await player.websocket.send(json.dumps({
        "type": "error",
        "text": message
    }))


async def send_info(player, message):
    await player.websocket.send(json.dumps({
        "type": "info",
        "text": message
    }))


async def send_event(player, message, type="info"):
    await player.websocket.send(json.dumps({
        "type": "event",
        "text": message,
        "event_type": type
    }))


async def send_timer_tick(player):
    """Send lightweight timer update without full game state."""
    time_remaining = max(0, int(turn_end_time - time.time()))
    await player.websocket.send(json.dumps({
        "type": "timer",
        "time_remaining": time_remaining,
        "players_ready": len(players_ready),
        "total_players": len(players)
    }))


def check_ownership(world):
    changed = False
    defender = None
    if world.owner and (world.iships > 0 or world.pships > 0):
        defender = world.owner

    orbiting_players = {f.owner for f in world.fleets if f.ships > 0}

    if defender:
        pass
    else:
        if len(orbiting_players) == 1:
            new_owner = list(orbiting_players)[0]
            if world.owner != new_owner:
                if world.owner:
                    world.owner.worlds.remove(world)
                world.owner = new_owner
                new_owner.worlds.append(world)
                changed = True
        elif len(orbiting_players) > 1:
            if world.owner:
                world.owner.worlds.remove(world)
                world.owner = None
                changed = True
        else:
            if world.owner:
                world.owner.worlds.remove(world)
                world.owner = None
                changed = True
    return changed


# ---------- NEW HELPERS FOR ROBUSTNESS / EXTENSIBILITY ----------

def has_exclusive_order(player, fleet_id: int) -> bool:
    """
    Returns True if the given player already has an exclusive order
    (MOVE, FIRE, AMBUSH) for the specified fleet.
    """
    return any(
        o.get("fleet_id") == fleet_id and o.get("type") in EXCLUSIVE_ORDER_TYPES
        for o in player.orders
    )


def group_orders_by_type(orders):
    """
    Groups raw orders by their 'type' field into a dict:
      { 'MOVE': [...], 'BUILD': [...], ... }
    """
    grouped = {}
    for order in orders:
        order_type = order.get("type")
        if order_type is None:
            continue
        grouped.setdefault(order_type, []).append(order)
    return grouped


def process_world_production(world):
    """
    Handles mineral production and population growth for a single world.
    Production is limited by population NOT used in building during this turn.
    """
    if not world.owner:
        return

    # Population available for mining = total population - population allocated to building
    population_used_building = getattr(world, 'population_used_building', 0)
    available_population = world.population - population_used_building

    production = min(world.mines, max(0, available_population))
    world.metal += production

    # Reset building tracker for next turn
    world.population_used_building = 0

    if world.population < world.limit:
        growth = math.ceil(world.population * 0.10)
        world.population = min(world.population + growth, world.limit)


def calculate_player_score(player):
    """
    Calculate player's score based on their assets.
    Score = worlds + industry + ships + artifacts + population
    """
    score = 0

    # Worlds: 10 points each
    score += len(player.worlds) * 10

    # Industry, ships, population from owned worlds
    for world in player.worlds:
        score += world.industry * 2  # 2 points per industry
        score += world.iships  # 1 point per IShip
        score += world.pships  # 1 point per PShip
        score += world.population  # 1 point per population

    # Ships in fleets
    for fleet in player.fleets:
        score += fleet.ships  # 1 point per ship
        score += fleet.cargo  # 1 point per cargo (population in transit)

    # Artifacts
    artifact_count = 0
    special_artifact_count = 0
    for world in player.worlds:
        for artifact in world.artifacts:
            if artifact.type == "special":
                special_artifact_count += 1
            else:
                artifact_count += 1
    for fleet in player.fleets:
        for artifact in fleet.artifacts:
            if artifact.type == "special":
                special_artifact_count += 1
            else:
                artifact_count += 1

    score += artifact_count * 10  # 10 points per regular artifact
    score += special_artifact_count * 50  # 50 points per special artifact

    player.score = score
    return score


async def handle_fleet_captures(world):
    """
    Resolves control of empty fleets in orbit around a world based on
    which owners have ships present (including world garrisons).
    """
    owners_with_ships = set()
    for f in world.fleets:
        if f.ships > 0:
            owners_with_ships.add(f.owner)

    if world.owner and (world.iships > 0 or world.pships > 0):
        owners_with_ships.add(world.owner)

    if len(owners_with_ships) == 1:
        sole_owner = next(iter(owners_with_ships))
        for f in world.fleets:
            if f.ships == 0 and f.owner != sole_owner:
                if f.owner:
                    f.owner.fleets.remove(f)
                    await send_event(
                        f.owner,
                        f"Lost control of empty Fleet {f.id} at World {world.id}.",
                        "combat"
                    )
                f.owner = sole_owner
                sole_owner.fleets.append(f)
                await send_event(
                    sole_owner,
                    f"Captured empty Fleet {f.id} at World {world.id}.",
                    "capture"
                )
    else:
        for f in world.fleets:
            if f.ships == 0 and f.owner is not None:
                f.owner.fleets.remove(f)
                await send_event(
                    f.owner,
                    f"Lost control of empty Fleet {f.id} at World {world.id} (Neutralized).",
                    "combat"
                )
                f.owner = None


# ---------- TURN PROCESSING (REFINED) ----------

async def process_turn():
    global game_turn, turn_end_time, players_ready, current_turn_duration

    print(f"=== PROCESS_TURN START: Turn {game_turn} -> {game_turn + 1} ===")
    game_turn += 1
    players_ready.clear()

    if game_turn <= 10 and game_turn % 2 == 0:
        current_turn_duration = min(
            MAX_TURN_DURATION,
            current_turn_duration + 60
        )
        print(f"Turn duration increased to {current_turn_duration}s")

    turn_end_time = time.time() + current_turn_duration
    print(f"Next turn will process in {current_turn_duration}s at {turn_end_time}")

    # Collect and clear all player orders
    all_orders = []
    for p in players.values():
        all_orders.extend(p.orders)
        p.orders = []

    print(f"Processing {len(all_orders)} total orders from {len(players)} players")

    # 1. Execute orders by priority
    orders_by_type = group_orders_by_type(all_orders)
    print(f"Orders by type: {', '.join(f'{k}:{len(v)}' for k, v in orders_by_type.items())}")

    for o in orders_by_type.get("TRANSFER", []):
        await execute_transfer(o)

    for o in orders_by_type.get("LOAD", []):
        await execute_load(o)

    for o in orders_by_type.get("UNLOAD", []):
        await execute_unload(o)

    for o in orders_by_type.get("BUILD", []):
        await execute_build(o)

    for o in orders_by_type.get("MIGRATE", []):
        await execute_migrate(o)

    for o in orders_by_type.get("FIRE", []):
        await execute_combat(o)

    for o in orders_by_type.get("AMBUSH", []):
        fid = o["fleet_id"]
        if fid in fleets:
            fleets[fid].is_ambushing = True

    for o in orders_by_type.get("MOVE", []):
        await execute_move_order(o)

    # 2. Production (economy)
    for w in worlds.values():
        process_world_production(w)

    # 3. Empty-fleet captures / neutralization
    for w in worlds.values():
        await handle_fleet_captures(w)

    # 4. World ownership changes and capture events
    for w in worlds.values():
        if check_ownership(w):
            if w.owner:
                await send_event(w.owner, f"Captured World {w.id}!", "capture")

    # 5. Fleet cleanup
    for f in fleets.values():
        f.moved = False
        f.is_ambushing = False

    # 6. Calculate scores for all players
    for p in players.values():
        calculate_player_score(p)

    # 7. Knowledge / visibility updates
    for p in players.values():
        presence_worlds = {f.world.id for f in p.fleets} | {w.id for w in p.worlds}
        for wid in presence_worlds:
            p.known_worlds[wid] = game_turn
            for neighbor in worlds[wid].connections:
                if neighbor not in p.known_worlds:
                    p.known_worlds[neighbor] = game_turn

    # 8. Push full updates to all players (force full after turn processing)
    for p in players.values():
        await send_update(p, force_full=True)
        await send_info(
            p,
            f"Turn {game_turn} processed. Next turn in {current_turn_duration}s."
        )

    print(f"=== PROCESS_TURN COMPLETE: Turn {game_turn} finished ===")
    print(f"Timer reset to {int(turn_end_time - time.time())}s from now")


# ---------- ORDER EXECUTION (UNCHANGED BEHAVIOR) ----------

async def execute_transfer(order):
    """
    Transfer ships from fleet to world defenses or another fleet.
    F5T10I - Transfer 10 ships to world IShips
    F5T10P - Transfer 10 ships to world PShips
    F5T10F7 - Transfer 10 ships to fleet 7
    """
    player = order["player"]
    fid = order["fleet_id"]
    amt = order["amount"]
    target_type = order["target_type"]

    if fid not in fleets:
        return
    f = fleets[fid]
    if f.owner != player:
        return
    if f.ships < amt:
        return

    w = f.world
    if target_type in ["I", "P"] and w.owner != player:
        return

    f.ships -= amt
    if target_type == "I":
        w.iships += amt
    elif target_type == "P":
        w.pships += amt
    elif target_type == "F":
        target_fid = order["target_id"]
        if target_fid not in fleets:
            # Invalid target fleet, refund ships
            f.ships += amt
            return

        target_fleet = fleets[target_fid]
        # Check both fleets are at the same world (compare world objects directly)
        if target_fleet.world.id != f.world.id:
            # Not at same world, refund ships
            f.ships += amt
            await send_event(player, f"F{target_fid} is not at the same world as F{fid}.", "error")
            return

        # Transfer successful
        target_fleet.ships += amt
        await send_event(player, f"Transferred {amt} ships from F{fid} to F{target_fid}.", "info")


async def execute_load(order):
    """
    Load population from world onto fleet as cargo.
    F5L - Load max capacity
    F5L10 - Load 10 population
    Merchants get 2x cargo capacity (2 pop per ship), others get 1x (1 pop per ship)
    """
    player = order["player"]
    fid = order["fleet_id"]
    amt = order["amount"]  # None means load max

    if fid not in fleets:
        return
    f = fleets[fid]
    if f.owner != player:
        return

    w = f.world
    if w.owner != player:
        await send_event(player, f"Cannot load from world you don't own.", "error")
        return

    # Calculate cargo capacity
    cargo_multiplier = 2 if player.character_type == "Merchant" else 1
    max_capacity = f.ships * cargo_multiplier
    available_capacity = max_capacity - f.cargo

    # Determine amount to load
    if amt is None:
        # Load max
        amt = min(available_capacity, w.population)
    else:
        # Load specified amount, limited by capacity and available population
        amt = min(amt, available_capacity, w.population)

    if amt <= 0:
        await send_event(player, f"F{fid} cannot load cargo (no capacity or population).", "error")
        return

    # Execute load
    w.population -= amt
    f.cargo += amt
    await send_event(player, f"F{fid} loaded {amt} population from W{w.id}.", "info")


async def execute_unload(order):
    """
    Unload cargo from fleet to world population.
    F5U - Unload all
    F5U10 - Unload 10 population
    """
    player = order["player"]
    fid = order["fleet_id"]
    amt = order["amount"]  # None means unload all

    if fid not in fleets:
        return
    f = fleets[fid]
    if f.owner != player:
        return

    w = f.world
    if w.owner != player:
        await send_event(player, f"Cannot unload to world you don't own.", "error")
        return

    # Determine amount to unload
    if amt is None:
        # Unload all
        amt = f.cargo
    else:
        # Unload specified amount, limited by cargo available
        amt = min(amt, f.cargo)

    if amt <= 0:
        await send_event(player, f"F{fid} has no cargo to unload.", "error")
        return

    # Check population limit
    if w.population + amt > w.limit:
        max_unload = w.limit - w.population
        if max_unload <= 0:
            await send_event(player, f"W{w.id} is at population limit.", "error")
            return
        amt = max_unload

    # Execute unload
    f.cargo -= amt
    w.population += amt
    await send_event(player, f"F{fid} unloaded {amt} population to W{w.id}.", "info")


async def execute_build(order):
    player = order["player"]
    wid = order["world_id"]
    amt = order["amount"]
    target_type = order["target_type"]

    if wid not in worlds:
        return
    w = worlds[wid]
    if w.owner != player:
        return

    # Different build types have different costs
    if target_type in ["I", "P", "F"]:
        # IShips, PShips, or Fleet ships: 1 industry, 1 metal, 1 population each
        # Industry and population are used but not consumed (they're rate limiters)
        # Metal is consumed (raw materials)
        max_build = min(w.industry, w.metal, w.population)
        amt = min(amt, max_build)

        if amt > 0:
            w.metal -= amt
            # Track population allocated to building (for production calculation later)
            if not hasattr(w, 'population_used_building'):
                w.population_used_building = 0
            w.population_used_building += amt

            if target_type == "I":
                w.iships += amt
            elif target_type == "P":
                w.pships += amt
            elif target_type == "F":
                fid = order["target_id"]
                if (
                    fid in fleets and fleets[fid].world == w
                    and fleets[fid].owner == player
                ):
                    fleets[fid].ships += amt
                else:
                    # Invalid target, refund metal and population allocation
                    w.metal += amt
                    w.population_used_building -= amt

    elif target_type == "INDUSTRY":
        # Build industry: 5 industry (4 for empire builders) + 5 metal + 5 population = 1 industry
        # This consumes population (they become part of the industrial infrastructure)
        required_ind = 4 if player.character_type == "Empire Builder" else 5
        max_build = min(w.industry // required_ind, w.metal // 5, w.population // 5)
        amt = min(amt, max_build)

        if amt > 0:
            w.metal -= amt * 5
            w.population -= amt * 5  # Consumed - workers become part of infrastructure
            w.industry += amt
            await send_event(player, f"Built {amt} industry at W{wid}.", "info")

    elif target_type == "LIMIT":
        # Increase population limit: 5 industry (4 for empire builders) per 1 limit
        # Uses industry as a rate limiter, doesn't consume anything
        required_ind = 4 if player.character_type == "Empire Builder" else 5
        max_build = w.industry // required_ind
        amt = min(amt, max_build)

        if amt > 0:
            w.limit += amt
            await send_event(player, f"Increased population limit by {amt} at W{wid}.", "info")

    elif target_type == "ROBOT":
        # Build robots: 1 industry + 1 metal = 2 robots (only berserkers, only at robot worlds)
        if player.character_type != "Berserker":
            await send_event(player, f"Only Berserkers can build robots!", "combat")
            return

        # TODO: Check if world has robot population
        # For now, just allow it
        max_build = min(w.industry, w.metal)
        amt = min(amt, max_build)

        if amt > 0:
            w.metal -= amt
            w.population += amt * 2  # 2 robots per industry
            await send_event(player, f"Built {amt * 2} robots at W{wid}.", "info")


async def execute_migrate(order):
    """
    Execute population migration from one world to an adjacent world.
    1 industry + 1 metal = move 1 population
    """
    player = order["player"]
    wid = order["world_id"]
    amt = order["amount"]
    dest_wid = order["dest_world"]

    if wid not in worlds or dest_wid not in worlds:
        return

    w_from = worlds[wid]
    w_to = worlds[dest_wid]

    if w_from.owner != player:
        return

    # Check connection
    if dest_wid not in w_from.connections:
        return

    # Calculate max migration: limited by industry, metal, and population
    max_migrate = min(w_from.industry, w_from.metal, w_from.population)
    amt = min(amt, max_migrate)

    if amt > 0:
        # Consume resources
        w_from.metal -= amt
        w_from.population -= amt  # Population leaves the world (already not available for mining)

        # Add to destination
        w_to.population += amt

        # Player gets visibility of destination world
        player.known_worlds[dest_wid] = game_turn

        await send_event(
            player,
            f"Migrated {amt} population from W{wid} to W{dest_wid}.",
            "info"
        )


async def execute_combat(order):
    player = order["player"]
    fid = order["fleet_id"]
    target_type = order["target_type"]

    if fid not in fleets:
        return
    attacker = fleets[fid]
    if attacker.owner != player:
        return

    w = attacker.world

    if target_type == "WORLD":
        sub_target = order["sub_target"]
        shots = attacker.ships
        if sub_target == "P":
            def_ships = w.pships
            w.pships = max(0, w.pships - math.ceil(shots / 2))
            rem_shots = shots - (def_ships * 2)
            if rem_shots > 0:
                pop_killed = math.ceil(rem_shots / 2)
                w.population = max(0, w.population - pop_killed)
                player.score -= pop_killed
                await send_event(
                    player,
                    f"Fired on W{w.id} population, killing {pop_killed}.",
                    "combat"
                )
        elif sub_target == "I":
            def_ships = w.iships
            w.iships = max(0, w.iships - math.ceil(shots / 2))
            rem_shots = shots - (def_ships * 2)
            if rem_shots > 0:
                ind_destroyed = math.ceil(rem_shots / 2)
                w.industry = max(0, w.industry - ind_destroyed)
                await send_event(
                    player,
                    f"Fired on W{w.id} industry, destroying {ind_destroyed}.",
                    "combat"
                )

    elif target_type == "FLEET":
        target_fid = order["target_id"]
        if target_fid in fleets:
            defender = fleets[target_fid]
            if defender.world == w:
                dmg_attacker, dmg_defender = await resolve_combat(
                    attacker.ships,
                    defender.ships
                )
                attacker.ships = max(0, attacker.ships - dmg_attacker)
                defender.ships = max(0, defender.ships - dmg_defender)
                msg = (
                    f"Combat at W{w.id}! F{fid} vs F{target_fid}. "
                    f"Losses: Attacker {dmg_attacker}, "
                    f"Defender {dmg_defender}."
                )
                await send_event(player, msg, "combat")
                await send_event(defender.owner, msg, "combat")


async def execute_move_order(order):
    player = order["player"]
    fid = order["fleet_id"]
    path = order["path"]

    if fid not in fleets:
        return
    fleet = fleets[fid]
    if fleet.owner != player:
        return
    if fleet.ships == 0:
        return

    current_world = fleet.world

    for dest_id in path:
        dest_world = worlds[dest_id]

        ambushers = [
            f for f in dest_world.fleets
            if f.is_ambushing and f.owner != player and f.ships > 0
        ]
        if ambushers:
            await send_event(
                player,
                f"Fleet {fid} ambushed at World {dest_id}!",
                "ambush"
            )
            current_world.fleets.remove(fleet)
            fleet.world = dest_world
            dest_world.fleets.append(fleet)
            fleet.moved = True

            total_ambush_strength = sum(f.ships for f in ambushers) * 2
            damage_to_fleet = math.ceil(total_ambush_strength / 2)
            fleet.ships = max(0, fleet.ships - damage_to_fleet)

            for ambusher in ambushers:
                await send_event(
                    ambusher.owner,
                    f"Your Fleet {ambusher.id} ambushed Fleet "
                    f"{fid} at World {dest_id}.",
                    "ambush"
                )

            return

        current_world = dest_world

    final_dest = worlds[path[-1]]
    if fleet.world != final_dest:
        fleet.world.fleets.remove(fleet)
        fleet.world = final_dest
        final_dest.fleets.append(fleet)

    fleet.moved = True
    await send_event(
        player,
        f"Fleet {fid} moved to World {path[-1]}.",
        "info"
    )


async def resolve_combat(attacker_ships, defender_ships):
    hits_on_defender = attacker_ships
    hits_on_attacker = defender_ships
    defender_losses = math.ceil(hits_on_defender / 2)
    attacker_losses = math.ceil(hits_on_attacker / 2)
    return attacker_losses, defender_losses


# ---------- COMMAND PROCESSING (USING HELPERS) ----------

async def process_command(player, command):
    parts = command.split()
    if not parts:
        return
    cmd = parts[0].upper()

    if cmd == "JOIN":
        if len(parts) >= 2:
            name = ""
            char_type = "Empire Builder"

            full_args = " ".join(parts[1:])
            found_type = False
            for ct in CHARACTER_TYPES:
                if full_args.upper().endswith(ct.upper()):
                    char_type = ct
                    name = full_args[:-(len(ct))].strip()
                    found_type = True
                    break

            if not found_type:
                name = full_args

            if not name:
                await send_error(player, "Usage: JOIN <name> [type]")
                return

            await join_game(player, name, char_type)
        else:
            await send_error(player, "Usage: JOIN <name> [type]")
        return

    if not player.worlds and not player.fleets:
        await send_error(player, "Please JOIN the game first.")
        return

    if cmd == "TURN":
        if player.websocket not in players_ready:
            players_ready.add(player.websocket)
            print(f"[TURN] Player {player.name} ready. {len(players_ready)}/{len(players)} players ready.")
            await send_info(
                player,
                "You have ended your turn. Waiting for others..."
            )
            if len(players_ready) == len(players):
                try:
                    print(f"[TURN] All players ready ({len(players_ready)}/{len(players)}). Processing turn...")
                    await process_turn()
                except Exception as e:
                    print(f"Error in process_turn from TURN command: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                for p in players.values():
                    await send_update(p)
        else:
            print(f"[TURN] Player {player.name} already marked ready")
        return

    # FIRE at world population / industry
    fire_world_match = re.match(r"^F(\d+)A(P|I)$", cmd)
    if fire_world_match:
        fid, target = int(fire_world_match.group(1)), fire_world_match.group(2)
        if has_exclusive_order(player, fid):
            await send_error(
                player,
                "Fleet already has an exclusive order."
            )
            return
        if fid in fleets and fleets[fid].owner == player:
            player.orders.append({
                "type": "FIRE",
                "player": player,
                "fleet_id": fid,
                "target_type": "WORLD",
                "sub_target": target
            })
            await send_info(player, "Fire order queued.")
            await send_update(player)
        else:
            await send_error(player, "Invalid fleet.")
        return

    # AMBUSH
    ambush_match = re.match(r"^F(\d+)A$", cmd)
    if ambush_match:
        fid = int(ambush_match.group(1))
        if has_exclusive_order(player, fid):
            await send_error(
                player,
                "Fleet already has an exclusive order."
            )
            return
        if fid in fleets and fleets[fid].owner == player:
            player.orders.append({
                "type": "AMBUSH",
                "player": player,
                "fleet_id": fid
            })
            await send_info(player, "Ambush order queued.")
            await send_update(player)
        else:
            await send_error(player, "Invalid fleet.")
        return

    # FIRE at fleet
    fire_match = re.match(r"^F(\d+)AF(\d+)$", cmd)
    if fire_match:
        fid, target_fid = int(fire_match.group(1)), int(fire_match.group(2))
        if has_exclusive_order(player, fid):
            await send_error(
                player,
                "Fleet already has an exclusive order."
            )
            return
        if fid in fleets and fleets[fid].owner == player:
            player.orders.append({
                "type": "FIRE",
                "player": player,
                "fleet_id": fid,
                "target_type": "FLEET",
                "target_id": target_fid
            })
            await send_info(player, "Attack order queued.")
            await send_update(player)
        else:
            await send_error(player, "Invalid fleet.")
        return

    # BUILD (ships, industry, limit, robots)
    build_match = re.match(r"^W(\d+)B(\d+)(F(\d+)|I|P|IND|INDUSTRY|L|LIMIT|R|ROBOT)$", cmd, re.IGNORECASE)
    if build_match:
        wid = int(build_match.group(1))
        amt = int(build_match.group(2))
        target_type = build_match.group(3).upper()
        target_id = None

        # Parse fleet target
        if target_type.startswith("F"):
            target_id = int(build_match.group(4))
            target_type = "F"
        # Normalize target types
        elif target_type in ["IND", "INDUSTRY"]:
            target_type = "INDUSTRY"
        elif target_type in ["L", "LIMIT"]:
            target_type = "LIMIT"
        elif target_type in ["R", "ROBOT"]:
            target_type = "ROBOT"

        if wid in worlds and worlds[wid].owner == player:
            player.orders.append({
                "type": "BUILD",
                "player": player,
                "world_id": wid,
                "amount": amt,
                "target_type": target_type,
                "target_id": target_id
            })
            await send_info(player, "Build order queued.")
            await send_update(player)
        else:
            await send_error(player, "Invalid world.")
        return

    # MIGRATE POPULATION
    migrate_match = re.match(r"^W(\d+)M(\d+)W(\d+)$", cmd)
    if migrate_match:
        wid = int(migrate_match.group(1))
        amt = int(migrate_match.group(2))
        dest_wid = int(migrate_match.group(3))

        if wid in worlds and worlds[wid].owner == player:
            # Check if destination is connected
            if dest_wid not in worlds[wid].connections:
                await send_error(player, f"W{dest_wid} is not connected to W{wid}.")
                return

            player.orders.append({
                "type": "MIGRATE",
                "player": player,
                "world_id": wid,
                "amount": amt,
                "dest_world": dest_wid
            })
            await send_info(player, "Migration order queued.")
            await send_update(player)
        else:
            await send_error(player, "Invalid world.")
        return

    # TRANSFER
    transfer_match = re.match(r"^F(\d+)T(\d+)(F(\d+)|I|P)$", cmd)
    if transfer_match:
        fid = int(transfer_match.group(1))
        amt = int(transfer_match.group(2))
        target_type = transfer_match.group(3)
        target_id = int(transfer_match.group(4)) if target_type.startswith("F") else None
        if fid in fleets and fleets[fid].owner == player:
            player.orders.append({
                "type": "TRANSFER",
                "player": player,
                "fleet_id": fid,
                "amount": amt,
                "target_type": target_type[0],
                "target_id": target_id
            })
            await send_info(player, "Transfer order queued.")
            await send_update(player)
        else:
            await send_error(player, "Invalid fleet.")
        return

    # LOAD - F5L or F5L10 (load population from world as cargo)
    load_match = re.match(r"^F(\d+)L(\d+)?$", cmd, re.IGNORECASE)
    if load_match:
        fid = int(load_match.group(1))
        amt = int(load_match.group(2)) if load_match.group(2) else None  # None means load max
        if fid in fleets and fleets[fid].owner == player:
            player.orders.append({
                "type": "LOAD",
                "player": player,
                "fleet_id": fid,
                "amount": amt  # None means load max
            })
            await send_info(player, "Load order queued.")
            await send_update(player)
        else:
            await send_error(player, "Invalid fleet.")
        return

    # UNLOAD - F5U or F5U10 (unload cargo to world population)
    unload_match = re.match(r"^F(\d+)U(\d+)?$", cmd, re.IGNORECASE)
    if unload_match:
        fid = int(unload_match.group(1))
        amt = int(unload_match.group(2)) if unload_match.group(2) else None  # None means unload all
        if fid in fleets and fleets[fid].owner == player:
            player.orders.append({
                "type": "UNLOAD",
                "player": player,
                "fleet_id": fid,
                "amount": amt  # None means unload all
            })
            await send_info(player, "Unload order queued.")
            await send_update(player)
        else:
            await send_error(player, "Invalid fleet.")
        return

    # MOVE with path: F<id>W1W2W3...
    move_match = re.match(r"^F(\d+)(W\d+)+$", cmd)
    if move_match:
        fid = int(move_match.group(1))
        if has_exclusive_order(player, fid):
            await send_error(
                player,
                "Fleet already has an exclusive order."
            )
            return
        path = [int(x) for x in cmd[len(f"F{fid}"):].split("W") if x]
        if fid in fleets and fleets[fid].owner == player:
            player.orders.append({
                "type": "MOVE",
                "player": player,
                "fleet_id": fid,
                "path": path
            })
            await send_info(player, "Move order queued.")
            await send_update(player)
        else:
            await send_error(player, "Invalid fleet.")
        return

    # Legacy MOVE command: MOVE <fleet_id> <dest_id>
    if cmd == "MOVE":
        if len(parts) < 3:
            await send_error(player, "Usage: MOVE <fleet_id> <dest_id>")
            return
        try:
            fid = int(parts[1])
            dest_id = int(parts[2])
            if has_exclusive_order(player, fid):
                await send_error(
                    player,
                    "Fleet already has an exclusive order."
                )
                return
            if fid in fleets and fleets[fid].owner == player:
                player.orders.append({
                    "type": "MOVE",
                    "player": player,
                    "fleet_id": fid,
                    "path": [dest_id]
                })
                await send_info(player, "Move order queued.")
                await send_update(player)
            else:
                await send_error(player, "Invalid fleet.")
        except ValueError:
            await send_error(player, "Invalid numbers.")
        return

    await send_error(player, f"Unknown command: {cmd}")


# ---------- SERVER LOOP ----------

async def timer_loop():
    """Main game timer - processes turns and sends timer ticks."""
    tick_count = 0
    while True:
        await asyncio.sleep(1)
        tick_count += 1

        current_time = time.time()
        time_remaining = int(turn_end_time - current_time)

        # Debug every 30 seconds
        if tick_count % 30 == 0:
            print(f"[Timer] Turn {game_turn}, {time_remaining}s remaining, {len(players)} players, {len(players_ready)} ready")

        if current_time >= turn_end_time:
            print(f"[Timer] Time expired! Triggering turn processing...")
            try:
                await process_turn()
            except Exception as e:
                print(f"Error in process_turn: {e}")
                import traceback
                traceback.print_exc()
        else:
            # Send lightweight timer tick to all connected players
            for player in list(players.values()):
                try:
                    await send_timer_tick(player)
                except Exception as e:
                    print(f"Error sending timer tick: {e}")
                    pass  # Player disconnected, will be cleaned up elsewhere


async def handler(websocket):
    await register(websocket)
    player = players[websocket]
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "command":
                await process_command(player, data["text"])
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await unregister(websocket)


def run_http_server():
    PORT = 8000
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    Handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"HTTP Server serving at http://0.0.0.0:{PORT}")
        httpd.serve_forever()


async def main():
    http_thread = threading.Thread(
        target=run_http_server,
        daemon=True
    )
    http_thread.start()
    asyncio.create_task(timer_loop())
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket Server started on ws://0.0.0.0:8765")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")