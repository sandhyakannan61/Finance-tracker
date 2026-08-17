import sqlite3

DATABASE_NAME = "finance.db"


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


# ==================================================
# INITIALIZE DATABASE
# ==================================================

def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------
    # USERS TABLE
    # --------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # --------------------------------------------------
    # TRANSACTIONS TABLE
    # --------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Check old transactions table
    cursor.execute("PRAGMA table_info(transactions)")

    transaction_columns = [
        column["name"]
        for column in cursor.fetchall()
    ]

    # Add user_id if old database doesn't have it
    if "user_id" not in transaction_columns:

        cursor.execute("""
            ALTER TABLE transactions
            ADD COLUMN user_id INTEGER
        """)

    # --------------------------------------------------
    # SETTINGS TABLE
    # --------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            monthly_budget REAL NOT NULL DEFAULT 10000,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Check old settings table
    cursor.execute("PRAGMA table_info(settings)")

    settings_columns = [
        column["name"]
        for column in cursor.fetchall()
    ]

    # Add user_id if old database doesn't have it
    if "user_id" not in settings_columns:

        cursor.execute("""
            ALTER TABLE settings
            ADD COLUMN user_id INTEGER
        """)

    # --------------------------------------------------
    # FIND FIRST USER
    # --------------------------------------------------

    cursor.execute("""
        SELECT id
        FROM users
        ORDER BY id
        LIMIT 1
    """)

    first_user = cursor.fetchone()

    # --------------------------------------------------
    # ASSIGN OLD TRANSACTIONS TO FIRST USER
    # --------------------------------------------------

    if first_user:

        cursor.execute("""
            UPDATE transactions
            SET user_id = ?
            WHERE user_id IS NULL
        """, (
            first_user["id"],
        ))

        # --------------------------------------------------
        # ASSIGN OLD SETTINGS TO FIRST USER
        # --------------------------------------------------

        cursor.execute("""
            UPDATE settings
            SET user_id = ?
            WHERE user_id IS NULL
        """, (
            first_user["id"],
        ))

    connection.commit()
    connection.close()


# ==================================================
# ADD TRANSACTION
# ==================================================

def add_transaction(
    user_id,
    transaction_type,
    amount,
    category,
    transaction_date,
    description
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO transactions (
            user_id,
            transaction_type,
            amount,
            category,
            date,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        transaction_type,
        amount,
        category,
        str(transaction_date),
        description
    ))

    connection.commit()
    connection.close()


# ==================================================
# GET USER TRANSACTIONS
# ==================================================

def get_transactions(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM transactions
        WHERE user_id = ?
        ORDER BY date DESC, id DESC
    """, (
        user_id,
    ))

    transactions = cursor.fetchall()

    connection.close()

    return transactions


# ==================================================
# UPDATE TRANSACTION
# ==================================================

def update_transaction(
    transaction_id,
    user_id,
    transaction_type,
    amount,
    category,
    transaction_date,
    description
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE transactions
        SET
            transaction_type = ?,
            amount = ?,
            category = ?,
            date = ?,
            description = ?
        WHERE id = ?
        AND user_id = ?
    """, (
        transaction_type,
        amount,
        category,
        str(transaction_date),
        description,
        transaction_id,
        user_id
    ))

    connection.commit()
    connection.close()


# ==================================================
# DELETE TRANSACTION
# ==================================================

def delete_transaction(
    transaction_id,
    user_id
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM transactions
        WHERE id = ?
        AND user_id = ?
    """, (
        transaction_id,
        user_id
    ))

    connection.commit()
    connection.close()


# ==================================================
# GET USER BUDGET
# ==================================================

def get_budget(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT monthly_budget
        FROM settings
        WHERE user_id = ?
    """, (
        user_id,
    ))

    result = cursor.fetchone()

    connection.close()

    if result:
        return result["monthly_budget"]

    return 10000


# ==================================================
# UPDATE USER BUDGET
# ==================================================

def update_budget(
    user_id,
    amount
):

    connection = get_connection()
    cursor = connection.cursor()

    # Check whether user already has a budget
    cursor.execute("""
        SELECT id
        FROM settings
        WHERE user_id = ?
    """, (
        user_id,
    ))

    existing = cursor.fetchone()

    if existing:

        cursor.execute("""
            UPDATE settings
            SET monthly_budget = ?
            WHERE user_id = ?
        """, (
            amount,
            user_id
        ))

    else:

        cursor.execute("""
            INSERT INTO settings (
                user_id,
                monthly_budget
            )
            VALUES (?, ?)
        """, (
            user_id,
            amount
        ))

    connection.commit()
    connection.close()


# ==================================================
# INITIALIZE DATABASE
# ==================================================

initialize_database()