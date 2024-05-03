import pymssql

server = '10.9.135.41\SCMSTAGING'
username = 'userstaging'
password = 'Qwerty@123'
database = 'SCMSTAGINGDB'

try:
    conn = pymssql.connect(
        server=server,
        user=username,
        password=password,
        database=database,
        as_dict=True
    )
    print("Connection successful!")

    SQL_QUERY = """
    SELECT *
    FROM MasterGrading_Staging;
    """

    cursor = conn.cursor()
    cursor.execute(SQL_QUERY)

    records = cursor.fetchall()
    for r in records:
        print(r)  # This will print all columns for each row

except pymssql.Error as e:
    print(f"Connection failed. Error: {e}")

finally:
    conn.close()  # Close the database connection when done