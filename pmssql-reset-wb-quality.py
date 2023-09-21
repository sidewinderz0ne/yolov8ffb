import pymssql

conn = pymssql.connect(
    server='192.168.1.254\DBSTAGING',
    user='usertesting',
    password='Qwerty@123',
    database='skmstagingdb',
    as_dict=True
)

# Define the UPDATE query
SQL_UPDATE = """
UPDATE MOPweighbridgeTicket_Staging
SET AI_pull_time = NULL;
"""

# Define the UPDATE query
SQL_DELETE = """
DELETE MOPQuality_Staging;
"""

cursor = conn.cursor()
cursor.execute(SQL_UPDATE)

# Commit the changes to the database
conn.commit()

cursor.execute(SQL_DELETE)

# Commit the changes to the database
conn.commit()

# Close the database connection when done
conn.close()