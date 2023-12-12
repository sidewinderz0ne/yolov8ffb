import pymssql

conn = pymssql.connect(
    server='10.9.135.41\SCMSTAGING',
    user='userstaging',
    password='Qwerty@123',
    database='SCMSTAGINGDB',
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