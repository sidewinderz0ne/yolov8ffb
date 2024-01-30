# import subprocess
# from pathlib import Path
# import os

# arr_ip = Path(os.getcwd() + '/array_ip.txt')

# def process_source(source_program, ip_address, additional_params):
#     command = ['python', source_program, '--mode', 'total', '--source', ip_address] + additional_params
#     try:
#         process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         stdout, stderr = process.communicate()
#         print(f"Command: {' '.join(command)}")
#         print(f"stdout:\n{stdout.decode()}")
#         print(f"stderr:\n{stderr.decode()}")
#         if process.returncode == 0:
#             print(f"{source_program} completed successfully for IP {ip_address}.")
#         else:
#             print(f"{source_program} failed with return code {process.returncode} for IP {ip_address}.")
#     except Exception as e:
#         print(f"Error running {source_program} for IP {ip_address}: {str(e)}")

# if __name__ == '__main__':
#     # Define the path to the source program
#     source_program = '9-track-master.py'

#     ip_addresses = []
#     if arr_ip.is_file():
#         with open(arr_ip, 'r') as file:
#             for line in file:
#                 ip_address = line.strip()
#                 ip_addresses.append(ip_address)
    
#     print(ip_addresses)

#     # Use a loop to run the source program for each IP address with additional parameters
#     for index, ip_address in enumerate(ip_addresses):
#         additional_params = []
#         if index == 0:
#             additional_params.append('--save_vid')
#             additional_params.append('True')    
#         elif index == 1:
#             additional_params.append('--debug')
#             additional_params.append('True')

#         process_source(source_program, ip_address, additional_params)


import subprocess
import cv2
import os
import argparse
import datetime
from datetime import datetime
from datetime import date
import json
from pathlib import Path
import math
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--tiket', type=str, default='123', help='model.pt path')
parser.add_argument('--mode', type=str, default='sampling', help='model.pt path')
opt = parser.parse_args()
no_tiket = opt.tiket
mode = opt.mode

current_date = datetime.now()
formatted_date = current_date.strftime('%Y-%m-%d')

file_directory = './hasil/' + formatted_date + '/' + no_tiket + '/'
path_avg_result_cctv = Path(os.getcwd() + '/hasil/' + formatted_date  + '/' + no_tiket + '/result_average_hasil_cctv.TXT')
if not path_avg_result_cctv.exists():
    path_avg_result_cctv.touch()

cctv_ip = '192.168.3.64'
cctv2_ip = '192.168.99.2'

program1_command = ['python', '9-track-master.py','--tiket', no_tiket, '--source', cctv_ip, '--mode', mode]
program2_command = ['python', '9-track-master.py','--tiket', no_tiket, '--source', cctv2_ip, '--mode', mode]

# file_path_cctv_2 = os.path.join(file_directory, 'video_' + cctv2_ip + '.mp4')
# file_path_cctv_3 = os.path.join(file_directory, 'video_' + cctv3_ip + '.mp4')


# processCctv2_command = ['python', '9-track-new-pov.py', '--mode', param1_value,'--cctv', cctv2_ip, '--tiket', no_tiket, '--source', file_path_cctv_2]
# processCctv3_command = ['python', '9-track-new-pov.py', '--mode', param1_value,'--cctv', cctv3_ip,  '--tiket', no_tiket, '--source', file_path_cctv_3]

try:
    mainCCTV = subprocess.Popen(program1_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cctv2 = subprocess.Popen(program2_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # cctv3 = subprocess.Popen(program3_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # inference semua cctv
    mainCCTV.wait()
    cctv2.wait()
    # cctv3.wait()
    # if mainCCTV.returncode != 0:
    #     print(f"Error in Program 1:\n{mainCCTV.stderr.read().decode('utf-8')}")
    
    
    # if cctv2.returncode != 0:
    #     print(f"Error in Program 2:\n{cctv2.stderr.read().decode('utf-8')}")

    
    # if cctv3.returncode != 0:
    #     print(f"Error in Program 3:\n{cctv3.stderr.read().decode('utf-8')}")
    
    # # olah semua hasil cctv
    # processCctv2 = subprocess.Popen(processCctv2_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # processCctv2.wait()

    # if processCctv2.returncode != 0:
    #     print(f"Error in Program 4:\n{processCctv2.stderr.read().decode('utf-8')}")

    # processCctv3 = subprocess.Popen(processCctv3_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # processCctv3.wait()

    # if processCctv3.returncode != 0:
    #     print(f"Error in Program 4:\n{processCctv3.stderr.read().decode('utf-8')}")    

    keys = ['unripe', 'ripe', 'overripe', 'empty_bunch', 'abnormal', 'long_stalk', 'kastrasi']

    def read_and_average(file_path, key):
        with open(file_path, 'r') as file:
            content = file.read()
            data = json.loads(content)
            return data.get(key, 0)

    def calculate_average_for_key(key):
        values_for_key = [
            read_and_average(os.path.join(file_directory, f'result_{cctv_ip}.TXT'), key)
            for cctv_ip in [cctv_ip, cctv2_ip]
        ]

        average_for_key = math.ceil(sum(values_for_key) / 3)

        return average_for_key


    averages = {key: calculate_average_for_key(key) for key in keys}

    with open(path_avg_result_cctv, 'w') as log_file:
        log_file.write(str(averages))

    # print("All programs have finished.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
    

print('all program has been running')






