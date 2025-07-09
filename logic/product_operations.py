# logic/product_operations.py

from logic.db_handler import get_db_connection

def add_product(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def get_all_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM products ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_all_products_full():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM products ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_product(product_id, new_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name=? WHERE id=?", (new_name, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
