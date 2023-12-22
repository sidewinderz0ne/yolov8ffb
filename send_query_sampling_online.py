import os
import asyncio
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path
import pytz
import json
from urllib.request import urlopen
import sqlite3
tzInfo = pytz.timezone('Asia/Bangkok')
url = 'https://srs-ssms.com/post-py-sampling.php'
url_list_data = 'https://srs-ssms.com/pdf_grading/get_list_data_sampling.php'
headers = {"content-type": "application/x-www-form-urlencoded",
          'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36'}
timer = 0
id_mill_dir = Path(os.getcwd() + '/config/id_mill.TXT')

id_mill = None
current_date = datetime.now(tz=tzInfo).strftime("%Y-%m-%d")
formatted_date = current_date
offline_log_dir = Path(os.getcwd() + '/hasil/' + formatted_date  + '/offline_log.TXT')


with open(id_mill_dir, 'r') as z:
    id_mill = z.readline()

arr = []
response = urlopen(url_list_data)
test =  json.loads(response.read())


database_file = './hasil/' + str(formatted_date) + '/log_' + str(formatted_date)+  '.db'

if not os.path.exists(database_file):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    cursor.execute('''
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
    ''')

    conn.commit()
    
    print(f"Database file '{database_file}' and table 'log_sampling' have been created.")
else:
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
  

async def fetch_server_data(url):
    try:
        response = urlopen(url_list_data)
        return json.loads(response.read())
    except Exception as e:
        print("An error occurred while fetching the server data:", str(e))
        return None
            
async def run_comparison():

    server_data = await fetch_server_data(url_list_data)
    if server_data is None:
        return

    # Fetch data from the local database
    cursor.execute("SELECT * FROM log_sampling;")
    local_data = cursor.fetchall()

    local_data_dict_list = []
    for local_row in local_data:
        local_row_dict = {}
        for column_index, column_value in enumerate(local_row):
            column_name = cursor.description[column_index][0]
            
            if column_name == 'blok':
                column_value = column_value.replace('\n', ',').replace(' ', ',')

            column_value = None if column_value == '' else column_value

            local_row_dict[column_name] = column_value

        local_data_dict_list.append(local_row_dict)
    tasks = []

    arr_server_data = []
    for server_record in server_data:
        server_mill = server_record['mill_id']
        server_waktu_mulai = server_record['waktu_mulai']
        server_waktu_selesai = server_record['waktu_selesai']
        server_no_tiket = server_record['no_tiket']
        server_no_plat = server_record['no_plat']
        server_nama_driver = server_record['nama_driver']
        server_bisnis_unit = server_record['bisnis_unit']
        server_divisi = server_record['divisi']
        server_blok = server_record['blok']
        server_status = server_record['status']

        arr_server_data.append(server_no_tiket)
    
    for local_record in local_data_dict_list:
            local_blok = local_record.get('no_tiket')

            is_blok_present = any(local_blok in record for record in arr_server_data)

            if is_blok_present:
                print(f"{local_blok} is present in server_record.")
            else:
                tasks.append(post_count(local_record))

    await asyncio.gather(*tasks)

async def post_count(params):
   
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url,data=params) as resp:
                    response = resp.status
                    print(response)
                    response_text = await resp.text()
                    print("Response Text: ", response_text)
    except:
        response = 99999
    return response


async def main():
    lastDate = datetime.now(tz=tzInfo) + timedelta(seconds=timer, minutes=0, hours=0)
    while True:
        if datetime.now(tz=tzInfo) > lastDate:
            await run_comparison()
            lastDate = datetime.now(tz=tzInfo) + timedelta(seconds=7, minutes=0, hours=0)
        await asyncio.sleep(1)


if __name__ == "__main__":
    
    asyncio.run(main())