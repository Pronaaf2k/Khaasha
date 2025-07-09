# logic/user_operations.py
from logic.db_handler import get_db_connection

def add_user(username, password, role):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, role FROM users ORDER BY username")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_user(username, password, role):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password=?, role=? WHERE username=?", (password, role, username))
    conn.commit()
    conn.close()

def delete_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()
