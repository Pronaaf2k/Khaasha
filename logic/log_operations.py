# logic/log_operations.py

from datetime import datetime, date
from logic.db_handler import get_db_connection

def log_bought(product: str, amount: float):
    """Log new stock received."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO daily_log (timestamp, product, received, used) VALUES (?, ?, ?, 0)",
        (ts, product, amount)
    )
    conn.commit()
    conn.close()

def log_used(product: str, amount: float):
    """Log stock used."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO daily_log (timestamp, product, received, used) VALUES (?, ?, 0, ?)",
        (ts, product, amount)
    )
    conn.commit()
    conn.close()

def get_today_inventory_with_leftover():
    """
    For each product, returns:
    (product, bought_today, used_today, leftover_from_past, remaining_today)
    where 'today' is determined by Python's date.today().
    """
    today_str = date.today().isoformat()  # e.g. "2025-06-23"
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
          p.name AS product,
          COALESCE(today.bought,0) AS bought,
          COALESCE(today.used,0)   AS used,
          COALESCE(past.leftover,0) AS leftover_from_past,
          COALESCE(past.leftover,0)
            + COALESCE(today.bought,0)
            - COALESCE(today.used,0)
            AS remaining_today
        FROM products p
        LEFT JOIN (
          SELECT
            product,
            SUM(received) AS bought,
            SUM(used)     AS used
          FROM daily_log
          WHERE substr(timestamp,1,10) = ?
          GROUP BY product
        ) AS today
          ON p.name = today.product
        LEFT JOIN (
          SELECT
            product,
            SUM(received) - SUM(used) AS leftover
          FROM daily_log
          WHERE substr(timestamp,1,10) < ?
          GROUP BY product
        ) AS past
          ON p.name = past.product
        ORDER BY p.name
    """, (today_str, today_str))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_today_totals():
    """Return (total_bought_today, total_used_today) using Python's date."""
    today_str = date.today().isoformat()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT COALESCE(SUM(received),0) FROM daily_log WHERE substr(timestamp,1,10)=?",
        (today_str,)
    )
    total_bought = cur.fetchone()[0]
    cur.execute(
        "SELECT COALESCE(SUM(used),0)     FROM daily_log WHERE substr(timestamp,1,10)=?",
        (today_str,)
    )
    total_used = cur.fetchone()[0]
    conn.close()
    return total_bought, total_used

def get_full_inventory_history():
    """
    Returns full history:
    (log_date, product, bought_that_day, used_that_day,
     leftover_from_before_that_day, remaining_if_today_else_NULL)
    with 'today' by Python date.today().
    """
    today_str = date.today().isoformat()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
          substr(timestamp,1,10)        AS log_date,
          product,
          SUM(received)                AS bought,
          SUM(used)                    AS used,
          -- leftover from all days before this log_date
          (SELECT COALESCE(SUM(received)-SUM(used),0)
           FROM daily_log dl2
           WHERE dl2.product = daily_log.product
             AND substr(dl2.timestamp,1,10) < substr(daily_log.timestamp,1,10)
          ) AS leftover_from_past,
          -- remaining only on today's date
          CASE WHEN substr(timestamp,1,10)=?
               THEN (
                 SELECT COALESCE(SUM(received)-SUM(used),0)
                 FROM daily_log dl3
                 WHERE dl3.product = daily_log.product
                   AND substr(dl3.timestamp,1,10)<=?
               )
               ELSE NULL
          END AS remaining_today
        FROM daily_log
        GROUP BY log_date, product
        ORDER BY log_date DESC, product
    """, (today_str, today_str))
    rows = cur.fetchall()
    conn.close()
    return rows
    # ... existing imports and functions ...


def clear_inventory():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE inventory SET leftover = 0")
    conn.commit()
    conn.close()

def clear_daily_logs():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM daily_log")
    conn.commit()
    conn.close()
