import sqlite3
from urllib.request import urlopen, Request
import json

url = "https://srs-ssms.com/grading_ai/get_list_mill.php"

try:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    request = Request(url, headers=headers)
    
    with urlopen(request) as response:
        arr = json.loads(response.read())

except Exception as e:
    print("An error occurred while fetching the server data:", str(e))


mill = arr[0]['mill']
ip = arr[0]['ip']

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('grading_sampling.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Create a table

#isi columnnya
create_table_query = '''CREATE TABLE IF NOT EXISTS cctv ( 
                    id INTEGER PRIMARY KEY,
                    mill TEXT,
                    ip TEXT,
                    nama_cctv TEXT
                )'''

if cursor.execute(create_table_query):
    print("Table created.")
else:
    print("Table already exists.")

default_record = (1, mill, ip, '')

# Execute an INSERT query to add the default record
cursor.execute("INSERT INTO cctv (id, mill, ip, nama_cctv) VALUES (?, ?, ?, ?)", default_record)

# Commit the changes and close the connection
conn.commit()
conn.close()