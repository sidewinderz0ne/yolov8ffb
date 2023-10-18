import sqlite3
from urllib.request import urlopen
import json

url = "https://srs-ssms.com/grading_ai/get_list_mill.php"

arr = None
try:
    # store the response of URL
    response = urlopen(url)
    arr = json.loads(response.read())
except Exception as e:
    print("An error occurred while fetching the server data:", str(e))


mill = arr[0]['mill']

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

default_record = (1, mill, '192.168.1.254\\DBSTAGING', 'usertesting', 'Qwerty@123', 'skmstagingdb')

# Execute an INSERT query to add the default record
cursor.execute("INSERT INTO config (id, mill, server, user, password, database) VALUES (?, ?, ?, ?, ?, ?)", default_record)

# Commit the changes and close the connection
conn.commit()
conn.close()