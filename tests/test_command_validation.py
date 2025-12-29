"""
Test command validation - verifies commands properly validate game state.
"""
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from server.game.commands import (
    MoveFleetCommand, BuildCommand, TransferCommand, FireCommand,
    LoadCommand, UnloadCommand, ScrapShipsCommand, PlunderCommand,
    ProbeCommand, ViewArtifactCommand, DeclareRelationCommand
)
from tests.fixtures import (
    create_basic_game_state, create_combat_game_state,
    create_artifact_game_state, create_economy_game_state
)


class TestCommandValidation(unittest.TestCase):
    """Test that commands properly validate game state."""

    def setUp(self):
        """Set up test fixtures."""
        self.game_state, self.player1, self.player2, self.worlds, self.fleets = create_basic_game_state()

    # Movement validation tests
    def test_move_nonexistent_fleet(self):
        """Cannot move a fleet that doesn't exist"""
        cmd = MoveFleetCommand(self.player1, 999, [2])
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("does not exist", msg)

    def test_move_not_owned_fleet(self):
        """Cannot move a fleet you don't own"""
        cmd = MoveFleetCommand(self.player1, 3, [1])  # Fleet 3 belongs to player2
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("do not own", msg)

    def test_move_empty_fleet(self):
        """Cannot move a fleet with no ships"""
        self.fleets[0].ships = 0
        cmd = MoveFleetCommand(self.player1, 1, [2])
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("no ships", msg)

    def test_move_disconnected_worlds(self):
        """Cannot move to disconnected world"""
        cmd = MoveFleetCommand(self.player1, 1, [99])  # World 99 doesn't exist
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("not connected", msg)

    def test_move_valid(self):
        """Valid move should pass validation"""
        cmd = MoveFleetCommand(self.player1, 1, [2])
        valid, msg = cmd.validate(self.game_state)
        self.assertTrue(valid)

    # Build validation tests
    def test_build_nonexistent_world(self):
        """Cannot build on world that doesn't exist"""
        cmd = BuildCommand(self.player1, 999, 10, "I")
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("does not exist", msg)

    def test_build_not_owned_world(self):
        """Cannot build on world you don't own"""
        cmd = BuildCommand(self.player1, 2, 10, "I")  # World 2 belongs to player2
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("do not own", msg)

    def test_build_exceeds_resources(self):
        """Cannot build more than available resources"""
        self.worlds[0].industry = 5
        cmd = BuildCommand(self.player1, 1, 20, "I")
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("maximum", msg)

    def test_build_valid(self):
        """Valid build should pass validation"""
        cmd = BuildCommand(self.player1, 1, 5, "I")
        valid, msg = cmd.validate(self.game_state)
        self.assertTrue(valid)

    # Transfer validation tests
    def test_transfer_nonexistent_fleet(self):
        """Cannot transfer from nonexistent fleet"""
        cmd = TransferCommand(self.player1, 999, 10, "I")
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("does not exist", msg)

    def test_transfer_not_owned_fleet(self):
        """Cannot transfer from fleet you don't own"""
        cmd = TransferCommand(self.player1, 3, 10, "I")  # Fleet 3 belongs to player2
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("do not own", msg)

    def test_transfer_insufficient_ships(self):
        """Cannot transfer more ships than available"""
        self.fleets[0].ships = 5
        cmd = TransferCommand(self.player1, 1, 10, "I")
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("only has", msg)

    def test_transfer_valid(self):
        """Valid transfer should pass validation"""
        cmd = TransferCommand(self.player1, 1, 5, "I")
        valid, msg = cmd.validate(self.game_state)
        self.assertTrue(valid)

    # Combat validation tests
    def test_fire_nonexistent_fleet(self):
        """Cannot fire from nonexistent fleet"""
        cmd = FireCommand(self.player1, 999, "FLEET", 2)
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("does not exist", msg)

    def test_fire_not_owned_fleet(self):
        """Cannot fire from fleet you don't own"""
        cmd = FireCommand(self.player1, 3, "FLEET", 1)
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("do not own", msg)

    def test_fire_empty_fleet(self):
        """Cannot fire from fleet with no ships"""
        self.fleets[0].ships = 0
        cmd = FireCommand(self.player1, 1, "FLEET", 3)
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("no ships", msg)

    def test_fire_at_own_fleet(self):
        """Cannot fire at your own fleet"""
        cmd = FireCommand(self.player1, 1, "FLEET", 2)
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("own fleet", msg)

    def test_fire_valid(self):
        """Valid fire command should pass validation"""
        # Move fleet 3 to same world as fleet 1
        self.fleets[2].world.fleets.remove(self.fleets[2])
        self.fleets[2].world = self.worlds[0]
        self.worlds[0].fleets.append(self.fleets[2])

        cmd = FireCommand(self.player1, 1, "FLEET", 3)
        valid, msg = cmd.validate(self.game_state)
        self.assertTrue(valid)

    # Cargo validation tests
    def test_load_nonexistent_fleet(self):
        """Cannot load on nonexistent fleet"""
        cmd = LoadCommand(self.player1, 999)
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("does not exist", msg)

    def test_load_not_owned_fleet(self):
        """Cannot load on fleet you don't own"""
        cmd = LoadCommand(self.player1, 3)
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("do not own", msg)

    def test_load_no_population(self):
        """Cannot load from world with no population"""
        self.worlds[0].population = 0
        cmd = LoadCommand(self.player1, 1, 10)
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("no population", msg)

    def test_load_valid(self):
        """Valid load should pass validation"""
        cmd = LoadCommand(self.player1, 1, 10)
        valid, msg = cmd.validate(self.game_state)
        self.assertTrue(valid)

    def test_unload_no_cargo(self):
        """Cannot unload fleet with no cargo"""
        self.fleets[0].cargo = 0
        cmd = UnloadCommand(self.player1, 1)
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("no cargo", msg)

    def test_unload_valid(self):
        """Valid unload should pass validation"""
        self.fleets[0].cargo = 10
        cmd = UnloadCommand(self.player1, 1, 5)
        valid, msg = cmd.validate(self.game_state)
        self.assertTrue(valid)

    # Scrap ships validation tests
    def test_scrap_not_owned_world(self):
        """Cannot scrap ships on world you don't own"""
        cmd = ScrapShipsCommand(self.player1, 2, 1)
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("do not own", msg)

    def test_scrap_insufficient_iships(self):
        """Cannot scrap more ships than available"""
        self.worlds[0].iships = 5
        self.player1.character_type = "Berserker"  # Needs 6 ships per industry
        cmd = ScrapShipsCommand(self.player1, 1, 2)  # Needs 12 ships
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("Need", msg)

    def test_scrap_empire_builder_bonus(self):
        """Empire Builder needs only 4 ships per industry"""
        self.worlds[0].iships = 8
        self.player1.character_type = "Empire Builder"
        cmd = ScrapShipsCommand(self.player1, 1, 2)  # Needs 8 ships (4x2)
        valid, msg = cmd.validate(self.game_state)
        self.assertTrue(valid)

    def test_scrap_valid(self):
        """Valid scrap should pass validation"""
        self.worlds[0].iships = 12
        cmd = ScrapShipsCommand(self.player1, 1, 2)
        valid, msg = cmd.validate(self.game_state)
        self.assertTrue(valid)

    # Plunder validation tests
    def test_plunder_not_owned_world(self):
        """Cannot plunder world you don't own"""
        cmd = PlunderCommand(self.player1, 2)
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("do not own", msg)

    def test_plunder_no_population(self):
        """Cannot plunder world with no population"""
        self.worlds[0].population = 0
        cmd = PlunderCommand(self.player1, 1)
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("no population", msg)

    def test_plunder_valid(self):
        """Valid plunder should pass validation"""
        cmd = PlunderCommand(self.player1, 1)
        valid, msg = cmd.validate(self.game_state)
        self.assertTrue(valid)

    # Probe validation tests
    def test_probe_insufficient_ships(self):
        """Cannot probe with fleet that has < 1 ship"""
        self.fleets[0].ships = 0
        cmd = ProbeCommand(self.player1, "F", 1, 2)
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("no ships", msg)

    def test_probe_disconnected_world(self):
        """Cannot probe world not adjacent"""
        cmd = ProbeCommand(self.player1, "F", 1, 99)
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("not adjacent", msg)

    def test_probe_valid(self):
        """Valid probe should pass validation"""
        cmd = ProbeCommand(self.player1, "F", 1, 2)
        valid, msg = cmd.validate(self.game_state)
        self.assertTrue(valid)

    # Artifact validation tests
    def test_view_artifact_not_owned(self):
        """Cannot view artifact you don't possess"""
        game_state, player1, player2, artifacts = create_artifact_game_state()
        # Artifact 3 is on player2's fleet
        cmd = ViewArtifactCommand(player1, 3)
        valid, msg = cmd.validate(game_state)
        self.assertFalse(valid)
        self.assertIn("not found", msg)

    def test_view_artifact_valid(self):
        """Valid view artifact should pass validation"""
        game_state, player1, player2, artifacts = create_artifact_game_state()
        # Artifact 1 is on player1's fleet
        cmd = ViewArtifactCommand(player1, 1)
        valid, msg = cmd.validate(game_state)
        self.assertTrue(valid)

    # Diplomacy validation tests
    def test_declare_relation_own_fleet(self):
        """Cannot declare relations with own fleet"""
        cmd = DeclareRelationCommand(self.player1, 1, 2, "PEACE")  # Both owned by player1
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("own fleet", msg)

    def test_declare_relation_nonexistent_target(self):
        """Cannot declare relations with nonexistent fleet"""
        cmd = DeclareRelationCommand(self.player1, 1, 999, "PEACE")
        valid, msg = cmd.validate(self.game_state)
        self.assertFalse(valid)
        self.assertIn("does not exist", msg)

    def test_declare_relation_valid(self):
        """Valid relation declaration should pass validation"""
        cmd = DeclareRelationCommand(self.player1, 1, 3, "PEACE")  # Fleet 3 belongs to player2
        valid, msg = cmd.validate(self.game_state)
        self.assertTrue(valid)


if __name__ == '__main__':
    unittest.main()
