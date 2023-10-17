import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('grading_sampling.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Create a table

#isi columnnya
create_table_query = '''CREATE TABLE IF NOT EXISTS config ( 
                    id INTEGER PRIMARY KEY,
                    mill TEXT,
                    server TEXT,
                    user TEXT,
                    password TEXT,
                    database TEXT
                )'''

if cursor.execute(create_table_query):
    print("Table created.")
else:
    print("Table already exists.")

# Commit the changes and close the connection
conn.commit()
conn.close()