import os
import asyncio
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path
import pytz
import json
from urllib.request import urlopen

tzInfo = pytz.timezone('Asia/Bangkok')
# url = 'https://srs-ssms.com/post-py-sampling.php'
url = 'https://srs-ssms.com/grading_ai/post_updated_grading_machine.php'
headers = {"content-type": "application/x-www-form-urlencoded",
          'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36'}
timer = 0
id_mill_dir = Path(os.getcwd() + '/config/id_mill.TXT')
id_mill = 1

with open(id_mill_dir, 'r') as z:
    id_mill = z.readline()

def update_grading_machine(date):
    try:
        code = asyncio.get_event_loop().run_until_complete(post_count(date, id_mill))
        print("Status : " + str(code) + " " + date +".")
    except Exception as e:
        code = asyncio.get_event_loop().run_until_complete(post_count(date, id_mill))
        print("Errornya "+ str(e))
 
async def post_count(date,id_mill):
    try:
        async with aiohttp.ClientSession() as session:
            params = {'id_mill': str(id_mill),'timestamp': str(date)}
            async with session.post(url,data=params) as resp:
                response_text = await resp.text()
                print("PHP Response: " + response_text)
                response = resp.status
    except:
        response = 99999
    return response

lastDate = datetime.now(tz=tzInfo)+timedelta(seconds=0, minutes=5, hours=0)

while True:

    if datetime.now(tz=tzInfo) > lastDate:
        update_grading_machine(datetime.now(tz=tzInfo).strftime("%Y-%m-%d %H:%M:%S"))
        lastDate = datetime.now(tz=tzInfo) + timedelta(seconds=10, minutes=0, hours=0)


