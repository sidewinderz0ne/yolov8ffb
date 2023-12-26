from collections import defaultdict
from unittest import result
import qrcode
import cv2
import numpy as np
import argparse
from ultralytics import YOLO
import datetime
import os
import threading
from datetime import datetime, timedelta
from datetime import date
import pytz
from pathlib import Path
from PIL import Image
from ultralytics.utils.plotting import Annotator
import pymssql
from reportlab.pdfgen import canvas
from reportlab.lib import colors as colorPdf
from collections import Counter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Image as ImgRl
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.platypus import Spacer
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import re
import subprocess
import json
import sys
from time import time
import logging
import asyncio
import aiohttp

url = 'https://srs-ssms.com/grading_ai/post_updated_grading_machine.php'
script_directory = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_directory, 'opencv_log.txt')
logging.basicConfig(filename=log_file_path, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')

parser = argparse.ArgumentParser()
parser.add_argument('--yolo_model', type=str, default='./model/best.pt', help='model.pt path')
parser.add_argument('--source', type=str, default='./video/Sampel Scm.mp4', help='source')  # file/folder, 0 for webcam
parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=1280, help='inference size h,w')
parser.add_argument('--conf_thres', type=float, default=0.05, help='object confidence threshold')
parser.add_argument('--iou_thres', type=float, default=0.5, help='IOU threshold for NMS')
parser.add_argument('--tracker', type=str, default='bytetrack.yaml', help='bytetrack.yaml or botsort.yaml')
parser.add_argument('--roi', type=float, default=0.43, help='line height')
parser.add_argument('--show', type=bool, default=True, help='line height')
parser.add_argument('--pull_data', type=str, default='-')
parser.add_argument('--mode', type=str, default='sampling')
parser.add_argument('--save_vid', type=bool, default=False)
parser.add_argument("--debug", type=bool, default=False, help="Enable debug mode to store everything printed result into txt file")
parser.add_argument("--tiket", type=str, default='default', help="Enable debug mode to store everything printed result into txt file")
opt = parser.parse_args()
yolo_model_str = opt.yolo_model
source = opt.source
mode = opt.mode
imgsz = opt.imgsz
conf_thres = opt.conf_thres
iou_thres = opt.iou_thres
tracker = opt.tracker
roi = opt.roi
show = opt.show
pull_data = opt.pull_data
save_vid = opt.save_vid
debug = opt.debug
no_tiket = opt.tiket
TotalJjg = 0
timer = 25
stream = None
ip_pattern = r'(\d+\.\d+\.\d+\.\d+)'
connection = None


file_name_without_extension = os.path.splitext(os.path.basename(source))[0]

id_mill_dir = Path(os.getcwd() + '/config/id_mill.TXT')
id_mill = 1

with open(id_mill_dir, 'r') as z:
    id_mill = z.readline()

def contains_video_keywords(file_path):
    # Define a list of keywords that are commonly found in video file names
    video_keywords = ['avi', 'mp4', 'mkv', 'mov', 'wmv', 'flv', 'webm', 'm4v']

    # Convert the file path to lowercase for case-insensitive matching
    file_path_lower = file_path.lower()

    # Check if any of the video keywords are present in the file path
    for keyword in video_keywords:
        if keyword in file_path_lower:
            return True

    return False
# Use regular expression to find the IP address in the source string
ip_match = re.search(ip_pattern, source)

if ip_match:
    extracted_ip = ip_match.group(1)
    stream = f'rtsp://admin:gr4d!ngs@{extracted_ip}/video'
elif contains_video_keywords(source):
    stream = source
else:
    stream = str(Path(os.getcwd() + '/video/Sampel Scm.mp4'))
    
def print_debug(str):
    if debug == True:
        print(str)

def append_hasil(apStr):
    video_path = source
    file_extension = os.path.splitext(video_path)[1]
    if file_extension.lower() in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv']:
        try:
            folder_path = os.path.dirname(video_path)
            # Get the file name without the extension
            file_name = os.path.splitext(os.path.basename(video_path))[0]

            # Replace the extension with ".txt"
            output_path = os.path.join(folder_path, file_name + ".txt")

            with open(output_path, 'a') as file:
                # Text to append
                line_to_append = apStr

                # Append the line with a newline character
                file.write(line_to_append + '\n')
        except:
            print("error append!")   
    else:
        print("The source is not a video file.")

# Load the YOLOv8 model
model = YOLO(yolo_model_str)

# Open the video filfe
video_path = stream
cap = cv2.VideoCapture(video_path)

# Store the track history
track_history = defaultdict(lambda: [])

# Initialize variables for counting
countOnFrame = 0
kastrasi = 0
kas_reset = 0
skor_tertinggi = 0
jum_tertinggi = 0
skor_terendah = 1000
object_ids_passed = []
object_ids_not_passed = []
baseScore = [0,3,2,0,2,1]
names = list(model.names.values())
class_count = [0] * len(names)
class_count_reset = [0] * len(names)

hexs = ['FF3838', 'FF9D97', 'FF701F', 'FFB21D', 'CFD231', '48F90A', '92CC17', '3DDB86', '1A9334', '00D4BB',
                '2C99A8', '00C2FF', '344593', '6473FF', '0018EC', '8438FF', '520085', 'CB38FF', 'FF95C8', 'FF37C7']
bgr_colors = []

for hex_color in hexs:
    # Convert hex to BGR
    blue = int(hex_color[4:6], 16)
    green = int(hex_color[2:4], 16)
    red = int(hex_color[0:2], 16)
    
    bgr_colors.append((blue, green, red))  # Appending as (Blue, Green, Red)\

max_area = 22000
font = 2
fontRipeness = 1
log_inference = Path(os.getcwd() + '/log_inference_sampling')
tzInfo = pytz.timezone('Asia/Bangkok')
current_date = datetime.now()
formatted_date = current_date.strftime('%Y-%m-%d')
log_inference.mkdir(parents=True, exist_ok=True)  # make dir
save_dir_txt = Path(os.getcwd() + '/hasil/temp.TXT')
if not save_dir_txt.exists():
    log_folder = os.path.dirname(save_dir_txt)
    os.makedirs(log_folder, exist_ok=True)
    save_dir_txt.touch()
grading_total_dir = Path(os.getcwd() + '/hasil/grading_total_log.TXT')
if not grading_total_dir.exists():
    log_folder = os.path.dirname(grading_total_dir)
    os.makedirs(log_folder, exist_ok=True)
    grading_total_dir.touch()


date_start = datetime.now(tz=tzInfo).strftime("%Y-%m-%d %H:%M:%S")
date_end = None
date_start_no_space = str(date_start).split(' ')
bt = False
timer_start = datetime.now(tz=tzInfo)
if debug:
    debug_dir = Path(os.getcwd() + '/hasil/debug/'  +str(date_start)+ '.TXT')
    if not debug_dir.exists() :
        log_folder = os.path.dirname(debug_dir)
        os.makedirs(log_folder, exist_ok=True)
        debug_dir.touch()

def mouse_callback(event, x, y, flags, param):
    
    global bt  # Declare that you want to modify the global variable bt
    
    if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button click event
        #print(f"Mouse clicked at ({x}, {y})")
        if x > 1720 and y < 200:
            bt = True



def save_img_inference_sampling(img, name):
    dt = date.today()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    imgP = Image.frombytes("RGB", (int(img.shape[1]), int(img.shape[0])), img)
    myHeight, myWidth = imgP.size
    imgP = imgP.resize((myHeight, myWidth))

    directory_path = './hasil/' + str(dt) + '/'

    # Check if the directory exists
    if not os.path.exists(directory_path):
        # If it doesn't exist, create the directory
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created.")
    else:
        print(f"Directory '{directory_path}' already exists.")

    # print(directory_path+name)
    imgP.save( directory_path+name, optimize=True, quality=25)

def save_txt(result):
    try:
        with open(save_dir_txt, 'w') as log_file:
            log_file.write(str(result))  # Append the result to the log file with a newline character
        # print(f"Data saved successfully to {save_dir_txt}")
    except Exception as e:
        print(f"Error saving data to, {save_dir_txt}, : {str(e)}")
            
def save_log(result, path, time):
    try:
        formatted_result = ';'.join(map(str, result))
        formatted_entry = f"{formatted_result};{time}\n"
        with open(path, 'a') as log_file:
            log_file.write(formatted_entry)
        # print(f"Data saved successfully to {path}")
    except Exception as e:
        print(f"Error saving data to {path}: {str(e)}")

def close():
    global prefix
    class_count.append(kastrasi)
    file_path = str(log_inference) + '/' + formatted_date + '_log.TXT'
    
    qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
    urlPDF = "https://www.srs-ssms.com/pdf_grading/hasil/" + str(formatted_date) +'/' + str(prefix) + '.pdf'
    
    qr.add_data(urlPDF)
    qr.make(fit=True)
    
    qr_image = qr.make_image(fill_color="black", back_color="white")

    qr_image.save(Path(os.getcwd() + '/default-img/qr.png'))

    names.append('kastrasi')

    date_end = datetime.now(tz=tzInfo).strftime("%Y-%m-%d %H:%M:%S")
    append_hasil(str(date_start) + "," + yolo_model_str + "," + str(imgsz) + "," +  str(roi) + "," + str(conf_thres)+ "," + str(iou_thres) +"," + str(class_count[0])+ "," + str(class_count[1])+ "," + str(class_count[2])+ "," + str(class_count[3])+ "," + str(class_count[4])+ "," + str(class_count[5])+ "," + str(kastrasi)+ "," + str(TotalJjg))
    if mode == 'sampling':
        img_dir = str(Path(os.getcwd() + '/hasil/')) + '/' + str(formatted_date)   + '/' + prefix 
        data = f"{class_count}${names}${img_dir}"
        save_txt(data)
    
    if mode == 'multi-inference':
        path_cctv_log = Path(os.getcwd() + '/hasil/' + formatted_date + '/'+ no_tiket + '/result_' + source + '.TXT')
        if not path_cctv_log.exists():
            path_cctv_log.touch()

        data = {name: count for name, count in zip(names, class_count)}

        json_data = json.dumps(data)
        try:
            with open(path_cctv_log, 'w') as log_file:
                log_file.write(str(json_data))
            
        except Exception as e:
            print(f"Error saving data to, {save_dir_txt}, : {str(e)}")
        save_txt(no_tiket)
    
last_id = 0
track_idsArr = []
prefix = ''
if mode == 'sampling':
    raw = pull_data[1:-2].replace("'","").replace(" ","").split(",")

    try:
        tiket = str(raw[1].replace("/", "_"))
    except Exception as e:
        print(f"An error occurred-tiket: {str(e)}")
        tiket = "-"
    try:
        bisnis_unit = str(raw[4])
    except Exception as e:
        print(f"An error occurred-bisnis_unit: {str(e)}")
        bisnis_unit = "-"
    try:
        divisi = str(raw[5])
    except Exception as e:
        print(f"An error occurred-divisi: {str(e)}")
        divisi = "-"

    prefix = str(tiket) +'_'+  str(bisnis_unit) + '_' + str(divisi) + '_'

window = "Yolov8 "+str(imgsz) + " CONF-" + str(conf_thres) + " IOU-" +  str(iou_thres) + " SRC-" + source + " MODEL-" + yolo_model_str
cv2.namedWindow(window)
cv2.setMouseCallback(window, mouse_callback)
cv2.setWindowProperty(window,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

if cap.isOpened() and save_vid == True:
    output_file = str(date_start) + '.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec (choose the appropriate one for your system)
    fpsVideoCap = 30.0  # Frames per second
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_file, fourcc, fpsVideoCap, (frame_width, frame_height))

if debug:
    output_file_txt = debug_dir
    save_debug = open(output_file_txt, 'w')
    # Redirect stdout and stderr to the file
    sys.stdout = save_debug
    sys.stderr = save_debug

async def post_count_async(date, id_mill):
    try:
        async with aiohttp.ClientSession() as session:
            params = {'id_mill': str(id_mill), 'timestamp': str(date)}
            async with session.post(url, data=params) as resp:
                response_text = await resp.text()
                print("PHP Response: " + response_text)
                response = resp.status
    except Exception as e:
        print("Error: " + str(e))
        response = 99999
    return response

def post_count(date, id_mill):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        code = loop.run_until_complete(post_count_async(date, id_mill))
        print("Status: " + str(code) + " " + date + ".")
    except Exception as e:
        print("Error: " + str(e))
    finally:
        loop.close()

def update_date(date, id_mill):
    threading.Thread(target=post_count, args=(date, id_mill)).start()

lastDate = datetime.now(tz=tzInfo)+timedelta(seconds=0, minutes=0, hours=0)
try:

    while cap.isOpened():
        # update grading machine timestamp
        if datetime.now(tz=tzInfo) > lastDate:
            dateNow = datetime.now(tz=tzInfo).strftime("%Y-%m-%d %H:%M:%S")
            update_date(dateNow, id_mill)
            lastDate = datetime.now(tz=tzInfo) + timedelta(seconds=0, minutes=5, hours=0)
            
        success, frame = cap.read()
        if success:
            # Start the timer
            start_time = time()

            results = model.track(frame, persist=True, conf=conf_thres, iou=iou_thres, imgsz=imgsz, tracker=tracker, verbose=False,stream_buffer=True)
            
            # Stop the timer
            end_time = time()

            # Calculate the FPS
            fps = 1 / (end_time - start_time)

            # Get the boxes and track IDs
            boxes = results[0].boxes.xywh.cpu()
                
            try:
                track_ids = results[0].boxes.id.int().cpu().tolist()
            except Exception as e:
                #print(f"An error occurred-track_ids: {str(e)}")
                track_ids = []
            # track_ids = results[0].boxes.id.int().cpu().tolist()
            clss = results[0].boxes.cls.cpu().tolist()

            # Visualize the results on the frame
            annotated_frame = results[0].plot(conf=False)
            
            # Calculate the middle y-coordinate of the frame
            middle_y = frame.shape[0] * (1-float(roi))
            # Draw the horizontal line
            cv2.line(annotated_frame, (0, int(middle_y)), (annotated_frame.shape[1], int(middle_y)), (0, 255, 0), 2)  # Green line
            
            skorTotal = 0
            countOnFrame = 0
            nilai = 0

            track_idsArr.append(track_ids)
            # Plot the tracks and count objects passing the line
            for box, track_id, cl in zip(boxes, track_ids, clss):
                x, y, w, h = box
                # print(int(w), int(h))
                
                wideArea = int(w) * int(h)

                track = track_history[track_id]
                
                track.append((float(x), float(y)))  # x, y center point
                
                if len(track) > 10:  # retain 10 tracks for 10 frames
                    track.pop(0)
                
                if wideArea < max_area and int(cl) < (int(len(class_count)-1)):
                    text = "kastrasi"
                    text_size, _ = cv2.getTextSize(text, font, fontRipeness, 2)

                    margin = 10  # Additional margin in pixels
                    rect_x = int(x) - margin
                    rect_y = int(y) - text_size[1] - margin  # Position the rectangle above the text with margin
                    rect_width = text_size[0] + 2 * margin  # Add margin on both sides
                    rect_height = text_size[1] + 2 * margin  # Add margin on top and bottom

                    cv2.rectangle(annotated_frame, (rect_x, rect_y), (rect_x + rect_width, rect_y + rect_height), bgr_colors[len(class_count)], -1)
                    cv2.putText(annotated_frame, text, (int(x), int(y)), font, fontRipeness, (255, 255, 255), 2)

                # Draw the tracking lines
                points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)

                try:
                    if middle_y > y and track_id not in object_ids_passed and track_id not in object_ids_not_passed:
                        object_ids_not_passed.append(track_id)
                except Exception as e:
                    print("error append track_id:" + str(e))

                try:
                    if len(object_ids_not_passed) > 50:
                        object_ids_not_passed.pop(0)
                except Exception as e:
                    print("error pop object_ids_not_passed:" + str(e))
                if y > middle_y and track_id not in object_ids_passed and track_id in object_ids_not_passed:
                    tid = False
                    for tis in track_idsArr:
                        if int(track_id) in tis:
                            tid = True
                            break

                    if tid:
                        try:
                            object_ids_passed.append(track_id)
                        except Exception as e:
                            print("error pop object_ids_not_passed:" + str(e))
                        try:
                            object_ids_not_passed.remove(track_id)
                        except Exception as e:
                            print("error cannot remove track_id:" + str(e))
                        last_id = track_id
                        if int(cl) != len(class_count)-1:
                            if wideArea < max_area:
                                kastrasi += 1
                                kas_reset += 1
                        class_count[int(cl)] += 1 
                        class_count_reset[int(cl)] += 1 
                
                        if wideArea < max_area:
                            skorTotal += baseScore[-1]
                        elif int(y-(int(h)/2))>50 and int(y+(int(h)/2))<(frame.shape[0]-50):
                            skorTotal += baseScore[int(cl)]
                        countOnFrame += 1    

                if len(track_idsArr) > 10:
                    try:
                        track_idsArr.pop(0)
                    except Exception as e:
                        print("error cannot remove track_idsArr:" + str(e))

            try:
                nilai = skorTotal / countOnFrame / 3 * 100
            except Exception as e:
                nilai = 0

            TotalJjg = sum(class_count)-int(class_count[5])+int(kastrasi)
            cv2.putText(annotated_frame, f"TOTAL: {TotalJjg}", (20, 40), cv2.FONT_HERSHEY_PLAIN, 3, (100, 100, 100), 15)
            cv2.putText(annotated_frame, f"TOTAL: {TotalJjg}", (20, 40), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 2)
            for index, (name, cc) in enumerate(zip(names, class_count)):
                cv2.putText(annotated_frame, f"{name}: {cc}", (20, ((index + 2) * 40)), font, fontRipeness, bgr_colors[index], 2)
            cv2.putText(annotated_frame, f"kastrasi: {kastrasi}", (20, ((len(class_count) + 2) * 40)), font, fontRipeness, bgr_colors[len(class_count)], 2)
                    
            cv2.putText(annotated_frame, str(datetime.now(tz=tzInfo).strftime("%A,%d-%m-%Y %H:%M:%S")), (850, 40), font, 1.5, (100, 100, 100), 15)
            cv2.putText(annotated_frame, str(datetime.now(tz=tzInfo).strftime("%A,%d-%m-%Y %H:%M:%S")), (850, 40), font, 1.5, (0, 255, 0), 2)

            last_id_str = "IDs: " + str(last_id)
            cv2.putText(annotated_frame, last_id_str, (1740, 1070), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 4)
            cv2.putText(annotated_frame, last_id_str, (1740, 1070), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
            cv2.putText(annotated_frame, "FPS: " + str(int(fps)), (1750, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


            if countOnFrame > jum_tertinggi:
                        jum_tertinggi = countOnFrame
            
            if  countOnFrame >= 2 and nilai > skor_tertinggi:
                skor_tertinggi = round(nilai,2)
                save_img_inference_sampling(annotated_frame, prefix + 'best.JPG')
                # print('tersimpan best')
            elif nilai == skor_tertinggi and countOnFrame > jum_tertinggi:
                skor_tertinggi = round(nilai,2)
                save_img_inference_sampling(annotated_frame, prefix +'best.JPG')
                # print('tersimpan best dengan jumlah tertinggi : ', str(jum_tertinggi))
            elif countOnFrame >2 and nilai < skor_terendah:
                skor_terendah = round(nilai,2)
                save_img_inference_sampling(annotated_frame, prefix +'worst.JPG')
                # print('tersimpan worst')
            elif nilai == skor_terendah and countOnFrame > jum_tertinggi:
                skor_terendah = round(nilai,2)
                save_img_inference_sampling(annotated_frame,prefix +'worst.JPG')
                # print('tersimpan worst dengan jumlah tertinggi : ', str(jum_tertinggi))

            elapsed_time = datetime.now(tz=tzInfo) - timer_start
            
            if elapsed_time.total_seconds() > timer and mode != 'sampling' and mode != 'testing':
                
                current_state = list(class_count_reset)
                kastrasi_int = int(kas_reset)
                current_state.append(kastrasi_int) 
                timer_start = datetime.now(tz=tzInfo)
                save_log(current_state, grading_total_dir, timer_start.strftime("%Y-%m-%d %H:%M:%S"))

                kas_reset = 0
                class_count_reset = [0] * len(names)

            # Display the annotated frame
            width, height = 100, 100
            background_color = (255, 255, 255)  # White in BGR format

            # Define the center and radius of the circular stop sign
            center = (width // 2, height // 2)
            radius = width // 2 - 5  # Leave a small border

            cv2.circle(annotated_frame, (1820,100), radius, (0, 0, 255), -1)  # Red in BGR format

            # Create the white border
            cv2.circle(annotated_frame, (1820,100), radius, (255, 255, 255), 5)
            cv2.putText(annotated_frame, window, (10, 1070), cv2.FONT_HERSHEY_PLAIN, 1, (150, 0, 0), 4)
            cv2.putText(annotated_frame, window, (10, 1070), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

            # Display the annotated frame
            cv2.imshow(window, annotated_frame)

            if save_vid == True:
                out.write(annotated_frame)
            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q") or bt:
                close()
                break
                

        else:
            close()
            break



except Exception as e:
    logging.exception(f"An error occurred: {e}") 
    
finally:
    cap.release()
    if save_vid:
        out.release()
        cmd = [
            'ffmpeg',
            '-i', str(output_file),
            '-c:v', 'libx265',
            '-crf', '23',  
            '-pix_fmt', 'yuv420p',
            '-r', str(fpsVideoCap),
            '-s', f'{frame_width}x{frame_height}',
            str(file_name_without_extension) + '_' + str(date_start) + '_exported.mp4'
        ]
    cv2.destroyAllWindows()
    if save_vid :
        subprocess.run(cmd)

        if os.path.exists(output_file):
            os.remove(output_file)
    
    if debug:
        save_debug.close()


   
    
  


