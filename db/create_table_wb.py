import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('grading_sampling.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Create a table

#isi columnnya
create_table_query = '''CREATE TABLE IF NOT EXISTS weight_bridge ( 
                    id INTEGER PRIMARY KEY,
                    WBTicketNo TEXT,
                    VehiclePoliceNO TEXT,
                    DriverName TEXT,
                    BUnitCode INTEGER,
                    DivisionCode INTEGER,
                    Field INTEGER,
                    Bunches INTEGER,
                    Ownership TEXT, 
                    Ppro_push_time DATETIME,
                    AI_pull_time DATETIME,
                    FOREIGN KEY (BUnitCode) REFERENCES master_bunit(id)
                    FOREIGN KEY (DivisionCode) REFERENCES master_div(id)
                    FOREIGN KEY (Field) REFERENCES master_blok(id)
                )'''

if cursor.execute(create_table_query):
    print("Table created.")
else:
    print("Table already exists.")

# Commit the changes and close the connection
conn.commit()
conn.close()