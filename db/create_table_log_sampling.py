import sqlite3
import pymssql

# Connect to the SQLite3 database (grading_sampling.db)
sqlite_conn = sqlite3.connect('grading_sampling.db')
sqlite_cursor = sqlite_conn.cursor()

# Create a table in the SQLite3 database if it doesn't exist
create_table_query = '''
CREATE TABLE IF NOT EXISTS log_sampling (
    id INTEGER PRIMARY KEY,
    mill_id TEXT,
    waktu_mulai DATETIME,
    waktu_selesai DATETIME,
    no_tiket TEXT,
    no_plat TEXT,
    nama_driver TEXT,
    bisnis_unit TEXT,
    divisi TEXT,
    blok TEXT,
    status TEXT,
    unripe TEXT,
    ripe TEXT,
    overripe TEXT,
    empty_bunch TEXT,
    abnormal TEXT,
    kastrasi TEXT,
    tp TEXT
)
'''

sqlite_cursor.execute(create_table_query)
sqlite_conn.commit()
