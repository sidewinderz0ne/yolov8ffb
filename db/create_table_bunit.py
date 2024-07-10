import sqlite3
import pymssql
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

def check_sql_server_connection(server, user, password, database):
    try:
        conn = pymssql.connect(
            server=server,
            user=user,
            password=password,
            database=database
        )
        conn.close()
        print(f"Connected to SQL Server at {server}")
        return True
    except pymssql.Error as e:
        print(f"SQL Server connection error: {e}")
        return False

# Read the JSON data from the .txt file
with open('config_pks_ppro.txt', 'r') as file:
    json_data = file.read()

# Convert the JSON data back to a Python dictionary
data = json.loads(json_data)

# Check SQLite connection
sqlite_db_path = 'grading_sampling.db'
if not check_sqlite_connection(sqlite_db_path):
    print("Failed to connect to SQLite database. Exiting...")
    exit(1)

# Check SQL Server connection
if not check_sql_server_connection(
    server=data['Servername'],
    user=data['Username'],
    password=data['Password'],
    database=data['Nama_Database']
):
    print("Failed to connect to SQL Server database. Exiting...")
    exit(1)

# Connect to the SQLite3 database (grading_sampling.db)
sqlite_conn = sqlite3.connect(sqlite_db_path)
sqlite_cursor = sqlite_conn.cursor()

# Create a table in the SQLite3 database if it doesn't exist
create_table_query = '''
CREATE TABLE IF NOT EXISTS master_bunit (
    id INTEGER PRIMARY KEY,
    Ppro_BUnitName TEXT,
    Ppro_push_time DATETIME,
    AI_pull_time DATETIME
)
'''
sqlite_cursor.execute(create_table_query)
sqlite_conn.commit()

# Connect to the SQL Server (pymssql) database
sql_server_conn = pymssql.connect(
    server=data['servername'],
    user=data['username'],
    password=data['password'],
    database=data['nama_database'],
    as_dict=True
)

# Query the data from the SQL Server (pymssql) database
sql_query = "SELECT * FROM MasterBunit_staging;"
sql_cursor = sql_server_conn.cursor(as_dict=True)
sql_cursor.execute(sql_query)
sql_records = sql_cursor.fetchall()

# Insert the data into the SQLite3 database
for record in sql_records:
    insert_query = '''
    INSERT INTO master_bunit (Ppro_BUnitName, Ppro_push_time, AI_pull_time)
    VALUES (?, ?, ?)
    '''
    sqlite_cursor.execute(insert_query, (
        record['Ppro_BUnitName'], record['Ppro_push_time'], record['AI_pull_time']
    ))

# Commit the changes in the SQLite3 database and close the connections
sqlite_conn.commit()
sqlite_conn.close()
sql_server_conn.close()

print("Data transfer complete.")
