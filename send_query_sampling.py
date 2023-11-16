import os
import asyncio
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path
import pytz
import json

tzInfo = pytz.timezone('Asia/Bangkok')
url = 'https://srs-ssms.com/post-py-sampling.php'
headers = {"content-type": "application/x-www-form-urlencoded",
          'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36'}
timer = 30
id_mill_dir = Path(os.getcwd() + '/config/id_mill.TXT')

id_mill = None
current_date = datetime.now(tz=tzInfo).strftime("%Y-%m-%d")
formatted_date = current_date
offline_log_dir = Path(os.getcwd() + '/hasil/' + formatted_date  + '/offline_log.TXT')


with open(id_mill_dir, 'r') as z:
    id_mill = z.readline()

def read_text_file(file_path, timestamp):
    if os.path.exists(file_path):
        with open(file_path, 'r') as z:
            content = z.readlines()
            try:
                if content and content[0].strip(): 
                    line = content[0].replace("'", "\"")
                    line_dict = json.loads(line)
                    new_key_value_pairs = {'id_mill': id_mill}

                    line_dict.update(new_key_value_pairs)

                    code = asyncio.get_event_loop().run_until_complete(post_count(line_dict))

                    if code == 99999 or len(content[0].strip()) == 0 or content[0] == '' or '\n' in content[0] or '\r\n' in content[0] or code == 200:
                        wr = open(file_path, "w")
                        for x in range(len(content)):
                            if x != 0:
                                wr.write(content[x])
                        wr.close()
                    print("Status: " + str(code) + " Payload: " + str(line_dict) + ".")
                else:
                    print("File is empty or does not have any value.")
            except Exception as e:
                print("Error:", str(e))

async def post_count(params):
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
        read_text_file(offline_log_dir,datetime.now(tz=tzInfo).strftime("%Y-%m-%d %H:%M:%S"))
        lastDate = datetime.now(tz=tzInfo) + timedelta(seconds=timer, minutes=0, hours=0)
