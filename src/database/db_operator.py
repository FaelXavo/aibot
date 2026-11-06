"""Database access layer for the application.

This module handles all SQLite interactions related to users, conversations,
and messages. It keeps database logic isolated from the rest of the app so
that business logic can remain simpler and easier to test.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from exceptions import EmailAlreadyExistsError


DB_PATH = Path(__file__).parent / "app.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_user(username: str, email: str, password: str):
    """Create a new user with a hashed password."""
    # Hash the password before saving it to the database.
    # Argon2 is used for secure password storage.
    ph = PasswordHasher()
    password_hash = ph.hash(password)

    if check_email_exists(email):
        raise EmailAlreadyExistsError(
            "This email is already registerded"
        )

    # Insert the user record into the database.
    # The current timestamp is stored in ISO format for easier debugging and
    # sorting.
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (username, email, password_hash, datetime.now().isoformat())
        )


def get_user(id: int):
    """Return a user by matching the given database id."""
    # Fetch one row only because the id should be unique.
    with get_connection() as conn:
        return conn.execute(
            "SELECT * from users WHERE id = ?",
            (id,)
        ).fetchone()


def create_conversation(user_id: int, title: str):
    """Create a new conversation linked to a specific user."""
    # A conversation belongs to one user and stores a title plus creation time.
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO conversations (user_id, title, created_at)
            VALUES (?, ?, ?)
            """,
            (user_id, title, datetime.now().isoformat())
        )


def create_message(conv_id: int, author: str, content: str):
    """Insert a message into a conversation."""
    # Messages are stored with their conversation id, sender, payload, and
    # creation timestamp.
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO messages (conversation_id, author, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (conv_id, author, content, datetime.now().isoformat())
        )


def check_password(user_id: str, password: str) -> bool:
    """Validate whether the provided password matches the stored hash."""
    # Create a verifier instance for the Argon2 hashing algorithm.
    ph = PasswordHasher()

    # Retrieve the stored password hash for the target user.
    with get_connection() as conn:
        result = conn.execute(
            """
            SELECT password_hash FROM users WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

    # If there is no such user, the password cannot be valid.
    if result is None:
        return False

    password_hash = result[0]

    try:
        # Verify the plain-text entered password against the stored hash.
        return ph.verify(password_hash, password)
    except VerifyMismatchError:
        # A password mismatch is treated as a failed login attempt.
        return False


def check_email_exists(email: str):
    """Return True if an email address is already registered."""
    # We check only for the existence of the email and do not return the row
    # itself because this helper is used to validate uniqueness.
    with get_connection() as conn:
        result = conn.execute(
            """
            SELECT 1 FROM users WHERE email = ?
            """,
            (email,)
        ).fetchone()
    return result is not None


def get_user_by_email(email: str):
    """Find a user by email address and return their basic identity data."""
    # This function is mainly used for login flow and email lookup.
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id FROM users WHERE email = ?
            """,
            (email,)
        ).fetchone()


def login(email: str, password: str):
    """Authenticate a user by email and password."""
    # First, find the user by email.
    result = get_user_by_email(email)

    # If no user is found, login fails immediately.
    if result is None:
        return None

    # If the stored password matches the provided password, return the user id.
    if check_password(result[0], password):
        return result[0]

    # Otherwise, the authentication attempt fails.
    return None

