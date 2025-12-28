"""
Message sender abstraction for sending various message types to clients.
Provides a clean API for sending updates, deltas, events, etc.
"""
import json
import logging
from typing import Optional
import time

from .game.entities import Player
from .game.state import get_game_state
from .data.delta import calculate_state_delta
from .formatting import get_order_formatter
from websockets.protocol import State

logger = logging.getLogger(__name__)


class MessageSender:
    """
    Handles sending messages to clients with proper formatting.
    """

    async def send_welcome(self, player: Player):
        """
        Send welcome message to a new connection.

        Args:
            player: The player who just connected
        """
        await self._send(player, {
            "type": "welcome",
            "id": player.id,
            "name": player.name
        })

    async def send_full_update(self, player: Player):
        """
        Send complete game state to player.

        Args:
            player: The player to send to
        """
        state = self._build_state(player)
        await self._send(player, {
            "type": "update",
            "state": state
        })

        # Update snapshot for future deltas
        player.last_state_snapshot = state

    async def send_delta_update(self, player: Player):
        """
        Send only changes since last update.

        Args:
            player: The player to send to
        """
        current_state = self._build_state(player)

        if player.last_state_snapshot is None:
            # No previous snapshot, send full update
            await self.send_full_update(player)
            return

        # Calculate delta
        delta = calculate_state_delta(player.last_state_snapshot, current_state)

        if delta:
            await self._send(player, {
                "type": "delta",
                "changes": delta
            })

        # Update snapshot
        player.last_state_snapshot = current_state

    async def send_timer_tick(self, player: Player):
        """
        Send lightweight timer update.

        Args:
            player: The player to send to
        """
        game_state = get_game_state()
        time_remaining = max(0, int(game_state.turn_end_time - time.time()))

        await self._send(player, {
            "type": "timer",
            "time_remaining": time_remaining,
            "players_ready": len(game_state.players_ready),
            "total_players": len(game_state.players)
        })

    async def send_info(self, player: Player, message: str):
        """
        Send informational message.

        Args:
            player: The player to send to
            message: The info message
        """
        await self._send(player, {
            "type": "info",
            "text": message
        })

    async def send_error(self, player: Player, message: str):
        """
        Send error message.

        Args:
            player: The player to send to
            message: The error message
        """
        await self._send(player, {
            "type": "error",
            "text": message
        })

    async def send_event(self, player: Player, message: str, event_type: str = "info"):
        """
        Send game event message.

        Args:
            player: The player to send to
            message: The event message
            event_type: Type of event (info, combat, capture, ambush)
        """
        await self._send(player, {
            "type": "event",
            "text": message,
            "event_type": event_type
        })

    async def send_animation(self, player: Player, animation_data: dict):
        """
        Send animation trigger to client.

        Args:
            player: The player to send to
            animation_data: Animation parameters
        """
        animation_data["type"] = "animate"
        await self._send(player, animation_data)

    async def send_chat(self, player: Player, from_player: str, message: str, channel: str = "public"):
        """
        Send chat message.

        Args:
            player: The player to send to
            from_player: Name of sender
            message: Chat message
            channel: Chat channel (public, private, alliance)
        """
        await self._send(player, {
            "type": "chat",
            "from": from_player,
            "message": message,
            "channel": channel
        })

    async def send_alliance_update(self, player: Player, alliance_data: dict):
        """
        Send alliance information update.

        Args:
            player: The player to send to
            alliance_data: Alliance information
        """
        await self._send(player, {
            "type": "alliance_update",
            **alliance_data
        })

    def _build_state(self, player: Player) -> dict:
        """
        Build complete game state for a player.

        Args:
            player: The player

        Returns:
            Complete state dict
        """
        game_state = get_game_state()
        visible_worlds = {}

        # Determine visible worlds
        presence_worlds = set()
        for w in player.worlds:
            presence_worlds.add(w.id)
        for f in player.fleets:
            presence_worlds.add(f.world.id)

        # Update known worlds
        for wid in presence_worlds:
            player.known_worlds[wid] = game_state.game_turn
            world = game_state.get_world(wid)
            if world:
                for neighbor in world.connections:
                    if neighbor not in player.known_worlds:
                        player.known_worlds[neighbor] = game_state.game_turn

        # Build visible worlds dict
        for wid, turn in player.known_worlds.items():
            world = game_state.get_world(wid)
            if world:
                visible_worlds[wid] = world.to_dict(
                    viewer=player,
                    turn_last_seen=turn
                )

        # Build visible fleets list
        visible_fleets = []
        for f in game_state.fleets.values():
            if f.owner == player or f.world.id in presence_worlds:
                visible_fleets.append(f.to_dict(viewer=player))

        # Format orders
        formatted_orders = [self._format_order(o) for o in player.orders]

        time_remaining = max(0, int(game_state.turn_end_time - time.time()))

        # Build players list (scoreboard)
        players_list = []
        for p in game_state.get_all_players():
            players_list.append({
                "name": p.name,
                "score": p.score,
                "character_type": p.character_type,
                "ready": p in game_state.players_ready
            })

        return {
            "worlds": visible_worlds,
            "fleets": visible_fleets,
            "player_name": player.name,
            "character_type": player.character_type,
            "score": player.score,
            "game_turn": game_state.game_turn,
            "time_remaining": time_remaining,
            "players_ready": len(game_state.players_ready),
            "total_players": len(game_state.players),
            "players": players_list,
            "orders": formatted_orders
        }

    def _format_order(self, order: dict) -> str:
        """Format order dict as human-readable string using registry."""
        formatter = get_order_formatter()
        return formatter.format(order)

    async def _send(self, player: Player, message: dict):
        """
        Send a message to a player.

        Args:
            player: The player
            message: The message dict
        """
        try:
            # Check if websocket is open using the state attribute (websockets >= 11.0)
            if hasattr(player.websocket, 'state'):
                if player.websocket.state == State.OPEN:
                    await player.websocket.send(json.dumps(message))
            # Fallback for older websockets library versions
            elif hasattr(player.websocket, 'open'):
                if player.websocket.open:
                    await player.websocket.send(json.dumps(message))
            else:
                logger.error(f"Player {player.name} has unknown websocket type: {type(player.websocket)}")
        except Exception as e:
            logger.error(f"Error sending message to {player.name}: {e}")


# Global message sender instance
_message_sender = None


def get_message_sender() -> MessageSender:
    """Get the global message sender instance."""
    global _message_sender
    if _message_sender is None:
        _message_sender = MessageSender()
    return _message_sender


def reset_message_sender():
    """Reset the global message sender (useful for testing)."""
    global _message_sender
    _message_sender = MessageSender()
