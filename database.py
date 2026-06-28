import sqlite3
from datetime import datetime, date

DB_NAME = "tracker.db"


def connect():
    return sqlite3.connect(DB_NAME)


def setup_database():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS businesses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        yelp_id TEXT UNIQUE,
        name TEXT,
        phone TEXT,
        yelp_url TEXT,
        website TEXT,
        email TEXT,
        category TEXT,
        city TEXT,
        status TEXT DEFAULT 'not_done',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        city TEXT NOT NULL,
        UNIQUE(category, city)
        )      
    """)

    conn.commit()
    conn.close()


def save_activity(business, category, city):
    conn = connect()
    cursor = conn.cursor()

    yelp_id = business.get("id")
    name = business.get("name")
    phone = business.get("display_phone") or business.get("phone")
    yelp_url = business.get("url")
    created = date.today().isoformat()

    cursor.execute("""
        INSERT OR IGNORE INTO businesses (yelp_id, name, phone, yelp_url, website, email, category, city, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        yelp_id, name, phone, yelp_url, None, None, category, city, created
    ))

    added = cursor.rowcount

    conn.commit()
    conn.close()

    return added


def show_businesses(status_filter, search="", limit=10, offset=0):
    conn = connect()
    cursor = conn.cursor()

    search = search or ""
    search = f"%{search}%"

    if status_filter == "all":
        cursor.execute("""
        SELECT id, yelp_id, name, phone, yelp_url, website, email, category, city, status, created_at
        FROM businesses
        WHERE 
            name LIKE ?
            OR phone LIKE ?
            OR website LIKE ?
            OR email LIKE ?
            OR category LIKE ?
            OR city LIKE ?
        ORDER BY id ASC
        LIMIT ? OFFSET ?             
        """, (search, search, search, search, search, search, limit, offset))
    else:
        cursor.execute("""
        SELECT id, yelp_id, name, phone, yelp_url, website, email, category, city, status, created_at
        FROM businesses
        WHERE status = ?
        AND (
            name LIKE ?
            OR phone LIKE ?
            OR website LIKE ?
            OR email LIKE ?
            OR category LIKE ?
            OR city LIKE ?
        )
        ORDER BY id ASC
        LIMIT ? OFFSET ?             
        """, (status_filter, search, search, search, search, search, search, limit, offset))

    rows = cursor.fetchall()

    conn.close()

    return rows


def update_businesses():
    conn = connect()
    cursor = conn.cursor()

    created = date.today().isoformat()

    try:
        cursor.execute("""
            UPDATE businesses
            SET created_at = ?
            WHERE created_at IS not NULL
        """, (created,))
    except:
        print("e")

    conn.commit()
    conn.close()


def update_businesses_status(business_id, status):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
       UPDATE businesses
       SET status = ?
       WHERE id = ?             
    """, (status, business_id))

    conn.commit()
    conn.close()


def get_business_count(status):
    conn = connect()
    cursor = conn.cursor()

    if status == "all":
        cursor.execute("SELECT COUNT(*) FROM businesses")
    else:
        cursor.execute(
            "SELECT COUNT(*) FROM businesses WHERE status = ?",
            (status,)
        )

    count = cursor.fetchone()[0]

    conn.close()

    return count


def get_dashboard_stats():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM businesses")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM businesses
        WHERE email IS NOT NULL
        AND email != ''
    """)
    with_email = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM businesses
        WHERE website IS NOT NULL
        AND website != ''
    """)
    with_website = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM businesses
        WHERE status = 'emailed'
    """)
    contacted = cursor.fetchone()[0]

    conn.close()

    return {
        "total": total,
        "email": with_email,
        "website": with_website,
        "contacted": contacted
    }


def searches_already_done(category,city):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 
        FROM searches
        WHERE category = ? AND city = ?          
    """, (category, city))

    exists = cursor.fetchone() is not None 

    conn.close()
    return exists


def save_search(category, city):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO searches (
                   category, 
                   city
        )
        VALUES (?,?)
    """, (category, city))

    conn.commit()
    conn.close()