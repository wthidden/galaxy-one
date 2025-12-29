"""
Test command execution - verifies commands produce correct game state changes.
These are integration tests that execute commands and verify results.
"""
import unittest
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from server.game.mechanics.movement import execute_move_order, execute_probe_order
from server.game.mechanics.combat import execute_fire_order
from server.game.mechanics.production import (
    execute_build_order, execute_transfer_order, execute_load_order,
    execute_unload_order, execute_scrap_ships_order, execute_plunder_order,
    execute_consumer_goods_order, execute_declare_relation_order
)
from server.game.state import set_game_state
from tests.fixtures import (
    create_basic_game_state, create_combat_game_state, create_economy_game_state,
    get_mock_message_sender
)

# Monkey-patch message sender for testing
import server.message_sender
server.message_sender._message_sender = get_mock_message_sender()


class TestCommandExecution(unittest.TestCase):
    """Test that commands execute correctly and produce expected game state changes."""

    def setUp(self):
        """Set up test fixtures."""
        self.game_state, self.player1, self.player2, self.worlds, self.fleets = create_basic_game_state()
        set_game_state(self.game_state)

    def test_move_execution(self):
        """Test fleet movement execution"""
        order = {
            "type": "MOVE",
            "player": self.player1,
            "fleet_id": 1,
            "path": [2]
        }

        initial_world = self.fleets[0].world
        self.assertEqual(initial_world.id, 1)

        asyncio.run(execute_move_order(order))

        # Fleet should have moved to world 2
        self.assertEqual(self.fleets[0].world.id, 2)
        self.assertTrue(self.fleets[0].moved)
        self.assertNotIn(self.fleets[0], initial_world.fleets)
        self.assertIn(self.fleets[0], self.worlds[1].fleets)

    def test_build_iships_execution(self):
        """Test building ISHIPS"""
        order = {
            "type": "BUILD",
            "player": self.player1,
            "world_id": 1,
            "amount": 5,
            "target_type": "I",
            "target_id": None
        }

        initial_iships = self.worlds[0].iships
        initial_industry = self.worlds[0].industry
        initial_metal = self.worlds[0].metal
        initial_pop = self.worlds[0].population

        asyncio.run(execute_build_order(order))

        # World should have 5 more ISHIPS and 5 less of each resource
        self.assertEqual(self.worlds[0].iships, initial_iships + 5)
        self.assertEqual(self.worlds[0].industry, initial_industry - 5)
        self.assertEqual(self.worlds[0].metal, initial_metal - 5)
        self.assertEqual(self.worlds[0].population, initial_pop - 5)

    def test_transfer_to_iships_execution(self):
        """Test transferring ships to ISHIPS"""
        self.fleets[0].ships = 20

        order = {
            "type": "TRANSFER",
            "player": self.player1,
            "fleet_id": 1,
            "amount": 10,
            "target_type": "I",
            "target_id": None
        }

        initial_iships = self.worlds[0].iships
        initial_ships = self.fleets[0].ships

        asyncio.run(execute_transfer_order(order))

        # Fleet should have 10 fewer ships, world should have 10 more ISHIPS
        self.assertEqual(self.fleets[0].ships, initial_ships - 10)
        self.assertEqual(self.worlds[0].iships, initial_iships + 10)

    def test_load_cargo_execution(self):
        """Test loading population as cargo"""
        order = {
            "type": "LOAD",
            "player": self.player1,
            "fleet_id": 1,
            "amount": 10
        }

        initial_pop = self.worlds[0].population
        initial_cargo = self.fleets[0].cargo

        asyncio.run(execute_load_order(order))

        # Fleet should have 10 more cargo, world should have 10 less population
        self.assertEqual(self.fleets[0].cargo, initial_cargo + 10)
        self.assertEqual(self.worlds[0].population, initial_pop - 10)

    def test_unload_cargo_execution(self):
        """Test unloading cargo as population"""
        self.fleets[0].cargo = 10

        order = {
            "type": "UNLOAD",
            "player": self.player1,
            "fleet_id": 1,
            "amount": 5
        }

        initial_pop = self.worlds[0].population
        initial_cargo = self.fleets[0].cargo

        asyncio.run(execute_unload_order(order))

        # Fleet should have 5 less cargo, world should have 5 more population
        self.assertEqual(self.fleets[0].cargo, initial_cargo - 5)
        self.assertEqual(self.worlds[0].population, initial_pop + 5)

    def test_fire_at_fleet_execution(self):
        """Test firing at enemy fleet"""
        game_state, player1, player2, worlds, fleets = create_combat_game_state()
        set_game_state(game_state)

        # Move player2's fleet to same world as player1's fleet
        fleets[2].world.fleets.remove(fleets[2])
        fleets[2].world = worlds[0]
        worlds[0].fleets.append(fleets[2])

        order = {
            "type": "FIRE",
            "player": player1,
            "fleet_id": 1,
            "target_type": "FLEET",
            "target_id": 3,
            "sub_target": None
        }

        initial_target_ships = fleets[2].ships
        attacker_ships = fleets[0].ships

        asyncio.run(execute_fire_order(order))

        # Target fleet should have fewer ships (1 damage per 2 attacker ships)
        expected_damage = attacker_ships // 2
        self.assertEqual(fleets[2].ships, max(0, initial_target_ships - expected_damage))

    def test_scrap_ships_execution(self):
        """Test scrapping ships to industry"""
        self.worlds[0].iships = 12
        initial_industry = self.worlds[0].industry

        order = {
            "type": "SCRAP_SHIPS",
            "player": self.player1,
            "world_id": 1,
            "amount": 2
        }

        asyncio.run(execute_scrap_ships_order(order))

        # World should have 2 more industry and 12 fewer ISHIPS (6 per industry)
        self.assertEqual(self.worlds[0].industry, initial_industry + 2)
        self.assertEqual(self.worlds[0].iships, 0)

    def test_scrap_ships_empire_builder_execution(self):
        """Test Empire Builder scrap bonus (4 ships per industry)"""
        self.player1.character_type = "Empire Builder"
        self.worlds[0].iships = 8
        initial_industry = self.worlds[0].industry

        order = {
            "type": "SCRAP_SHIPS",
            "player": self.player1,
            "world_id": 1,
            "amount": 2
        }

        asyncio.run(execute_scrap_ships_order(order))

        # World should have 2 more industry and 8 fewer ISHIPS (4 per industry for Empire Builder)
        self.assertEqual(self.worlds[0].industry, initial_industry + 2)
        self.assertEqual(self.worlds[0].iships, 0)

    def test_plunder_execution(self):
        """Test plundering population to metal"""
        self.worlds[0].population = 50
        initial_metal = self.worlds[0].metal

        order = {
            "type": "PLUNDER",
            "player": self.player1,
            "world_id": 1
        }

        asyncio.run(execute_plunder_order(order))

        # World should have 50 more metal and 0 population
        self.assertEqual(self.worlds[0].metal, initial_metal + 50)
        self.assertEqual(self.worlds[0].population, 0)

    def test_consumer_goods_execution(self):
        """Test Merchant consumer goods delivery"""
        game_state, player1, player2, worlds, fleets = create_economy_game_state()
        set_game_state(game_state)

        # Make player1 a Merchant
        player1.character_type = "Merchant"
        fleets[0].cargo = 10
        initial_score = player1.score

        order = {
            "type": "UNLOAD_CONSUMER_GOODS",
            "player": player1,
            "fleet_id": 1,
            "amount": 5
        }

        asyncio.run(execute_consumer_goods_order(order))

        # First delivery should give 10 points per cargo (5 * 10 = 50)
        self.assertEqual(player1.score, initial_score + 50)
        self.assertEqual(fleets[0].cargo, 5)

        # Second delivery to same world should give 8 points per cargo
        asyncio.run(execute_consumer_goods_order(order))
        self.assertEqual(player1.score, initial_score + 50 + 40)
        self.assertEqual(fleets[0].cargo, 0)

    def test_declare_peace_execution(self):
        """Test declaring peace with another player"""
        order = {
            "type": "DECLARE_RELATION",
            "player": self.player1,
            "fleet_id": 1,
            "target_fleet_id": 3,
            "relation_type": "PEACE"
        }

        asyncio.run(execute_declare_relation_order(order))

        # Player1 should have peace relation with player2
        self.assertTrue(hasattr(self.player1, 'relations'))
        self.assertEqual(self.player1.relations.get(self.player2.id), "PEACE")

    def test_declare_war_execution(self):
        """Test declaring war with another player"""
        order = {
            "type": "DECLARE_RELATION",
            "player": self.player1,
            "fleet_id": 1,
            "target_fleet_id": 3,
            "relation_type": "WAR"
        }

        asyncio.run(execute_declare_relation_order(order))

        # Player1 should have war relation with player2
        self.assertTrue(hasattr(self.player1, 'relations'))
        self.assertEqual(self.player1.relations.get(self.player2.id), "WAR")

    def test_probe_execution(self):
        """Test probing adjacent world"""
        order = {
            "type": "PROBE",
            "player": self.player1,
            "source_type": "F",
            "source_id": 1,
            "target_world": 2
        }

        initial_ships = self.fleets[0].ships

        asyncio.run(execute_probe_order(order))

        # Fleet should have 1 fewer ship (probe cost)
        self.assertEqual(self.fleets[0].ships, initial_ships - 1)


class TestCommandExecutionEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions in command execution."""

    def setUp(self):
        """Set up test fixtures."""
        self.game_state, self.player1, self.player2, self.worlds, self.fleets = create_basic_game_state()
        set_game_state(self.game_state)

    def test_fire_destroys_fleet(self):
        """Test that firing can completely destroy a fleet"""
        game_state, player1, player2, worlds, fleets = create_combat_game_state()
        set_game_state(game_state)

        # Move player2's small fleet to player1's world
        fleets[2].ships = 10  # Small target
        fleets[2].world.fleets.remove(fleets[2])
        fleets[2].world = worlds[0]
        worlds[0].fleets.append(fleets[2])

        # Player1 has 30 ships, should do 15 damage
        fleets[0].ships = 30

        order = {
            "type": "FIRE",
            "player": player1,
            "fleet_id": 1,
            "target_type": "FLEET",
            "target_id": 3,
            "sub_target": None
        }

        asyncio.run(execute_fire_order(order))

        # Target fleet should be destroyed (0 ships)
        self.assertEqual(fleets[2].ships, 0)

    def test_load_all_population(self):
        """Test loading all population from a world"""
        self.worlds[0].population = 100
        self.fleets[0].ships = 200  # Enough capacity

        order = {
            "type": "LOAD",
            "player": self.player1,
            "fleet_id": 1,
            "amount": None  # Load all
        }

        asyncio.run(execute_load_order(order))

        # Should load all population (limited by world pop)
        self.assertEqual(self.worlds[0].population, 0)
        self.assertEqual(self.fleets[0].cargo, 100)

    def test_transfer_creates_empty_fleet(self):
        """Test transferring all ships leaves fleet with 0 ships"""
        self.fleets[0].ships = 10

        order = {
            "type": "TRANSFER",
            "player": self.player1,
            "fleet_id": 1,
            "amount": 10,
            "target_type": "I",
            "target_id": None
        }

        asyncio.run(execute_transfer_order(order))

        # Fleet should have 0 ships
        self.assertEqual(self.fleets[0].ships, 0)
        self.assertEqual(self.worlds[0].iships, 10)


if __name__ == '__main__':
    unittest.main()
