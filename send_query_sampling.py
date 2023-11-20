import os
import asyncio
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path
import pytz
import json
from urllib.request import urlopen

tzInfo = pytz.timezone('Asia/Bangkok')
url = 'https://srs-ssms.com/post-py-sampling.php'
url_list_data = 'https://srs-ssms.com/pdf_grading/get_list_data_sampling.php'
headers = {"content-type": "application/x-www-form-urlencoded",
          'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36'}
timer = 10
id_mill_dir = Path(os.getcwd() + '/config/id_mill.TXT')

id_mill = None
current_date = datetime.now(tz=tzInfo).strftime("%Y-%m-%d")
formatted_date = current_date
offline_log_dir = Path(os.getcwd() + '/hasil/' + formatted_date  + '/offline_log.TXT')


with open(id_mill_dir, 'r') as z:
    id_mill = z.readline()

arr = []

async def fetch_server_data():
    try:
        # store the response of URL
        response = urlopen(url_list_data)
        return json.loads(response.read())
    except Exception as e:
        print("An error occurred while fetching the server data:", str(e))
        return None

async def update_arr_variable():
    global arr
    new_data = await fetch_server_data()
    if new_data:
        arr = new_data

def compare_dicts(dict1, dict2, key_mapping):
    for key1, key2 in key_mapping.items():
        value1 = dict1.get(key1)
        value2 = dict2.get(key2)

        
        if key1 in {'unripe', 'ripe', 'overripe', 'empty_bunch','abnormal','kastrasi','tp'} and key2 in {'unripe', 'ripe', 'overripe', 'empty_bunch','abnormal','kastrasi','long_stalk'}:
            value1 = int(value1) if isinstance(value1, str) and value1.isdigit() else value1
            value2 = int(value2) if isinstance(value2, str) and value2.isdigit() else value2
        elif key1 in {'unripe', 'ripe', 'overripe', 'empty_bunch','abnormal','kastrasi','tp'} and key2 in {'unripe', 'ripe', 'overripe', 'empty_bunch','abnormal','kastrasi','long_stalk'} and isinstance(value1, str) and isinstance(value2, str) and value1.isdigit() and value2.isdigit():
            value1 = int(value1)
            value2 = int(value2)

        if value1 != value2:
            return False

    return True

def read_text_file(file_path, timestamp):
    if os.path.exists(file_path):
        with open(file_path, 'r') as z:
            content = z.readlines()

            ready_lines = [line for line in content if "'status_inference': 'READY'" in line]
            
            for line in ready_lines:
                try:
                    if line.strip():
                        line = line.replace("'", "\"")
                        line_dict = json.loads(line)

                        
                        key_mapping = {'no_tiket': 'no_tiket', 'no_plat': 'no_plat', 'nama_driver': 'nama_driver', 'bisnis_unit': 'bunit', 'divisi':'divisi','blok':'blok','status':'ownership','unripe':'unripe','ripe':'ripe','overripe':'overripe','empty_bunch':'empty_bunch','abnormal':'abnormal','kastrasi':'kastrasi','tp':'long_stalk','waktu_mulai':'waktu_mulai','waktu_selesai':'waktu_selesai'}
                        matching_data = [data for data in arr if compare_dicts(data, line_dict, key_mapping)]

                        if not matching_data:
                            new_key_value_pairs = {'id_mill': id_mill}
                            line_dict.update(new_key_value_pairs)
                            code = asyncio.get_event_loop().run_until_complete(post_count(line_dict))
                        else:
                            print('Match found. Skipping posting.')
                        # for key in arr_key:
                        #     if key in arr and key in line_dict_key and key in line_dict and arr[key] == line_dict[key]:
                        #         common_pairs[key] = line_dict[key]

                        # if common_pairs:
                        #     print("Common key-value pairs:", line_dict)
                        # else:
                        #     print("No common key-value pairs.", line_dict)

                        

                        # Continue with the rest of your code
                        

                        # if code == 99999 or len(line.strip()) == 0 or line == '' or '\n' in line or '\r\n' in line or code == 200:
                        #     wr = open(file_path, "w")
                        #     for x in range(len(content)):
                        #         if x != 0:
                        #             wr.write(content[x])
                        #     wr.close()
                        # print("Status: " + str(code))
                    else:
                        print("Line is empty or does not have any value.")
                except Exception as e:
                    print("Error:", str(e))

async def post_count(params):
    print('sudah di store gan')
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url,data=params) as resp:
                response = resp.status
    except:
        response = 99999
    return response

lastDate = datetime.now(tz=tzInfo)+timedelta(seconds=timer, minutes=0, hours=0)


while True:
    
    if datetime.now(tz=tzInfo) > lastDate:
        if arr == []:
            asyncio.get_event_loop().run_until_complete(update_arr_variable())
        
        read_text_file(offline_log_dir,datetime.now(tz=tzInfo).strftime("%Y-%m-%d %H:%M:%S"))
        asyncio.get_event_loop().run_until_complete(update_arr_variable())
        lastDate = datetime.now(tz=tzInfo) + timedelta(seconds=timer, minutes=0, hours=0)


