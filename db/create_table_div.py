import sqlite3
import pymssql

# Connect to the SQLite3 database (grading_sampling.db)
sqlite_conn = sqlite3.connect('grading_sampling.db')
sqlite_cursor = sqlite_conn.cursor()

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
sql_server_conn = pymssql.connect(
    server='192.168.1.254\\DBSTAGING',
    user='usertesting',
    password='Qwerty@123',
    database='skmstagingdb',
    as_dict=True
)

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
