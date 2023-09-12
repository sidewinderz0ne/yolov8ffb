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
UPDATE MasterBunit_staging
SET Ppro_BUnitName = 'test-bos', AI_pull_time = NULL
WHERE Ppro_BUnitCode = 53;
"""

# Define the UPDATE query
SQL_UPDATE = """
UPDATE MasterBunit_staging
SET Ppro_BUnitName = 'HEAD OFFICE - CBI', AI_pull_time = NULL
WHERE Ppro_BUnitCode = 53;
"""

cursor = conn.cursor()
cursor.execute(SQL_UPDATE)

# Commit the changes to the database
conn.commit()

# Close the database connection when done
conn.close()