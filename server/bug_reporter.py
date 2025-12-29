"""
Bug report handling.
Saves player bug reports to a file for developers to review.
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from .game.entities import Player

logger = logging.getLogger(__name__)


class BugReporter:
    """Handles bug report submissions from players."""

    def __init__(self, reports_file: str = "data/bug_reports.jsonl"):
        """
        Initialize bug reporter.

        Args:
            reports_file: Path to JSON Lines file for storing reports
        """
        self.reports_file = Path(reports_file)
        self.reports_file.parent.mkdir(parents=True, exist_ok=True)

        # Create file if it doesn't exist
        if not self.reports_file.exists():
            self.reports_file.touch()

    async def handle_bug_report(self, player: Player, data: dict):
        """
        Handle a bug report from a player.

        Args:
            player: The player submitting the report
            data: Bug report data containing description, timestamp, etc.
        """
        description = data.get('description', '').strip()

        if not description:
            logger.warning(f"Empty bug report from {player.name}")
            return

        # Create bug report entry
        report = {
            'timestamp': data.get('timestamp', datetime.utcnow().isoformat()),
            'player_id': player.id,
            'player_name': player.name,
            'character_type': player.character_type,
            'game_turn': data.get('game_turn', 0),
            'description': description,
            'server_time': datetime.utcnow().isoformat()
        }

        # Append to bug reports file (JSON Lines format)
        try:
            with open(self.reports_file, 'a') as f:
                f.write(json.dumps(report) + '\n')

            logger.info(f"Bug report saved from {player.name}: {description[:50]}...")
        except Exception as e:
            logger.error(f"Failed to save bug report from {player.name}: {e}")

    def get_recent_reports(self, limit: int = 50) -> list[dict]:
        """
        Get recent bug reports.

        Args:
            limit: Maximum number of reports to return

        Returns:
            List of bug report dictionaries, most recent first
        """
        if not self.reports_file.exists():
            return []

        reports = []
        try:
            with open(self.reports_file, 'r') as f:
                for line in f:
                    if line.strip():
                        reports.append(json.loads(line))

            # Return most recent first
            return reports[-limit:][::-1]
        except Exception as e:
            logger.error(f"Failed to read bug reports: {e}")
            return []

    def get_report_count(self) -> int:
        """Get total number of bug reports."""
        if not self.reports_file.exists():
            return 0

        try:
            with open(self.reports_file, 'r') as f:
                return sum(1 for line in f if line.strip())
        except Exception as e:
            logger.error(f"Failed to count bug reports: {e}")
            return 0


# Global bug reporter instance
_bug_reporter: Optional[BugReporter] = None


def get_bug_reporter() -> BugReporter:
    """Get the global bug reporter instance."""
    global _bug_reporter
    if _bug_reporter is None:
        _bug_reporter = BugReporter()
    return _bug_reporter
