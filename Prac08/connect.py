import psycopg2
import csv
import config

def get_connection():
    return psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )

def import_csv():
    conn = get_connection()
    cur = conn.cursor()
    with open("contacts.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            name = row[0]
            phone = row[1]
            cur.execute(
                "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
                (name, phone)
            )

    conn.commit()
    cur.close()
    conn.close()

    print("CSV imported successfully!")

if __name__ == "__main__":
    import_csv()