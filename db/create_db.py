import sqlite3
import os

database_file = 'grading_sampling.db'

if not os.path.exists(database_file):
    # Database file doesn't exist, so create it
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    # Continue with creating tables or performing other database operations here
    print(f"Database file '{database_file}' has been created.")
else:
    # Database file exists, so connect to it
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    print(f"Connected to database file '{database_file}'.")

# Close the connection when you're done
conn.close()
