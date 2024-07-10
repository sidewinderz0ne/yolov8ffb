import sqlite3
import pymssql
import json

def read_config(config_file_path):
    try:
        with open(config_file_path, 'r') as file:
            json_data = file.read()
        config_data = json.loads(json_data)
        return config_data
    except Exception as e:
        print(f"An error occurred while reading the configuration file: {e}")
        exit(1)

# Read the JSON data from the .txt file for database configuration
config_file_path = 'config_pks_ppro.txt'
config_data = read_config(config_file_path)

# Connect to the SQLite3 database (grading_sampling.db)
sqlite_db_path = 'grading_sampling.db'

try:
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_cursor = sqlite_conn.cursor()
    print(f"Connected to SQLite database at {sqlite_db_path}")
except sqlite3.Error as e:
    print(f"SQLite connection error: {e}")
    exit(1)

# Create tables in the SQLite3 database if they don't exist
create_master_div_query = '''
CREATE TABLE IF NOT EXISTS master_div (
    id INTEGER PRIMARY KEY,
    Ppro_BUnitCode INTEGER,
    Ppro_DivisionName TEXT,
    Ppro_push_time DATETIME,
    AI_pull_time DATETIME,
    FOREIGN KEY (Ppro_BUnitCode) REFERENCES master_bunit(id)
)
'''
sqlite_cursor.execute(create_master_div_query)
sqlite_conn.commit()

# Connect to the SQL Server (pymssql) database
try:
    sql_server_conn = pymssql.connect(
        server=config_data['servername'],
        user=config_data['username'],
        password=config_data['password'],
        database=config_data['nama_database'],
        as_dict=True
    )
    print(f"Connected to SQL Server at {config_data['Servername']}")
except pymssql.Error as e:
    print(f"SQL Server connection error: {e}")
    exit(1)

# Query the data from the SQL Server (pymssql) database
sql_query = "SELECT * FROM MasterDivisi_Staging;"
sql_cursor = sql_server_conn.cursor(as_dict=True)
sql_cursor.execute(sql_query)
sql_records = sql_cursor.fetchall()

# Insert the data into the SQLite3 database
for record in sql_records:
    insert_query = '''
    INSERT INTO master_div (Ppro_BUnitCode, Ppro_DivisionName, Ppro_push_time, AI_pull_time)
    VALUES (?, ?, ?, ?)
    '''
    sqlite_cursor.execute(insert_query, (
        record['Ppro_BUnitCode'], record['Ppro_DivisionName'], record['Ppro_push_time'], record['AI_pull_time']
    ))

# Commit the changes in the SQLite3 database and close the connections
sqlite_conn.commit()
sqlite_conn.close()
sql_server_conn.close()

print("Operation complete.")
