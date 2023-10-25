import sqlite3

# Connect to the database
conn = sqlite3.connect('comic.db')

# Create a cursor object
cursor = conn.cursor()

def menu():
    desired = input("What do you want to do? (drop, create, check, exit): ")
    if desired == "drop":
        cursor.execute('DROP TABLE comics')
        cursor.execute('CREATE TABLE IF NOT EXISTS comics (rowid INTEGER PRIMARY KEY, image_path TEXT, description TEXT)')
    elif desired == "create":
        cursor.execute('CREATE TABLE IF NOT EXISTS comics (rowid INTEGER PRIMARY KEY, image_path TEXT, description TEXT)')
    elif desired == "check":
        # check the comics in the table
        cursor.execute('SELECT * FROM comics')
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    elif desired == "exit":
        cursor.close()
        conn.close()
        exit()
    conn.commit()
    menu()
menu()