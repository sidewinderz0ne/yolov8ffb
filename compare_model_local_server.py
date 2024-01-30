import hashlib
import requests
import time
import os
from urllib.request import urlopen, URLError

def is_connected():
    try:
        urlopen('https://www.google.com', timeout=1)
        return True
    except URLError:
        return False

def calculate_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            md5.update(byte_block)
    return md5.hexdigest()

def download_and_compare_checksum(file_url, local_file_path):
    # Check if the directory exists, and create it if not
    directory_path = os.path.dirname(local_file_path)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Created directory: {directory_path}")

    # Check if the local file exists
    if os.path.exists(local_file_path):
        local_checksum = calculate_md5(local_file_path)
        print("Local Checksum:", local_checksum)

        response = requests.get(file_url, headers=headers)
        if response.status_code == 200:
            
            server_checksum = response.text.strip()
            print("Server Checksum:", server_checksum)

            if local_checksum == server_checksum:
                print("Checksums match. The files are identical.")
            else:
                print("Checksums do not match. Downloading the file.")

                download_link = 'https://srs-ssms.com/grading_ai/model/download_model.php'
                download_response = requests.get(download_link, headers=headers)

                if download_response.status_code == 200:
                    with open(local_file_path, 'wb') as file:
                        file.write(download_response.content)
                    print(f"Download successful. File saved to: {local_file_path}")
                else:
                    print(f"Failed to download file. Status code: {download_response.status_code}")

        else:
            print(f"Request failed with status code: {response.status_code}")

    else:
        print("Local file does not exist. Downloading the file.")

        # Download the file using requests
        download_link = 'https://srs-ssms.com/grading_ai/model/download_model.php'
        download_response = requests.get(download_link, headers=headers)

        if download_response.status_code == 200:
            # Save the downloaded file to the specified directory
            with open(local_file_path, 'wb') as file:
                file.write(download_response.content)
            print(f"Download successful. File saved to: {local_file_path}")
        else:
            print(f"Failed to download file. Status code: {download_response.status_code}")

username = os.path.basename(os.path.expanduser("~"))

local_file_path = f'/home/{username}/weights/model.pt'
server_file_url = 'https://srs-ssms.com/grading_ai/model/version_model.php'

# Define user agent header
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/98.0'
}

try:
    if is_connected():
        download_and_compare_checksum(server_file_url, local_file_path)
except Exception as e:
    print(f"An error occurred: {e}")