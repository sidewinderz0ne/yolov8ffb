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
UPDATE MasterBlock_Staging
SET Ppro_FieldName = 'test-bos', AI_pull_time = NULL
WHERE Ppro_FieldCode = 5752;
"""

# Define the UPDATE query
SQL_UPDATE = """
UPDATE MasterBlock_Staging
SET Ppro_FieldName = 'TSA-NNE-19-P-U023', AI_pull_time = NULL
WHERE Ppro_FieldCode = 5752;
"""

cursor = conn.cursor()
cursor.execute(SQL_UPDATE)

# Commit the changes to the database
conn.commit()

# Close the database connection when done
conn.close()