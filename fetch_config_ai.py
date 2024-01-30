import os
import asyncio
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path
import pytz
import json
from urllib.request import urlopen
import sqlite3
import requests
from urllib.request import urlopen
tzInfo = pytz.timezone('Asia/Bangkok')

url = 'https://srs-ssms.com/grading_ai/get_config_ai.php'
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
    'Referer': 'https://srs-ssms.com/',  # Add a Referer header if needed
}

timer = 0
id_mill_dir = Path(os.getcwd() + '/config/id_mill.TXT')

id_mill = None
current_date = datetime.now(tz=tzInfo).strftime("%Y-%m-%d")
formatted_date = current_date
offline_log_dir = Path(os.getcwd() + '/hasil/' + formatted_date  + '/offline_log.TXT')


with open(id_mill_dir, 'r') as z:
    id_mill = z.readline()

data = {'id_mill': id_mill}

try:
    requests.get('https://www.google.com', timeout=5)
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        try:
            result = json.loads(response.text)
            config_ai_dir = Path(os.getcwd() + '/config/config_ai.txt')
            with open(config_ai_dir, 'w') as config_file:
                json.dump(result[0], config_file)
            
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            default_data = {"conf": "0.3", "iou": "0.3", "roi": "0.3", "id_mill": "1"}
            with open(config_ai_dir, 'w') as config_file:
                json.dump(default_data, config_file)
            
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        
        config_ai_dir = Path(os.getcwd() + '/config/config_ai.txt')
        default_data = {"conf": "0.3", "iou": "0.3", "roi": "0.3", "id_mill": "1"}
        with open(config_ai_dir, 'w') as config_file:
            json.dump(default_data, config_file)

except requests.ConnectionError:
    
    config_ai_dir = Path(os.getcwd() + '/config/config_ai.txt')
    default_data = {"conf": "0.3", "iou": "0.3", "roi": "0.3", "id_mill": "1"}
    with open(config_ai_dir, 'w') as config_file:
        json.dump(default_data, config_file)

except Exception as e:
    print(f"An unexpected error occurred: {e}")