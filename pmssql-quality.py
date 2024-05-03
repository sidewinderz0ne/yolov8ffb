import pymssql

conn = pymssql.connect(
    server='10.9.135.41\SCMSTAGING',
    user='userstaging',
    password='Qwerty@123',
    database='SCMSTAGINGDB',
    as_dict=True
)

SQL_QUERY = """
SELECT *
FROM MOPQuality_Staging;
"""

cursor = conn.cursor()
cursor.execute(SQL_QUERY)

records = cursor.fetchall()
for r in records:
    print(r)  # This will print all columns for each row

conn.close()  # Close the database connection when done
