"""
Persistence for player accounts and sessions.
"""
import json
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class AccountPersistence:
    """Handles saving and loading player accounts and sessions."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.accounts_file = self.data_dir / "accounts.json"
        self.sessions_file = self.data_dir / "sessions.json"

    def save_accounts(self, accounts: dict):
        """
        Save player accounts to disk.

        Args:
            accounts: Dictionary of username -> PlayerAccount
        """
        try:
            accounts_data = [
                account.to_dict()
                for account in accounts.values()
            ]

            with open(self.accounts_file, 'w') as f:
                json.dump(accounts_data, f, indent=2)

            logger.info(f"Saved {len(accounts_data)} accounts to {self.accounts_file}")
        except Exception as e:
            logger.error(f"Failed to save accounts: {e}")

    def load_accounts(self) -> list:
        """
        Load player accounts from disk.

        Returns:
            List of account dictionaries
        """
        if not self.accounts_file.exists():
            logger.info("No accounts file found, starting with empty accounts")
            return []

        try:
            with open(self.accounts_file, 'r') as f:
                accounts_data = json.load(f)

            logger.info(f"Loaded {len(accounts_data)} accounts from {self.accounts_file}")
            return accounts_data
        except Exception as e:
            logger.error(f"Failed to load accounts: {e}")
            return []

    def save_sessions(self, sessions: dict):
        """
        Save active sessions to disk.

        Args:
            sessions: Dictionary of token -> Session
        """
        try:
            sessions_data = [
                session.to_dict()
                for session in sessions.values()
            ]

            with open(self.sessions_file, 'w') as f:
                json.dump(sessions_data, f, indent=2)

            logger.info(f"Saved {len(sessions_data)} sessions to {self.sessions_file}")
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")

    def load_sessions(self) -> list:
        """
        Load sessions from disk.

        Returns:
            List of session dictionaries
        """
        if not self.sessions_file.exists():
            logger.info("No sessions file found, starting with empty sessions")
            return []

        try:
            with open(self.sessions_file, 'r') as f:
                sessions_data = json.load(f)

            logger.info(f"Loaded {len(sessions_data)} sessions from {self.sessions_file}")
            return sessions_data
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
            return []


# Global persistence instance
_account_persistence: Optional[AccountPersistence] = None


def get_account_persistence() -> AccountPersistence:
    """Get the global account persistence instance."""
    global _account_persistence
    if _account_persistence is None:
        _account_persistence = AccountPersistence()
    return _account_persistence
