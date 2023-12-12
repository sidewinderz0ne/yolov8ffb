import sqlite3
import pymssql

# Connect to the SQLite3 database (grading_sampling.db)
sqlite_conn = sqlite3.connect('grading_sampling.db')
sqlite_cursor = sqlite_conn.cursor()

# Create tables in the SQLite3 database if they don't exist
create_weight_bridge_query = '''
CREATE TABLE IF NOT EXISTS weight_bridge (
    id INTEGER PRIMARY KEY,
    WBTicketNo TEXT,
    VehiclePoliceNO TEXT,
    DriverName TEXT,
    BUnitCode INTEGER,
    DivisionCode INTEGER,
    Field INTEGER,
    Bunches INTEGER,
    Ownership TEXT,
    Ppro_push_time DATETIME,
    AI_pull_time DATETIME,
    FOREIGN KEY (BUnitCode) REFERENCES master_bunit(id),
    FOREIGN KEY (DivisionCode) REFERENCES master_div(id),
    FOREIGN KEY (Field) REFERENCES master_blok(id)
)
'''
sqlite_cursor.execute(create_weight_bridge_query)
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
sql_query = "SELECT * FROM MOPweighbridgeTicket_Staging;"
sql_cursor = sql_server_conn.cursor(as_dict=True)
sql_cursor.execute(sql_query)
sql_records = sql_cursor.fetchall()


# print(sql_records)
# Insert the data into the SQLite3 database
for record in sql_records:
    insert_query = '''
    INSERT INTO weight_bridge (WBTicketNo, VehiclePoliceNO, DriverName, BUnitCode, DivisionCode, Field, Bunches, Ownership, Ppro_push_time, AI_pull_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    sqlite_cursor.execute(insert_query, (
        record['WBTicketNo'], record['VehiclePoliceNO'], record['DriverName'], record['BUnitCode'],
        record['DivisionCode'], record['Field'], record['Bunches'], record['Ownership'],
        record['push_time'], record['pull_time']
    ))

# Commit the changes in the SQLite3 database and close the connections
sqlite_conn.commit()
sqlite_conn.close()
sql_server_conn.close()
