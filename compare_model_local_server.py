import hashlib
from pathlib import Path
import requests
import time
import pytz
import os
from datetime import datetime, timedelta
import json
from urllib.request import urlopen, URLError
tzInfo = pytz.timezone('Asia/Bangkok')

def is_connected():
    try:
        urlopen('https://www.google.com', timeout=1)
        return True
    except URLError:
        return False

# def calculate_md5(file_path):
#     md5 = hashlib.md5()
#     with open(file_path, 'rb') as file:
#         for byte_block in iter(lambda: file.read(4096), b""):
#             md5.update(byte_block)
#     return md5.hexdigest()
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
    'Referer': 'https://srs-ssms.com/',  # Add a Referer header if needed
}
    
def fetch_server_config():
    url = 'https://srs-ssms.com/grading_ai/get_config_ai.php'
    
    id_mill_dir = Path(os.getcwd() + '/config/id_mill.TXT')

    id_mill = None
    current_date = datetime.now(tz=tzInfo).strftime("%Y-%m-%d")
    formatted_date = current_date
    offline_log_dir = Path(os.getcwd() + '/hasil/' + formatted_date  + '/offline_log.TXT')

    with open(id_mill_dir, 'r') as z:
        id_mill = z.readline()

    data = {'id_mill': id_mill}
    
    requests.get('https://www.google.com', timeout=5)
    response = requests.post(url, headers=headers, data=data)

    result = ''
    if response.status_code == 200:
        try:
            result = json.loads(response.text)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")

    return result

def download_and_compare_version(local_file_path):
    file_contents = local_file_path.read_text()

    server_result = fetch_server_config()
    local_dict = json.loads(file_contents)
    server_dict = server_result[0]

    if local_dict['version'] !=  server_dict['version']:
        updated_local_json = json.dumps(server_dict, indent=2)
        local_file_path.write_text(updated_local_json)

        model_path = Path(os.getcwd()) / 'model'
        download_link = 'https://srs-ssms.com/grading_ai/model/download_model.php'
        download_params = {'name_file': server_dict['model']}
        output_file_path = model_path / download_params['name_file']

        model_path.mkdir(parents=True, exist_ok=True)

        response = requests.post(download_link, data=download_params, headers=headers)

        if response.status_code == 200:
            # Save the downloaded content to the specified file path
            with open(output_file_path, 'wb') as output_file:
                output_file.write(response.content)
            print(f"File downloaded and saved to {output_file_path}")

            ready_to_download_sign_file = Path(os.getcwd()) / 'config' / 'ready_to_download_sign.txt'
            ready_to_download_sign_file.touch()
            print(f"New file 'ready_to_download_sign.txt' created in /config/")
        else:
            print(f"Failed to download the file. Status code: {response.status_code}")

        return 1
    else:
        return 0

#     # Check if the directory exists, and create it if not
#     directory_path = os.path.dirname(local_file_path)
#     if not os.path.exists(directory_path):
#         os.makedirs(directory_path)
#         print(f"Created directory: {directory_path}")

#     # Check if the local file exists
#     if os.path.exists(local_file_path):
#         local_checksum = calculate_md5(local_file_path)
#         print("Local Checksum:", local_checksum)

#         response = requests.get(file_url, headers=headers)
#         if response.status_code == 200:
            
#             server_checksum = response.text.strip()
#             print("Server Checksum:", server_checksum)

#             if local_checksum == server_checksum:
#                 print("Checksums match. The files are identical.")
#             else:
#                 print("Checksums do not match. Downloading the file.")

#                 download_link = 'https://srs-ssms.com/grading_ai/model/download_model.php'
#                 download_response = requests.get(download_link, headers=headers)

#                 if download_response.status_code == 200:
#                     with open(local_file_path, 'wb') as file:
#                         file.write(download_response.content)
#                     print(f"Download successful. File saved to: {local_file_path}")
#                 else:
#                     print(f"Failed to download file. Status code: {download_response.status_code}")

#         else:
#             print(f"Request failed with status code: {response.status_code}")

#     else:
#         print("Local file does not exist. Downloading the file.")

#         # Download the file using requests
#         download_link = 'https://srs-ssms.com/grading_ai/model/download_model.php'
#         download_response = requests.get(download_link, headers=headers)

#         if download_response.status_code == 200:
#             # Save the downloaded file to the specified directory
#             with open(local_file_path, 'wb') as file:
#                 file.write(download_response.content)
#             print(f"Download successful. File saved to: {local_file_path}")
#         else:
#             print(f"Failed to download file. Status code: {download_response.status_code}")

# username = os.path.basename(os.path.expanduser("~"))

local_file_path = Path(os.getcwd() + '/config/config_ai.txt')
# server_file_url = 'https://srs-ssms.com/grading_ai/model/version_model.php'
local_file_path.parent.mkdir(parents=True, exist_ok=True)

default_config = {"conf": "", "iou": "", "roi": "", "id_mill": "", "model": "", "version": ""}
if not local_file_path.exists():
    local_file_path.write_text(json.dumps(default_config, indent=2))

try:
    if is_connected():
        result = download_and_compare_version(local_file_path)
        print(result)
except Exception as e:
    print(f"An error occurred: {e}")



# import os
# from pathlib import Path
# import requests

# # Set up the paths and parameters
# test_path = Path(os.getcwd()) / 'config'
# download_link = 'https://srs-ssms.com/grading_ai/model/download_model.php'
# download_params = {'name_file': 'best_yolov8n_nbm'}
# output_file_path = test_path / download_params['name_file']

# # Create the directory if it doesn't exist
# test_path.mkdir(parents=True, exist_ok=True)

# # Make the POST request and download the file
# response = requests.post(download_link, data=download_params, headers=headers)

# # Check if the request was successful (status code 200)
# if response.status_code == 200:
#     # Save the downloaded content to the specified file path
#     with open(output_file_path, 'wb') as output_file:
#         output_file.write(response.content)
#     print(f"File downloaded and saved to {output_file_path}")
# else:
#     print(f"Failed to download the file. Status code: {response.status_code}")
