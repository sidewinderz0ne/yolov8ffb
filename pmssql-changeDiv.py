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
UPDATE MasterDivisi_Staging
SET Ppro_DivisionName = 'test-bos', AI_pull_time = NULL
WHERE Ppro_DivisionCode = 708;
"""

# TRIGGER DEFAULT
SQL_UPDATE = """
UPDATE MasterDivisi_Staging
SET Ppro_DivisionName = 'CBI-RISK MNG HEAD OFFICE', AI_pull_time = NULL
WHERE Ppro_DivisionCode = 708;
"""

cursor = conn.cursor()
cursor.execute(SQL_UPDATE)

# Commit the changes to the database
conn.commit()

# Close the database connection when done
conn.close()