import sqlite3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--table', type=str, default='')
parser.add_argument('--all', action='store_true', default=False)  # Use 'store_true' for boolean flags
opt = parser.parse_args()
table = opt.table
all_tables = opt.all  # Rename the variable to avoid shadowing 'all'

# Connect to the database
conn = sqlite3.connect('grading_sampling.db')
cursor = conn.cursor()

if all_tables:
    # Delete all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    for table_info in tables:
        table_name = table_info[0]
        cursor.execute(f"DROP TABLE {table_name}")
        print(f"Table '{table_name}' has been deleted.")

else:
    # Delete the specified table
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
    table_exists = cursor.fetchone()

    if table_exists:
        # Table exists; delete it
        cursor.execute(f"DROP TABLE {table}")
        print(f"Table '{table}' has been deleted.")
    else:
        # Table does not exist
        print(f"Table '{table}' does not exist.")

# Commit the changes and close the connection
conn.commit()
conn.close()
