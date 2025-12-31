"""
Authentication manager for player accounts.
"""
import logging
from typing import Optional, Dict, Tuple
from .models import PlayerAccount, Session
from .password_utils import hash_password, verify_password, validate_password, validate_username
from .session_manager import get_session_manager

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages player authentication and accounts."""

    def __init__(self):
        self._accounts: Dict[str, PlayerAccount] = {}  # username -> PlayerAccount
        self._accounts_by_id: Dict[str, PlayerAccount] = {}  # player_id -> PlayerAccount
        self.session_manager = get_session_manager()

    def signup(self, username: str, password: str, email: Optional[str] = None) -> Tuple[bool, str, Optional[Session]]:
        """
        Create a new player account.

        Args:
            username: Desired username
            password: Plain text password
            email: Optional email address

        Returns:
            (success, message, session) - session is None on failure
        """
        # Validate username
        valid, error = validate_username(username)
        if not valid:
            return False, error, None

        # Check if username already exists
        if username.lower() in [u.lower() for u in self._accounts.keys()]:
            return False, "Username already exists", None

        # Validate password
        valid, error = validate_password(password)
        if not valid:
            return False, error, None

        # Create account
        password_hash = hash_password(password)
        account = PlayerAccount(
            username=username,
            password_hash=password_hash,
            email=email
        )

        self._accounts[username] = account
        self._accounts_by_id[account.id] = account

        # Create session
        session = self.session_manager.create_session(account.id)

        logger.info(f"New account created: {username} (ID: {account.id})")
        return True, "Account created successfully", session

    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[Session]]:
        """
        Authenticate a player and create a session.

        Args:
            username: Username
            password: Plain text password

        Returns:
            (success, message, session) - session is None on failure
        """
        # Find account (case-insensitive username lookup)
        account = None
        for stored_username, stored_account in self._accounts.items():
            if stored_username.lower() == username.lower():
                account = stored_account
                break

        if not account:
            return False, "Invalid username or password", None

        # Verify password
        if not verify_password(password, account.password_hash):
            return False, "Invalid username or password", None

        # Update last login
        account.update_last_login()

        # Create session
        session = self.session_manager.create_session(account.id)

        logger.info(f"Player logged in: {username} (ID: {account.id})")
        return True, "Login successful", session

    def logout(self, token: str) -> Tuple[bool, str]:
        """
        Logout a player by invalidating their session.

        Args:
            token: Session token

        Returns:
            (success, message)
        """
        player_id = self.session_manager.validate_token(token)
        if not player_id:
            return False, "Invalid session"

        self.session_manager.invalidate_session(token)
        logger.info(f"Player logged out: {player_id}")
        return True, "Logged out successfully"

    def validate_session(self, token: str) -> Optional[PlayerAccount]:
        """
        Validate a session token and return the player account.

        Args:
            token: Session token

        Returns:
            PlayerAccount if valid, None otherwise
        """
        player_id = self.session_manager.validate_token(token)
        if not player_id:
            return None

        return self._accounts_by_id.get(player_id)

    def get_account(self, username: str) -> Optional[PlayerAccount]:
        """
        Get account by username.

        Args:
            username: Username to lookup

        Returns:
            PlayerAccount if found, None otherwise
        """
        return self._accounts.get(username)

    def get_account_by_id(self, player_id: str) -> Optional[PlayerAccount]:
        """
        Get account by player ID.

        Args:
            player_id: Player ID to lookup

        Returns:
            PlayerAccount if found, None otherwise
        """
        return self._accounts_by_id.get(player_id)

    def get_all_accounts(self) -> Dict[str, PlayerAccount]:
        """
        Get all player accounts.

        Returns:
            Dictionary of username -> PlayerAccount
        """
        return dict(self._accounts)

    def load_accounts(self, accounts_data: list):
        """
        Load accounts from persistence.

        Args:
            accounts_data: List of account dictionaries
        """
        for data in accounts_data:
            account = PlayerAccount.from_dict(data)
            self._accounts[account.username] = account
            self._accounts_by_id[account.id] = account

        logger.info(f"Loaded {len(self._accounts)} player accounts")


# Global auth manager instance
_auth_manager: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """Get the global auth manager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager
