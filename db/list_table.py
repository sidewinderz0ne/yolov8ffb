import sqlite3

# Connect to the database
conn = sqlite3.connect('grading_sampling.db')
cursor = conn.cursor()

# List all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("\nList of Tables:")
for table in tables:
    print(table[0])

# Close the connection
conn.close()
