import sqlite3

def validate_credentials(username, password):
    conn = sqlite3.connect("kitchen.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None