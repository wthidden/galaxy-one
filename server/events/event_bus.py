"""
Event bus for pub/sub pattern in StarWeb game.
Allows decoupled communication between game components.
"""
import asyncio
from typing import Callable, Dict, List, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class EventBus:
    """
    Central event bus for game events.

    Components can:
    - Publish events to notify others
    - Subscribe to event types to receive notifications
    - Unsubscribe from events
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_history: List[Any] = []
        self._max_history = 1000

    def subscribe(self, event_type: str, handler: Callable):
        """
        Subscribe to an event type.

        Args:
            event_type: The type of event to listen for (e.g., "FLEET_MOVED")
            handler: Async function to call when event is published
        """
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)
            logger.debug(f"Subscribed {handler.__name__} to {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable):
        """
        Unsubscribe from an event type.

        Args:
            event_type: The type of event
            handler: The handler to remove
        """
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
            logger.debug(f"Unsubscribed {handler.__name__} from {event_type}")

    async def publish(self, event: Any):
        """
        Publish an event to all subscribers.

        Args:
            event: GameEvent instance to publish
        """
        event_type = event.type

        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        # Notify subscribers
        handlers = self._subscribers.get(event_type, [])
        handlers += self._subscribers.get("*", [])  # Wildcard subscribers

        if not handlers:
            logger.debug(f"No subscribers for event {event_type}")
            return

        logger.debug(f"Publishing {event_type} to {len(handlers)} subscribers")

        # Call all handlers concurrently
        tasks = []
        for handler in handlers:
            try:
                task = asyncio.create_task(handler(event))
                tasks.append(task)
            except Exception as e:
                logger.error(f"Error creating task for {handler.__name__}: {e}")

        # Wait for all handlers to complete
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Handler {handlers[i].__name__} raised: {result}")

    def get_history(self, event_type: str = None, limit: int = 100) -> List[Any]:
        """
        Get event history.

        Args:
            event_type: Filter by event type, or None for all
            limit: Maximum number of events to return

        Returns:
            List of events in chronological order
        """
        if event_type:
            filtered = [e for e in self._event_history if e.type == event_type]
        else:
            filtered = self._event_history

        return filtered[-limit:]

    def clear_history(self):
        """Clear event history."""
        self._event_history.clear()

    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for an event type."""
        return len(self._subscribers.get(event_type, []))


# Global event bus instance
_event_bus = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def reset_event_bus():
    """Reset the global event bus (useful for testing)."""
    global _event_bus
    _event_bus = EventBus()
