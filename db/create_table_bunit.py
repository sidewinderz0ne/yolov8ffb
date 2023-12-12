import sqlite3
import pymssql

# Connect to the SQLite3 database (grading_sampling.db)
sqlite_conn = sqlite3.connect('grading_sampling.db')
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
    server='10.9.135.41\SCMSTAGING',
    user='userstaging',
    password='Qwerty@123',
    database='SCMSTAGINGDB',
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
