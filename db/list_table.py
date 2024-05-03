import sqlite3

# Connect to the database
conn = sqlite3.connect('grading_sampling.db')
cursor = conn.cursor()

# List all tables in the database
cursor.execute("SELECT * FROM weight_bridge;")
tables = cursor.fetchall()

print("\nList of Tables:")
for table in tables:
    print(table)

# Close the connection
conn.close()
