"""
Test fixtures for creating game state for testing.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import server modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from server.game.entities import Player, World, Fleet, Artifact
from server.game.state import GameState


class MockMessageSender:
    """Mock message sender for testing - doesn't actually send messages."""

    async def send_event(self, player, message, event_type="info"):
        """Mock send event - does nothing."""
        pass


# Singleton mock message sender
_mock_sender = MockMessageSender()


def get_mock_message_sender():
    """Get the mock message sender for testing."""
    return _mock_sender


def create_test_player(player_id=1, name="TestPlayer", character_type="Berserker"):
    """Create a test player."""
    player = Player(player_id, name, character_type)
    player.score = 0
    player.orders = []
    player.known_worlds = {}
    return player


def create_test_world(world_id=1, owner=None):
    """Create a test world with default values."""
    world = World(world_id)
    world.owner = owner
    world.industry = 10
    world.metal = 20
    world.mines = 5
    world.population = 15
    world.limit = 30
    world.iships = 0
    world.pships = 0
    world.connections = []
    world.artifacts = []
    world.fleets = []
    return world


def create_test_fleet(fleet_id=1, owner=None, world=None, ships=10):
    """Create a test fleet."""
    if world is None:
        # Need a dummy world for fleet creation
        world = create_test_world(999, owner)

    fleet = Fleet(fleet_id, owner, world)
    fleet.ships = ships
    fleet.cargo = 0
    fleet.moved = False
    fleet.is_ambushing = False
    fleet.artifacts = []

    return fleet


def create_test_artifact(artifact_id=1, name="Test Artifact"):
    """Create a test artifact."""
    return Artifact(artifact_id, name)


def create_basic_game_state():
    """
    Create a basic game state with 2 players, 3 worlds, and some fleets.

    Returns:
        tuple: (game_state, player1, player2, worlds, fleets)
    """
    game_state = GameState()

    # Create players
    player1 = create_test_player(1, "Player1", "Berserker")
    player2 = create_test_player(2, "Player2", "Merchant")

    game_state.players = {1: player1, 2: player2}

    # Create worlds
    world1 = create_test_world(1, player1)
    world2 = create_test_world(2, player2)
    world3 = create_test_world(3, None)  # Neutral world

    # Connect worlds
    world1.connections = [2, 3]
    world2.connections = [1, 3]
    world3.connections = [1, 2]

    game_state.worlds = {1: world1, 2: world2, 3: world3}

    # Create fleets
    fleet1 = create_test_fleet(1, player1, world1, 10)
    fleet2 = create_test_fleet(2, player1, world1, 5)
    fleet3 = create_test_fleet(3, player2, world2, 15)

    game_state.fleets = {1: fleet1, 2: fleet2, 3: fleet3}

    # Add fleets to player lists
    player1.fleets = [fleet1, fleet2]
    player2.fleets = [fleet3]

    # Add worlds to player lists
    player1.worlds = [world1]
    player2.worlds = [world2]

    game_state.game_turn = 1

    return game_state, player1, player2, [world1, world2, world3], [fleet1, fleet2, fleet3]


def create_combat_game_state():
    """
    Create a game state set up for combat testing.

    Returns:
        tuple: (game_state, player1, player2, worlds, fleets)
    """
    game_state, player1, player2, worlds, fleets = create_basic_game_state()

    # Set up world defenses
    worlds[0].iships = 20
    worlds[0].pships = 10
    worlds[1].iships = 15
    worlds[1].pships = 5

    # Add more ships to fleets for combat
    fleets[0].ships = 30
    fleets[2].ships = 25

    return game_state, player1, player2, worlds, fleets


def create_artifact_game_state():
    """
    Create a game state with artifacts for testing.

    Returns:
        tuple: (game_state, player1, player2, artifacts)
    """
    game_state, player1, player2, worlds, fleets = create_basic_game_state()

    # Create artifacts
    artifact1 = create_test_artifact(1, "Power Crystal")
    artifact2 = create_test_artifact(2, "Ancient Map")
    artifact3 = create_test_artifact(3, "Energy Shield")

    # Place artifacts
    fleets[0].artifacts.append(artifact1)
    worlds[0].artifacts.append(artifact2)
    fleets[2].artifacts.append(artifact3)

    return game_state, player1, player2, [artifact1, artifact2, artifact3]


def create_economy_game_state():
    """
    Create a game state set up for economy/production testing.

    Returns:
        tuple: (game_state, player1, player2, worlds, fleets)
    """
    game_state, player1, player2, worlds, fleets = create_basic_game_state()

    # Set up worlds with more resources
    worlds[0].industry = 50
    worlds[0].metal = 100
    worlds[0].population = 80
    worlds[0].iships = 30

    worlds[1].industry = 40
    worlds[1].metal = 60
    worlds[1].population = 70
    worlds[1].pships = 20

    # Set up fleets with cargo
    fleets[0].cargo = 10
    fleets[2].cargo = 5

    return game_state, player1, player2, worlds, fleets
