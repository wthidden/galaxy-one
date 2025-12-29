"""
Test command parsing - verifies all command syntaxes are correctly parsed.
"""
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from server.game.commands import parse_command
from server.game.commands import (
    MoveFleetCommand, BuildCommand, TransferCommand, TransferFromDefenseCommand,
    TransferArtifactCommand, LoadCommand, UnloadCommand, FireCommand,
    DefenseFireCommand, AmbushCommand, ProbeCommand, ScrapShipsCommand,
    JettisonCommand, UnloadConsumerGoodsCommand, ViewArtifactCommand,
    DeclareRelationCommand, PlunderCommand
)
from tests.fixtures import create_basic_game_state


class TestCommandParsing(unittest.TestCase):
    """Test that all command syntaxes parse correctly."""

    def setUp(self):
        """Set up test fixtures."""
        self.game_state, self.player1, self.player2, _, _ = create_basic_game_state()

    def test_move_command_single_hop(self):
        """Test: F5W10"""
        cmd = parse_command(self.player1, "F5W10", self.game_state)
        self.assertIsInstance(cmd, MoveFleetCommand)
        self.assertEqual(cmd.fleet_id, 5)
        self.assertEqual(cmd.path, [10])

    def test_move_command_multi_hop(self):
        """Test: F5W1W3W10"""
        cmd = parse_command(self.player1, "F5W1W3W10", self.game_state)
        self.assertIsInstance(cmd, MoveFleetCommand)
        self.assertEqual(cmd.fleet_id, 5)
        self.assertEqual(cmd.path, [1, 3, 10])

    def test_build_iships(self):
        """Test: W3B25I"""
        cmd = parse_command(self.player1, "W3B25I", self.game_state)
        self.assertIsInstance(cmd, BuildCommand)
        self.assertEqual(cmd.world_id, 3)
        self.assertEqual(cmd.amount, 25)
        self.assertEqual(cmd.target_type, "I")

    def test_build_pships(self):
        """Test: W3B10P"""
        cmd = parse_command(self.player1, "W3B10P", self.game_state)
        self.assertIsInstance(cmd, BuildCommand)
        self.assertEqual(cmd.world_id, 3)
        self.assertEqual(cmd.amount, 10)
        self.assertEqual(cmd.target_type, "P")

    def test_build_fleet(self):
        """Test: W3B15F7"""
        cmd = parse_command(self.player1, "W3B15F7", self.game_state)
        self.assertIsInstance(cmd, BuildCommand)
        self.assertEqual(cmd.world_id, 3)
        self.assertEqual(cmd.amount, 15)
        self.assertEqual(cmd.target_type, "F")
        self.assertEqual(cmd.target_id, 7)

    def test_build_industry(self):
        """Test: W3B2INDUSTRY"""
        cmd = parse_command(self.player1, "W3B2INDUSTRY", self.game_state)
        self.assertIsInstance(cmd, BuildCommand)
        self.assertEqual(cmd.world_id, 3)
        self.assertEqual(cmd.amount, 2)
        self.assertEqual(cmd.target_type, "INDUSTRY")

    def test_build_limit(self):
        """Test: W3B5LIMIT"""
        cmd = parse_command(self.player1, "W3B5LIMIT", self.game_state)
        self.assertIsInstance(cmd, BuildCommand)
        self.assertEqual(cmd.amount, 5)
        self.assertEqual(cmd.target_type, "LIMIT")

    def test_build_robot(self):
        """Test: W3B10ROBOT"""
        cmd = parse_command(self.player1, "W3B10ROBOT", self.game_state)
        self.assertIsInstance(cmd, BuildCommand)
        self.assertEqual(cmd.amount, 10)
        self.assertEqual(cmd.target_type, "ROBOT")

    def test_transfer_to_iships(self):
        """Test: F5T10I"""
        cmd = parse_command(self.player1, "F5T10I", self.game_state)
        self.assertIsInstance(cmd, TransferCommand)
        self.assertEqual(cmd.fleet_id, 5)
        self.assertEqual(cmd.amount, 10)
        self.assertEqual(cmd.target_type, "I")

    def test_transfer_to_pships(self):
        """Test: F5T10P"""
        cmd = parse_command(self.player1, "F5T10P", self.game_state)
        self.assertIsInstance(cmd, TransferCommand)
        self.assertEqual(cmd.target_type, "P")

    def test_transfer_to_fleet(self):
        """Test: F5T10F7"""
        cmd = parse_command(self.player1, "F5T10F7", self.game_state)
        self.assertIsInstance(cmd, TransferCommand)
        self.assertEqual(cmd.fleet_id, 5)
        self.assertEqual(cmd.amount, 10)
        self.assertEqual(cmd.target_type, "F")
        self.assertEqual(cmd.target_id, 7)

    def test_transfer_from_iships_to_fleet(self):
        """Test: I5T10F7"""
        cmd = parse_command(self.player1, "I5T10F7", self.game_state)
        self.assertIsInstance(cmd, TransferFromDefenseCommand)
        self.assertEqual(cmd.world_id, 5)
        self.assertEqual(cmd.amount, 10)
        self.assertEqual(cmd.source_type, "I")
        self.assertEqual(cmd.target_type, "F")
        self.assertEqual(cmd.target_id, 7)

    def test_transfer_from_pships_to_iships(self):
        """Test: P5T10I"""
        cmd = parse_command(self.player1, "P5T10I", self.game_state)
        self.assertIsInstance(cmd, TransferFromDefenseCommand)
        self.assertEqual(cmd.source_type, "P")
        self.assertEqual(cmd.target_type, "I")

    def test_transfer_artifact_fleet_to_fleet(self):
        """Test: F5TA3F7"""
        cmd = parse_command(self.player1, "F5TA3F7", self.game_state)
        self.assertIsInstance(cmd, TransferArtifactCommand)
        self.assertEqual(cmd.source_type, "F")
        self.assertEqual(cmd.source_id, 5)
        self.assertEqual(cmd.artifact_id, 3)
        self.assertEqual(cmd.target_type, "F")
        self.assertEqual(cmd.target_id, 7)

    def test_transfer_artifact_fleet_to_world(self):
        """Test: F5TA3W"""
        cmd = parse_command(self.player1, "F5TA3W", self.game_state)
        self.assertIsInstance(cmd, TransferArtifactCommand)
        self.assertEqual(cmd.source_type, "F")
        self.assertEqual(cmd.target_type, "W")

    def test_transfer_artifact_world_to_fleet(self):
        """Test: W5TA3F7"""
        cmd = parse_command(self.player1, "W5TA3F7", self.game_state)
        self.assertIsInstance(cmd, TransferArtifactCommand)
        self.assertEqual(cmd.source_type, "W")
        self.assertEqual(cmd.source_id, 5)
        self.assertEqual(cmd.artifact_id, 3)
        self.assertEqual(cmd.target_type, "F")

    def test_load_all(self):
        """Test: F5L"""
        cmd = parse_command(self.player1, "F5L", self.game_state)
        self.assertIsInstance(cmd, LoadCommand)
        self.assertEqual(cmd.fleet_id, 5)
        self.assertIsNone(cmd.amount)

    def test_load_amount(self):
        """Test: F5L10"""
        cmd = parse_command(self.player1, "F5L10", self.game_state)
        self.assertIsInstance(cmd, LoadCommand)
        self.assertEqual(cmd.amount, 10)

    def test_unload_all(self):
        """Test: F5U"""
        cmd = parse_command(self.player1, "F5U", self.game_state)
        self.assertIsInstance(cmd, UnloadCommand)
        self.assertEqual(cmd.fleet_id, 5)
        self.assertIsNone(cmd.amount)

    def test_unload_amount(self):
        """Test: F5U10"""
        cmd = parse_command(self.player1, "F5U10", self.game_state)
        self.assertIsInstance(cmd, UnloadCommand)
        self.assertEqual(cmd.amount, 10)

    def test_fire_at_fleet(self):
        """Test: F5AF10"""
        cmd = parse_command(self.player1, "F5AF10", self.game_state)
        self.assertIsInstance(cmd, FireCommand)
        self.assertEqual(cmd.fleet_id, 5)
        self.assertEqual(cmd.target_type, "FLEET")
        self.assertEqual(cmd.target_id, 10)

    def test_fire_at_pships(self):
        """Test: F5AP"""
        cmd = parse_command(self.player1, "F5AP", self.game_state)
        self.assertIsInstance(cmd, FireCommand)
        self.assertEqual(cmd.target_type, "WORLD")
        self.assertEqual(cmd.sub_target, "P")

    def test_fire_at_iships(self):
        """Test: F5AI"""
        cmd = parse_command(self.player1, "F5AI", self.game_state)
        self.assertIsInstance(cmd, FireCommand)
        self.assertEqual(cmd.sub_target, "I")

    def test_fire_at_defenses_and_neutralize(self):
        """Test: F5AH"""
        cmd = parse_command(self.player1, "F5AH", self.game_state)
        self.assertIsInstance(cmd, FireCommand)
        self.assertEqual(cmd.sub_target, "H")

    def test_defense_fire_iships_at_fleet(self):
        """Test: I5AF10"""
        cmd = parse_command(self.player1, "I5AF10", self.game_state)
        self.assertIsInstance(cmd, DefenseFireCommand)
        self.assertEqual(cmd.defense_type, "I")
        self.assertEqual(cmd.world_id, 5)
        self.assertEqual(cmd.target_type, "F")
        self.assertEqual(cmd.target_id, 10)

    def test_defense_fire_pships_at_fleet(self):
        """Test: P5AF10"""
        cmd = parse_command(self.player1, "P5AF10", self.game_state)
        self.assertIsInstance(cmd, DefenseFireCommand)
        self.assertEqual(cmd.defense_type, "P")

    def test_defense_fire_at_converts(self):
        """Test: I5AC"""
        cmd = parse_command(self.player1, "I5AC", self.game_state)
        self.assertIsInstance(cmd, DefenseFireCommand)
        self.assertEqual(cmd.target_type, "C")

    def test_ambush(self):
        """Test: F5A"""
        cmd = parse_command(self.player1, "F5A", self.game_state)
        self.assertIsInstance(cmd, AmbushCommand)
        self.assertEqual(cmd.fleet_id, 5)

    def test_probe_from_fleet(self):
        """Test: F5P10"""
        cmd = parse_command(self.player1, "F5P10", self.game_state)
        self.assertIsInstance(cmd, ProbeCommand)
        self.assertEqual(cmd.source_type, "F")
        self.assertEqual(cmd.source_id, 5)
        self.assertEqual(cmd.target_world, 10)

    def test_probe_from_iships(self):
        """Test: I5P10"""
        cmd = parse_command(self.player1, "I5P10", self.game_state)
        self.assertIsInstance(cmd, ProbeCommand)
        self.assertEqual(cmd.source_type, "I")
        self.assertEqual(cmd.source_id, 5)

    def test_probe_from_pships(self):
        """Test: P5P10"""
        cmd = parse_command(self.player1, "P5P10", self.game_state)
        self.assertIsInstance(cmd, ProbeCommand)
        self.assertEqual(cmd.source_type, "P")

    def test_scrap_ships(self):
        """Test: W5S3"""
        cmd = parse_command(self.player1, "W5S3", self.game_state)
        self.assertIsInstance(cmd, ScrapShipsCommand)
        self.assertEqual(cmd.world_id, 5)
        self.assertEqual(cmd.amount, 3)

    def test_jettison_all(self):
        """Test: F5J"""
        cmd = parse_command(self.player1, "F5J", self.game_state)
        self.assertIsInstance(cmd, JettisonCommand)
        self.assertEqual(cmd.fleet_id, 5)
        self.assertIsNone(cmd.amount)

    def test_jettison_amount(self):
        """Test: F5J10"""
        cmd = parse_command(self.player1, "F5J10", self.game_state)
        self.assertIsInstance(cmd, JettisonCommand)
        self.assertEqual(cmd.amount, 10)

    def test_consumer_goods_all(self):
        """Test: F5N"""
        cmd = parse_command(self.player1, "F5N", self.game_state)
        self.assertIsInstance(cmd, UnloadConsumerGoodsCommand)
        self.assertEqual(cmd.fleet_id, 5)
        self.assertIsNone(cmd.amount)

    def test_consumer_goods_amount(self):
        """Test: F5N10"""
        cmd = parse_command(self.player1, "F5N10", self.game_state)
        self.assertIsInstance(cmd, UnloadConsumerGoodsCommand)
        self.assertEqual(cmd.amount, 10)

    def test_view_artifact(self):
        """Test: V3"""
        cmd = parse_command(self.player1, "V3", self.game_state)
        self.assertIsInstance(cmd, ViewArtifactCommand)
        self.assertEqual(cmd.artifact_id, 3)
        self.assertIsNone(cmd.location_type)

    def test_view_artifact_on_fleet(self):
        """Test: V3F5"""
        cmd = parse_command(self.player1, "V3F5", self.game_state)
        self.assertIsInstance(cmd, ViewArtifactCommand)
        self.assertEqual(cmd.artifact_id, 3)
        self.assertEqual(cmd.location_type, "F")
        self.assertEqual(cmd.location_id, 5)

    def test_view_artifact_on_world(self):
        """Test: V3W"""
        cmd = parse_command(self.player1, "V3W", self.game_state)
        self.assertIsInstance(cmd, ViewArtifactCommand)
        self.assertEqual(cmd.artifact_id, 3)
        self.assertEqual(cmd.location_type, "W")

    def test_declare_peace(self):
        """Test: F5Q10"""
        cmd = parse_command(self.player1, "F5Q10", self.game_state)
        self.assertIsInstance(cmd, DeclareRelationCommand)
        self.assertEqual(cmd.fleet_id, 5)
        self.assertEqual(cmd.target_fleet_id, 10)
        self.assertEqual(cmd.relation_type, "PEACE")

    def test_declare_war(self):
        """Test: F5X10"""
        cmd = parse_command(self.player1, "F5X10", self.game_state)
        self.assertIsInstance(cmd, DeclareRelationCommand)
        self.assertEqual(cmd.fleet_id, 5)
        self.assertEqual(cmd.target_fleet_id, 10)
        self.assertEqual(cmd.relation_type, "WAR")

    def test_plunder(self):
        """Test: W5X"""
        cmd = parse_command(self.player1, "W5X", self.game_state)
        self.assertIsInstance(cmd, PlunderCommand)
        self.assertEqual(cmd.world_id, 5)

    def test_invalid_command(self):
        """Test invalid command returns None"""
        cmd = parse_command(self.player1, "INVALID", self.game_state)
        self.assertIsNone(cmd)

    def test_empty_command(self):
        """Test empty command returns None"""
        cmd = parse_command(self.player1, "", self.game_state)
        self.assertIsNone(cmd)


if __name__ == '__main__':
    unittest.main()
