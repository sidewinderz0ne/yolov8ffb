import sqlite3
from urllib.request import urlopen, Request
import json

def check_sqlite_connection(database_path):
    try:
        conn = sqlite3.connect(database_path)
        conn.close()
        print(f"Connected to SQLite database at {database_path}")
        return True
    except sqlite3.Error as e:
        print(f"SQLite connection error: {e}")
        return False

# URL for fetching data
url = "https://srs-ssms.com/grading_ai/get_list_mill.php"

try:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    request = Request(url, headers=headers)
    
    with urlopen(request) as response:
        arr = json.loads(response.read())
except Exception as e:
    print("An error occurred while fetching the server data:", str(e))
    exit(1)

mill = arr[0]['mill']

# Read the JSON data from the .txt file for database configuration
config_file_path = 'config_pks_ppro.txt'
try:
    with open(config_file_path, 'r') as file:
        json_data = file.read()
    config_data = json.loads(json_data)
except Exception as e:
    print(f"An error occurred while reading the configuration file: {e}")
    exit(1)

# Path to the SQLite database
sqlite_db_path = 'grading_sampling.db'

# Check SQLite connection
if not check_sqlite_connection(sqlite_db_path):
    print("Failed to connect to SQLite database. Exiting...")
    exit(1)

# Connect to the SQLite3 database
conn = sqlite3.connect(sqlite_db_path)
cursor = conn.cursor()

# Create a table in the SQLite3 database if it doesn't exist
create_table_query = '''CREATE TABLE IF NOT EXISTS config ( 
                    id INTEGER PRIMARY KEY,
                    mill TEXT,
                    server TEXT,
                    user TEXT,
                    password TEXT,
                    database TEXT
                )'''
cursor.execute(create_table_query)
conn.commit()

# Prepare the default record from the config file and fetched mill value
default_record = (
    1,
    mill,
    config_data['servername'],
    config_data['username'],
    config_data['password'],
    config_data['nama_database']
)

# Check if the default record already exists
cursor.execute("SELECT * FROM config WHERE id = ?", (1,))
existing_record = cursor.fetchone()

if existing_record:
    print("Default record already exists.")
else:
    # Insert the default record
    cursor.execute("INSERT INTO config (id, mill, server, user, password, database) VALUES (?, ?, ?, ?, ?, ?)", default_record)
    print("Default record inserted.")

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Operation complete.")
