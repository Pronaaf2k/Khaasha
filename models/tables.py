import sqlite3

def initialize_db():
    conn = sqlite3.connect("kitchen.db")
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('admin', 'staff'))
        )
    """)

    # Create products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # Create daily log table (with timestamp)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            product TEXT NOT NULL,
            received REAL DEFAULT 0,
            used REAL DEFAULT 0
        )
    """)

    # Create inventory table to track leftover stock
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product TEXT PRIMARY KEY,
            leftover REAL DEFAULT 0
        )
    """)

    # Add test users
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", ("Khaasha", "Khaasha22625", "admin"))

        print("✅ Sample users created: admin / staff")

    # Add sample products
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO products (name) VALUES (?)", [
            ("Tomatoes",), ("Potatoes",), ("Onions",), ("Carrots",)
        ])
        print("✅ Sample products added.")

    # Initialize inventory table with leftover based on existing daily_log data
    cursor.execute("SELECT COUNT(*) FROM inventory")
    if cursor.fetchone()[0] == 0:
        # For each product, calculate leftover = sum(received) - sum(used) from daily_log
        cursor.execute("SELECT name FROM products")
        products = cursor.fetchall()
        for (product_name,) in products:
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(received), 0) - COALESCE(SUM(used), 0)
                FROM daily_log
                WHERE product = ?
            """, (product_name,))
            leftover = cursor.fetchone()[0]
            cursor.execute("INSERT INTO inventory (product, leftover) VALUES (?, ?)", (product_name, leftover))
        print("✅ Inventory table initialized with leftover based on existing logs.")

    conn.commit()
    conn.close()
    print("✅ Database initialized.")

if __name__ == "__main__":
    initialize_db()
