"""
Authentication models for StarWeb.
"""
import uuid
from datetime import datetime
from typing import Optional


class PlayerAccount:
    """Player account with authentication credentials."""

    def __init__(
        self,
        username: str,
        password_hash: str,
        player_id: Optional[str] = None,
        email: Optional[str] = None,
        created_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None
    ):
        self.id = player_id or str(uuid.uuid4())
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.created_at = created_at or datetime.now()
        self.last_login = last_login

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "username": self.username,
            "password_hash": self.password_hash,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PlayerAccount':
        """Create PlayerAccount from dictionary."""
        return cls(
            username=data["username"],
            password_hash=data["password_hash"],
            player_id=data.get("id"),
            email=data.get("email"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            last_login=datetime.fromisoformat(data["last_login"]) if data.get("last_login") else None
        )

    def update_last_login(self):
        """Update last login timestamp to now."""
        self.last_login = datetime.now()

    def is_admin(self, config=None) -> bool:
        """
        Check if this account has admin privileges.

        Args:
            config: Optional GameConfig instance (will be loaded if not provided)

        Returns:
            True if username is in admin list, False otherwise
        """
        if config is None:
            from server.config import get_config
            config = get_config()
        return self.username.lower() in config.admin_users


class Session:
    """Player session with authentication token."""

    def __init__(
        self,
        player_id: str,
        token: Optional[str] = None,
        created_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None
    ):
        self.token = token or str(uuid.uuid4())
        self.player_id = player_id
        self.created_at = created_at or datetime.now()
        # Default expiration: 7 days from creation
        if expires_at is None:
            from datetime import timedelta
            self.expires_at = self.created_at + timedelta(days=7)
        else:
            self.expires_at = expires_at

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.now() > self.expires_at

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "token": self.token,
            "player_id": self.player_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Session':
        """Create Session from dictionary."""
        return cls(
            player_id=data["player_id"],
            token=data["token"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"])
        )
