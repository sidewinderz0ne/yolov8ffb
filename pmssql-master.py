import pymssql

conn = pymssql.connect(
    server='192.168.1.254\DBSTAGING',
    user='usertesting',
    password='Qwerty@123',
    database='skmstagingdb',
    as_dict=True
)

SQL_QUERY = """
SELECT *
FROM MasterGrading_Staging;
"""

cursor = conn.cursor()
cursor.execute(SQL_QUERY)

records = cursor.fetchall()
for r in records:
    print(r)  # This will print all columns for each row

conn.close()  # Close the database connection when done
