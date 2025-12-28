"""
Order formatting registry - data-driven order display.
Each order type registers its own formatter function.
"""
from typing import Callable, Dict


class OrderFormatterRegistry:
    """Registry for order formatters."""

    def __init__(self):
        self._formatters: Dict[str, Callable[[dict], str]] = {}

    def register(self, order_type: str):
        """Decorator to register an order formatter."""
        def decorator(func: Callable[[dict], str]):
            self._formatters[order_type] = func
            return func
        return decorator

    def format(self, order: dict) -> str:
        """Format an order using its registered formatter."""
        order_type = order.get("type", "UNKNOWN")
        formatter = self._formatters.get(order_type)

        if formatter:
            return formatter(order)
        else:
            return f"Unknown Order: {order_type}"


# Global registry instance
_registry = OrderFormatterRegistry()


# Register formatters for each order type
@_registry.register("MOVE")
def format_move(order: dict) -> str:
    return f"Move F{order['fleet_id']} -> W{order['path'][-1]}"


@_registry.register("BUILD")
def format_build(order: dict) -> str:
    target = f"F{order['target_id']}" if order.get("target_id") else order["target_type"]
    return f"Build {order['amount']} {target} at W{order['world_id']}"


@_registry.register("TRANSFER")
def format_transfer(order: dict) -> str:
    target = f"F{order['target_id']}" if order.get("target_id") else order["target_type"]
    return f"Transfer {order['amount']} from F{order['fleet_id']} to {target}"


@_registry.register("TRANSFER_ARTIFACT")
def format_transfer_artifact(order: dict) -> str:
    source = f"{order['source_type']}{order['source_id']}"
    if order['target_type'] == "F" and order.get('target_id'):
        target = f"F{order['target_id']}"
    else:
        target = "World"
    return f"Transfer Artifact {order['artifact_id']} from {source} to {target}"


@_registry.register("LOAD")
def format_load(order: dict) -> str:
    amt = order.get('amount')
    if amt is None:
        return f"F{order['fleet_id']} Load Max"
    else:
        return f"F{order['fleet_id']} Load {amt}"


@_registry.register("UNLOAD")
def format_unload(order: dict) -> str:
    amt = order.get('amount')
    if amt is None:
        return f"F{order['fleet_id']} Unload All"
    else:
        return f"F{order['fleet_id']} Unload {amt}"


@_registry.register("FIRE")
def format_fire(order: dict) -> str:
    target = f"F{order['target_id']}" if order.get("target_id") else f"World {order['sub_target']}"
    return f"F{order['fleet_id']} Fire at {target}"


@_registry.register("AMBUSH")
def format_ambush(order: dict) -> str:
    return f"F{order['fleet_id']} Ambush"


@_registry.register("MIGRATE")
def format_migrate(order: dict) -> str:
    return f"Migrate {order['amount']} population from W{order['world_id']} to W{order['dest_world']}"


def get_order_formatter():
    """Get the global order formatter registry."""
    return _registry
