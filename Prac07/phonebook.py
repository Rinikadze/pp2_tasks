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

def add_contact():
    name = input("Name: ")
    phone = input("Phone: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
        (name, phone)
    )
    conn.commit()
    cur.close()
    conn.close()
    print("Contact added!")

def show_all():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM contacts")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    cur.close()
    conn.close()

def search_by_name():
    name = input("Enter name: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM contacts WHERE name ILIKE %s",
        (f"%{name}%",)
    )
    print(cur.fetchall())
    cur.close()
    conn.close()

def search_by_prefix():
    prefix = input("Enter phone prefix: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM contacts WHERE phone LIKE %s",
        (f"{prefix}%",)
    )
    print(cur.fetchall())
    cur.close()
    conn.close()

def update_contact():
    old_name = input("Which name to update: ")
    new_name = input("New name (leave empty to skip): ")
    new_phone = input("New phone (leave empty to skip): ")
    conn = get_connection()
    cur = conn.cursor()
    if new_name:
        cur.execute(
            "UPDATE contacts SET name = %s WHERE name = %s",
            (new_name, old_name)
        )
    if new_phone:
        cur.execute(
            "UPDATE contacts SET phone = %s WHERE name = %s",
            (new_phone, old_name)
        )
    conn.commit()
    cur.close()
    conn.close()
    print("Contact updated!")

def delete_contact():
    choice = input("Delete by (name/phone): ")
    conn = get_connection()
    cur = conn.cursor()
    if choice == "name":
        name = input("Enter name: ")
        cur.execute("DELETE FROM contacts WHERE name = %s", (name,))
    elif choice == "phone":
        phone = input("Enter phone: ")
        cur.execute("DELETE FROM contacts WHERE phone = %s", (phone,))
    conn.commit()
    cur.close()
    conn.close()
    print("Contact deleted!")

def menu():
    while True:
        print("\n--- PHONEBOOK ---")
        print("1. Add contact")
        print("2. Show all")
        print("3. Search by name")
        print("4. Search by phone prefix")
        print("5. Update contact")
        print("6. Delete contact")
        print("0. Exit")

        choice = input("Choose: ")

        if choice == "1":
            add_contact()
        elif choice == "2":
            show_all()
        elif choice == "3":
            search_by_name()
        elif choice == "4":
            search_by_prefix()
        elif choice == "5":
            update_contact()
        elif choice == "6":
            delete_contact()
        elif choice == "0":
            break

if __name__ == "__main__":
    menu()