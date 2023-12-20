import os
import aiohttp
import asyncio
from datetime import datetime, timedelta
import pytz
from pathlib import Path

tzInfo = pytz.timezone('Asia/Bangkok')
url = 'https://srs-ssms.com/post-py-total.php'
headers = {
    "content-type": "application/x-www-form-urlencoded",
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36'
}
timer = 20
log_dir = Path(os.getcwd() + '/hasil/grading_total_log.TXT')
id_mill_dir = Path(os.getcwd() + '/config/id_mill.TXT')

with open(id_mill_dir, 'r') as z:
    id_mill = z.readline()

async def read_and_send_lines(file_path):
    try:
        if os.path.exists(file_path):
            async with aiohttp.ClientSession() as session:
                with open(file_path, 'r+') as file:
                    lines = file.readlines()

                    if not lines:
                        print("No data in the file. Skipping sending.")
                        return

                    lines_to_send = lines[:25]
                    lines_left = lines[25:]

                tasks = [post_count(line.strip()) for line in lines_to_send]
                results = await asyncio.gather(*tasks)

                # Update the file content based on successful responses
                with open(file_path, 'w') as file:
                    for line, success in zip(lines_to_send, results):
                        if success:
                            print("Successfully processed line:", line.strip())
                        else:
                            print("Failed to process line:", line.strip())
                            file.write(line)  # Write back the line if processing failed

                    file.writelines(lines_left)
    except Exception as e:
        print("Error:", str(e))

async def post_count(params):
    try:
        paramArr = params.split(";")
        async with aiohttp.ClientSession() as session:
            param = {'unripe': paramArr[0], 'ripe': paramArr[1], 'overripe': paramArr[2],
                     'empty_bunch': paramArr[3], 'abnormal': paramArr[4], 'tangkai_panjang': paramArr[5],
                     'kastrasi': paramArr[6], 'timestamp': paramArr[7], 'id_mill': str(id_mill)}

            for attempt in range(3):
                async with session.post(url, data=param) as resp:
                    response = resp.status
                    print(response)
                    response_text = await resp.text()
                    print("Response Text: ", response_text)

                    if response == 200:
                        return True  # Indicate success
                    else:
                        print(f"Retry attempt {attempt + 1} due to non-200 response")
                        await asyncio.sleep(1)

    except Exception as e:
        print("Error:", str(e))
    return False  # Indicate failure

async def main():
    lastDate = datetime.now(tz=tzInfo) + timedelta(seconds=timer, minutes=0, hours=0)

    while True:
        if datetime.now(tz=tzInfo) > lastDate:
            await read_and_send_lines(log_dir)
            lastDate = datetime.now(tz=tzInfo) + timedelta(seconds=timer, minutes=0, hours=0)
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
