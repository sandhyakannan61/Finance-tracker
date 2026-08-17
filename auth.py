import sqlite3
import hashlib

DATABASE_NAME = "finance.db"


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


# --------------------------------------------------
# PASSWORD HASHING
# --------------------------------------------------

def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# --------------------------------------------------
# CREATE USERS TABLE
# --------------------------------------------------

def create_users_table():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# --------------------------------------------------
# REGISTER USER
# --------------------------------------------------

def register_user(username, password):

    connection = get_connection()
    cursor = connection.cursor()

    hashed_password = hash_password(password)

    try:

        cursor.execute("""
            INSERT INTO users
            (username, password)
            VALUES (?, ?)
        """, (
            username,
            hashed_password
        ))

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


# --------------------------------------------------
# LOGIN USER
# --------------------------------------------------

def login_user(username, password):

    connection = get_connection()
    cursor = connection.cursor()

    hashed_password = hash_password(password)

    cursor.execute("""
        SELECT *
        FROM users
        WHERE username = ?
        AND password = ?
    """, (
        username,
        hashed_password
    ))

    user = cursor.fetchone()

    connection.close()

    return user


# --------------------------------------------------
# CREATE USERS TABLE
# --------------------------------------------------

create_users_table()