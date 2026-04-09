import psycopg2
import config

def get_connection():
    return psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )

def search(pattern):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
    rows = cur.fetchall()
    for row in rows:
        print(row)
    cur.close()
    conn.close()


def upsert(name, phone):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
    conn.commit()
    cur.close()
    conn.close()
    print("Upsert done!")

def bulk_insert(names, phones):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL bulk_insert_contacts(%s, %s)", (names, phones))
    conn.commit()
    cur.close()
    conn.close()
    print("Bulk insert done!")

def get_paginated(limit, offset):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM get_contacts_paginated(%s, %s)",
        (limit, offset)
    )
    rows = cur.fetchall()
    for row in rows:
        print(row)
    cur.close()
    conn.close()

def delete(value):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL delete_contact(%s)", (value,))
    conn.commit()
    cur.close()
    conn.close()
    print("Deleted!")

if __name__ == "__main__":
    upsert("Ali", "12345")
    upsert("Ali", "99999")
    search("Ali")
    bulk_insert(
        ["Bob", "Charlie"],
        ["55555", "abc"]  # abc будет invalid
    )
    get_paginated(5, 0)
    delete("Bob")