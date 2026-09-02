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
    ph = PasswordHasher()
    password_hash = ph.hash(password)

    if check_email_exists(email):
        raise EmailAlreadyExistsError (
            "This email is already registerded"
        )
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (username, email, password_hash, datetime.now().isoformat())
        )


def get_user(id: int):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * from users WHERE id = ?",
            (id,)
        ).fetchone()


def create_conversation(user_id: int, title: str):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO conversations (user_id, title, created_at)
            VALUES (?, ?, ?)
            """,
            (user_id, title, datetime.now().isoformat())
        )


def create_message(conv_id: int, author:str, content:str):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO messages (conversation_id, author, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (conv_id, author, content, datetime.now().isoformat())
        )


def check_password(user_id: str, password:str) -> bool:
    ph = PasswordHasher

    with get_connection() as conn:
        result = conn.execute(
            """
            SELECT password FROM users WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

    if result is None:
        return False

    password_hash = result[0]

    try:
        return ph.verify(password_hash, password)
    except VerifyMismatchError:
        return False

def check_email_exists(email:str):
    with get_connection() as conn:
            result = conn.execute(
                """
                SELECT 1 FROM users WHERE email = ?
                """,
                (email,)
            ).fetchone()
    return result is not None


def get_user_by_email(email:str, password:str):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id FROM users WHERE email = ?
            """,
            (email,)
        ).fetchone()


def login(email:str, password:str) -> bool:
    result = get_user_by_email(email, password)

    if result is None:
        return False

    return check_password(result[0], password)
