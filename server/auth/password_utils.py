"""
Password hashing and verification utilities.
Uses bcrypt for secure password storage.
"""
import bcrypt
import re


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password as string
    """
    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        password: Plain text password to verify
        password_hash: Stored password hash

    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    except Exception:
        return False


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password meets security requirements.

    Requirements:
    - At least 8 characters
    - At least one letter
    - At least one number

    Args:
        password: Password to validate

    Returns:
        (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if not re.search(r'[a-zA-Z]', password):
        return False, "Password must contain at least one letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    return True, ""


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username meets requirements.

    Requirements:
    - 3-20 characters
    - Only alphanumeric and underscore
    - Must start with letter

    Args:
        username: Username to validate

    Returns:
        (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters"

    if len(username) > 20:
        return False, "Username must be at most 20 characters"

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
        return False, "Username must start with a letter and contain only letters, numbers, and underscores"

    return True, ""
