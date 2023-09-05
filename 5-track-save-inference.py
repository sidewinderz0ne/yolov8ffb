from collections import defaultdict

import cv2
import numpy as np

from ultralytics import YOLO
import datetime
import os
from datetime import datetime
import pytz
from pathlib import Path

from ultralytics.utils.plotting import Annotator

# Load the YOLOv8 model
model = YOLO('/home/grading/yolov8/weights/yolov8n_25_agus_sampling_tanpa_brondol_kosong/weights/best.pt')

# Open the video file
video_path = "/home/grading/sampel_video/scm/sampel_agustus/test_24_agu_banyak.mp4"
cap = cv2.VideoCapture(video_path)

# Store the track history
track_history = defaultdict(lambda: [])

# Initialize variables for counting
object_count = 0
kastrasi = 0
object_ids_passed = set()

names = list(model.names.values())
class_count = [0] * len(names)

hexs = ['FF3838', 'FF9D97', 'FF701F', 'FFB21D', 'CFD231', '48F90A', '92CC17', '3DDB86', '1A9334', '00D4BB',
                '2C99A8', '00C2FF', '344593', '6473FF', '0018EC', '8438FF', '520085', 'CB38FF', 'FF95C8', 'FF37C7']
bgr_colors = []

for hex_color in hexs:
    # Convert hex to BGR
    blue = int(hex_color[4:6], 16)
    green = int(hex_color[2:4], 16)
    red = int(hex_color[0:2], 16)
    
    bgr_colors.append((blue, green, red))  # Appending as (Blue, Green, Red)\

max_area = 20000
font = 2
fontRipeness = 1
log_inference = Path('/home/grading/Yolov5_DeepSort_Pytorch-master_lama/log_inference_sampling')
log_inference.mkdir(parents=True, exist_ok=True)  # make dir
tzInfo = pytz.timezone('Asia/Bangkok')
current_date = datetime.now()
formatted_date = current_date.strftime('%Y-%m-%d')

date_start = datetime.now(tz=tzInfo).strftime("%Y-%m-%d %H:%M:%S")

def save_inference_data(count_per_classes,date_start, date_end, path):

    
    global path_no_plat, no_line_log, path_plat
    str_result = ''
    for count in count_per_classes:
        str_result += str(count) + ';'

    # print(date_start)
    str_result += date_start + ';'
    str_result += str(current_date.strftime('%Y-%m-%d %H:%M:%S'))
    # print(date_end)

    path_inference_truk = path +'/' +formatted_date + '_log.TXT'
    

    with open(path_inference_truk, 'r') as x:
        content = x.readlines()
        
        count = 0
        # LOGGER.info('63')
        for line in content:
            if 'Sedang Berjalan' in line:
                # LOGGER.info('65')
                targetLine = content[count]
                wr = open(path_inference_truk, "w")
                content[count] = targetLine.replace(";Sedang Berjalan","")
                wr.writelines(content)
                wr.close()

                strData = content[count].split(';')
                no_plat = strData[1]

                path_no_plat = path + '/' + no_plat + '.TXT'
                
                path_plat = strData[1]
                no_line_log = count
               
                if not os.path.exists(path_no_plat):
                    
                    f = open(path_no_plat, "a")
                    f.write("")
                    f.close()
    
                with open(path_no_plat, 'r') as z:
                    content = z.readlines()
                    wr = open(path_no_plat, "w")
                    try:
                        # LOGGER.info('68')
                        if len(content[0].strip()) == 0 | content[0] in ['\n', '\r\n']:
                            wr.write(str_result)
                            # LOGGER.info('69')
                        else:
                            wr.write(str_result)
                    except:
                        # LOGGER.info('70')
                        wr.write(str_result)
                    wr.close()
            else:
                print('data_tidak_tersimpan')

            count += 1          


def append_inference_data(count_per_classes,date_start, date_end, path, no_line):
    str_result = ''
    for count in count_per_classes:
        str_result += str(count) + ';'

    str_result += date_start + ';'
    str_result += date_end
    
    file_path = path + '/' + formatted_date + '_log.TXT'
    file_path_inference = path + '/log_inference.TXT'
    
    with open(file_path, 'r') as z:
        content = z.readlines()

        content[no_line] = content[no_line].rstrip("\n") + ";" +   str_result + '\n'

        with open(file_path,"w") as file:
            file.writelines(content)

        wr = open(file_path_inference, "a")
        try:
            if len(content[0].strip()) == 0 | content[0] in ['\n', '\r\n']:
                wr.write(content[no_line])
            else:
                wr.write(content[no_line])
        except:
            wr.write(content[no_line])
        wr.close()
    
def delete_inference_file(path_plat):
    os.remove(path_plat)
    
# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLOv8 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True, conf=0.05, iou=0.5, imgsz=1280)
        

        
        # Get the boxes and track IDs
        boxes = results[0].boxes.xywh.cpu()

        track_ids = results[0].boxes.id.int().cpu().tolist()
        cls = results[0].boxes.cls.cpu().tolist()

        # Visualize the results on the frame
        annotated_frame = results[0].plot(conf=False)

        # print(results[0])

        # Calculate the middle y-coordinate of the frame
        middle_y = annotated_frame.shape[0] // 2

        # Draw the horizontal line
        cv2.line(annotated_frame, (0, middle_y), (annotated_frame.shape[1], middle_y), (0, 255, 0), 2)  # Green line

        # Plot the tracks and count objects passing the line
        for box, track_id, cl in zip(boxes, track_ids, cls):
            x, y, w, h = box
            # print(int(w), int(h))
            
            wideArea = int(w) * int(h)
            if wideArea < max_area:
                #Annotator.box_label(bo.squeeze(), f"id:{track_id} {object_count}", color=bgr_colors[len(class_count)])

            track = track_history[track_id]
            
            track.append((float(x), float(y)))  # x, y center point
            
            # print(float(x), float(y))
            if len(track) > 10:  # retain 10 tracks for 10 frames
                track.pop(0)

            # Draw the tracking lines
            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)

            # Check if the object's center point has crossed the line
            if y > middle_y and track_id not in object_ids_passed:
                object_ids_passed.add(track_id)
                object_count += 1
                if wideArea < max_area:
                    kastrasi += 1
                else:
                    class_count[int(cl)] += 1

        # Display the object count on the frame
        cv2.putText(annotated_frame, f"TOTAL: {object_count}", (20, 40), cv2.FONT_HERSHEY_PLAIN, 3, (100, 100, 100), 15)
        cv2.putText(annotated_frame, f"TOTAL: {object_count}", (20, 40), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 2)
        for index, (name, cc) in enumerate(zip(names, class_count)):
            cv2.putText(annotated_frame, f"{name}: {cc}", (20, ((index + 2) * 40)), font, fontRipeness, bgr_colors[index], 2)
        cv2.putText(annotated_frame, f"kastrasi: {kastrasi}", (20, ((len(class_count) + 2) * 40)), font, fontRipeness, bgr_colors[len(class_count)], 2)
        cv2.putText(annotated_frame, str(datetime.now(tz=tzInfo).strftime("%A,%d-%m-%Y %H:%M:%S")), (850, 40), font, 1.5, (100, 100, 100), 15)
        cv2.putText(annotated_frame, str(datetime.now(tz=tzInfo).strftime("%A,%d-%m-%Y %H:%M:%S")), (850, 40), font, 1.5, (0, 255, 0), 2)
        
        # Display the annotated frame
        cv2.imshow("YOLOv8 Tracking", annotated_frame)

        # print(class_count)
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):

            # save_inference_data(class_count, str(date_start),str(datetime.now(tz=tzInfo).strftime("%Y-%m-%d %H:%M:%S")), str(log_inference))
            # append_inference_data(class_count, str(date_start),str(datetime.now(tz=tzInfo).strftime("%Y-%m-%d %H:%M:%S")), str(log_inference), no_line_log)
            # delete_inference_file(str(log_inference) + '/' + path_plat + '.TXT')
            break


    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()


