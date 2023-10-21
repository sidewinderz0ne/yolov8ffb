import sqlite3
import pymssql

# Connect to the SQLite3 database (grading_sampling.db)
sqlite_conn = sqlite3.connect('grading_sampling.db')
sqlite_cursor = sqlite_conn.cursor()

# Create tables in the SQLite3 database if they don't exist
create_master_blok_query = '''
CREATE TABLE IF NOT EXISTS master_blok (
    id INTEGER PRIMARY KEY,
    Ppro_DivisionCode INTEGER,
    Ppro_FieldName TEXT,
    Ppro_PlantingYear TEXT,
    Ppro_status TEXT,
    Ppro_push_time DATETIME,
    AI_pull_time DATETIME,
    FOREIGN KEY (Ppro_DivisionCode) REFERENCES master_div(id)
)
'''
sqlite_cursor.execute(create_master_blok_query)
sqlite_conn.commit()

# Connect to the SQL Server (pymssql) database
sql_server_conn = pymssql.connect(
    server='192.168.1.254\\DBSTAGING',
    user='usertesting',
    password='Qwerty@123',
    database='skmstagingdb',
    as_dict=True
)

# Query the data from the SQL Server (pymssql) database
sql_query = "SELECT * FROM MasterBlock_Staging;"
sql_cursor = sql_server_conn.cursor(as_dict=True)
sql_cursor.execute(sql_query)
sql_records = sql_cursor.fetchall()

# Insert the data into the SQLite3 database
for record in sql_records:
    insert_query = '''
    INSERT INTO master_blok (Ppro_DivisionCode, Ppro_FieldName, Ppro_PlantingYear, Ppro_status, Ppro_push_time, AI_pull_time)
    VALUES (?, ?, ?, ?, ?, ?)
    '''
    sqlite_cursor.execute(insert_query, (
        record['Ppro_DivisionCode'], record['Ppro_FieldName'], record['Ppro_PlantingYear'],
        record['Ppro_status'], record['Ppro_push_time'], record['AI_pull_time']
    ))

# Commit the changes in the SQLite3 database and close the connections
sqlite_conn.commit()
sqlite_conn.close()
sql_server_conn.close()
