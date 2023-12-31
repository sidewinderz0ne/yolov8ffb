from collections import defaultdict
from unittest import result

import cv2
import numpy as np

from ultralytics import YOLO
import datetime
import os
from datetime import datetime
from datetime import date
import pytz
from pathlib import Path
from PIL import Image
from ultralytics.utils.plotting import Annotator

from reportlab.pdfgen import canvas
from reportlab.lib import colors as colorPdf
from collections import Counter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Image as ImgRl
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.platypus import Spacer
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

def varTry(valStr, defVal):
    try:
        if len(valStr) > 0:
            valTry = valStr
        else:
            # Handle the case where arrData is empty
            valTry = defVal
    except IndexError:
        # Handle the case where arrData is empty (IndexError will be raised if it's empty)
        valTry = defVal
    return valTry

# Load the YOLOv8 model
model = YOLO('/home/sdz/grading/inference/Models/yolov8-25-8-23-best.pt')

# Open the video file
video_path = "/home/sdz/grading/inference/Sources/Sampel_SCM.mp4"
cap = cv2.VideoCapture(video_path)

# Store the track history
track_history = defaultdict(lambda: [])

# Initialize variables for counting
object_count = 0
countOnFrame = 0
kastrasi = 0
skor_tertinggi = 0
jum_tertinggi = 0
skor_terendah = 1000
object_ids_passed = set()
baseScore = [0,3,2,0,2,1]
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

max_area = 25000
font = 2
fontRipeness = 1
log_inference = Path('/home/grading/Yolov5_DeepSort_Pytorch-master/log_inference_sampling')
log_inference.mkdir(parents=True, exist_ok=True)  # make dir
tzInfo = pytz.timezone('Asia/Bangkok')
current_date = datetime.now()
formatted_date = current_date.strftime('%Y-%m-%d')

date_start = datetime.now(tz=tzInfo).strftime("%Y-%m-%d %H:%M:%S")

def generate_report(content, path):
    
    print(path)
    arrData = content.split(';')

    TotalJjg = 0
    prctgUnripe = 0
    prctgRipe = 0
    prctgEmptyBunch = 0
    prctgOverripe = 0
    prctgAbnormal = 0
    prctgKastrasi = 0
    prctgLongStalk = 0
    TotalRipeness = 0

    no_tiket = varTry(str(arrData[0]),"000000")
    no_plat = varTry(str(arrData[1]),"KH 0000 ZZ")
    nama_driver = varTry(str(arrData[2]), "FULAN")
    bisnis_unit = varTry(str(arrData[3]).replace('\n',''),"SSE")
    divisi = varTry(str(arrData[4]),"OZ")
    blok = varTry(str(arrData[5]),"Z9999")
    status = varTry(str(arrData[6]),"-")  

    dateStart = date_start
    dateEnd = date_end
    
    TotalJjg = int(Ripe) + int(Overripe) + int(Unripe) + int(EmptyBunch) + int(Abnormal) + int(Kastrasi)
    detectBuah = False

    if int(TotalJjg) != 0:
        detectBuah = True
        prctgUnripe = round((int(Unripe) / int(TotalJjg)) * 100,2)
        prctgRipe = round((int(Ripe) / int(TotalJjg)) * 100,2)
        prctgEmptyBunch = round((int(EmptyBunch) / int(TotalJjg)) * 100,2)
        prctgOverripe = round((int(Overripe) / int(TotalJjg)) * 100,2)
        prctgAbnormal = round((int(Abnormal) / int(TotalJjg)) * 100,2)
        prctgKastrasi = round((int(Kastrasi) / int(TotalJjg)) * 100,2)
        prctgLongStalk = round((int(LongStalk) / int(TotalJjg)) * 100,2)
        
        TotalRipeness = round((int(Ripe) / int(TotalJjg)) * 100,2)

    date = dateStart.split(' ')

    
    TabelAtas = [
        ['No Tiket',   str(no_tiket),'','','', 'Waktu Mulai',  str(dateStart)],
        ['Bisnis Unit',  str(bisnis_unit),'','','','Waktu Selesai', str(dateEnd)],
        ['Divisi',   str(divisi),'','','','No. Plat',str(no_plat)],
        ['Blok',  str(blok),'','','','Driver',str(nama_driver)],
        ['Status',  str(status)]
    ]

    colEachTable1 = [1.2*inch, 1.6*inch,  0.8*inch, 0.8*inch, 0.8*inch, 1.2*inch, 1.6*inch]

    TabelBawah = [
        ['Total\nJanjang', 'Ripe', 'Overripe', 'Unripe', 'Empty\nBunch','Abnormal','Kastrasi','Tangkai\nPanjang', 'Total\nRipeness'],
        [TotalJjg, Ripe , Overripe , Unripe ,EmptyBunch , Abnormal , Kastrasi ,LongStalk , str(TotalRipeness) + ' % '],
        ['',  str(prctgRipe) + ' %', str(prctgOverripe)+ ' %', str(prctgUnripe) +' %', str(prctgEmptyBunch) +  ' %',  str(prctgAbnormal)+ ' %',  str(prctgKastrasi)+ ' %',str(prctgLongStalk)+ ' %','']
    ]   


    colEachTable2 = [0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch]

    spacer = Spacer(1, 0.25*inch)
    
    checkImgBest = os.path.isfile(os.path.join(path, '_best_.JPG'))
    if checkImgBest:
        best_last_modified = datetime.fromtimestamp(os.path.getmtime(os.path.join(path, '_best_.JPG'))).date()
        best_last_modified_str = best_last_modified.strftime('%Y-%m-%d')
        if best_last_modified_str == formatted_date and detectBuah:
            image = ImgRl("/home/grading/Yolov5_DeepSort_Pytorch-master/img_inference/_best_.JPG")
        else:
            image = ImgRl("/home/grading/Yolov5_DeepSort_Pytorch-master/img_inference/no_image.png")
    else:
        image = ImgRl("/home/grading/Yolov5_DeepSort_Pytorch-master/img_inference/no_image.png")

    # Check if _worst_.JPG file exists
    checkImgWorst = os.path.isfile(os.path.join(path, '_worst_.JPG'))
    if checkImgWorst:
        worst_last_modified = datetime.fromtimestamp(os.path.getmtime(os.path.join(path, '_worst_.JPG'))).date()
        worst_last_modified_str = worst_last_modified.strftime('%Y-%m-%d')
        if worst_last_modified_str == formatted_date and detectBuah:
            image2 = ImgRl("/home/grading/Yolov5_DeepSort_Pytorch-master/img_inference/_worst_.JPG")
        else:
            image2 = ImgRl("/home/grading/Yolov5_DeepSort_Pytorch-master/img_inference/no_image.png")
    else:
        image2 = ImgRl("/home/grading/Yolov5_DeepSort_Pytorch-master/img_inference/no_image.png")
    
    logoCbi = ImgRl("/home/grading/Yolov5_DeepSort_Pytorch-master/Logo CBI.png")
    max_width = 285  # The maximum allowed width of the image
    max_widthLogo = 70  # The maximum allowed width of the image
    widthLogo = min(logoCbi.drawWidth, max_widthLogo)  # The desired width of the image
    width1 = min(image.drawWidth, max_width)  # The desired width of the image
    width2 = min(image2.drawWidth, max_width)  # The desired width of the image
    image._restrictSize(width1, image.drawHeight)
    image2._restrictSize(width2, image2.drawHeight)
    logoCbi._restrictSize(widthLogo, logoCbi.drawHeight)

    styleTitle = ParagraphStyle(name='Normal', fontName='Helvetica-Bold',fontSize=12,fontWeight='bold')
    t1 = Paragraph('CROP RIPENESS CHECK REPORT' )
    title_section = [[logoCbi, 'CROP RIPENESS CHECK REPORT', '']]

    
    titleImg = Table(title_section, colWidths=[100,375,100])
    titleImg.setStyle(TableStyle([
         ('GRID', (0, 0), (-1, -1), 1,  colorPdf.black),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 0), (1, 0), 15),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
       ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))

    
    dataImg = [[image, image2],['Kondisi Paling Baik', 'Kondisi Paling Buruk']]
    tblImg = Table(dataImg, [4.0*inch,4.0*inch])
    tblImg.setStyle(TableStyle([
    #    ('GRID', (0, 0), (-1, -1), 1, colorPdf.black), 
       ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
       ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))

    

    dataP1 = [['KONDISI TBS : ']]
    tblP1 = Table(dataP1,[8*inch])
    tblP1.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))


    doc = SimpleDocTemplate("/home/grading/Yolov5_DeepSort_Pytorch-master/pdf/" + str(dateStart) + '_' + bisnis_unit +'_' + divisi  + '.pdf', pagesize=letter)
    
    table1 = Table(TabelAtas,colWidths=colEachTable1)
    table1.setStyle(TableStyle([
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (1, 4), 1, colorPdf.black),
        ('GRID', (5, 0), (8, 3), 1, colorPdf.black)
    ]))
    table2 = Table(TabelBawah, colWidths=colEachTable2)
    table2.setStyle(TableStyle([
        ('ALIGN', (0, 0), (8, 0), 'CENTER'),
        ('ALIGN', (0, 1), (8, 1), 'LEFT'),
        ('VALIGN', (0, 0), (8, 0), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colorPdf.black),
        ('SPAN', (0, 1), (0, 2)),
        ('SPAN', (8, 1), (8, 2)),
        ('ALIGN', (8, 1), (8, 2), 'CENTER'), 
        ('VALIGN', (8, 1), (8, 2), 'MIDDLE'), 
        ('ALIGN', (0, 1), (0, 2), 'CENTER'),  
        ('VALIGN', (0, 1), (0, 2), 'MIDDLE'), 
    ]))



    elements = []
    elements.append(titleImg)
    elements.append(spacer)
    elements.append(table1)
    elements.append(spacer)
    elements.append(tblP1)
    
    elements.append(tblImg)
    elements.append(spacer)
    elements.append(table2)
    doc.build(elements)

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

    imgP.save( directory_path+name, optimize=True, quality=25)

def save_inference_data(count_per_classes,date_start, date_end, path):

    global path_no_plat, no_line_log, path_plat
    str_result = ''
    for count in count_per_classes:
        str_result += str(count) + ';'

    str_result += date_start + ';'
    str_result += str(current_date.strftime('%Y-%m-%d %H:%M:%S'))

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
            
        try:
            track_ids = results[0].boxes.id.int().cpu().tolist()
        except:
            track_ids = []
        # track_ids = results[0].boxes.id.int().cpu().tolist()
        clss = results[0].boxes.cls.cpu().tolist()

        # Visualize the results on the frame
        annotated_frame = results[0].plot(conf=False)
        
        # Calculate the middle y-coordinate of the frame
        middle_y = frame.shape[0] // 2

        # Draw the horizontal line
        cv2.line(annotated_frame, (0, middle_y), (annotated_frame.shape[1], middle_y), (0, 255, 0), 2)  # Green line

       # Print the value counts
        skorTotal = 0
        countOnFrame = 0
        nilai = 0
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

            # Check if the object's center point has crossed the line
            
            if y > middle_y and track_id not in object_ids_passed:
                object_ids_passed.add(track_id)
                if int(cl) != len(class_count)-1:
                    object_count += 1
                    if wideArea < max_area:
                        kastrasi += 1
                class_count[int(cl)] += 1 
            
            if wideArea < max_area:
                skorTotal += baseScore[-1]
            elif int(y-(int(h)/2))>50 and int(y+(int(h)/2))<(frame.shape[0]-50):
                skorTotal += baseScore[int(cl)]
            countOnFrame += 1    

        try:
            nilai = skorTotal / countOnFrame / 3 * 100
        except:
            nilai = 0
        print(nilai)        

        # Display the object count on the frame
        cv2.putText(annotated_frame, f"TOTAL: {object_count}", (20, 40), cv2.FONT_HERSHEY_PLAIN, 3, (100, 100, 100), 15)
        cv2.putText(annotated_frame, f"TOTAL: {object_count}", (20, 40), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 2)
        for index, (name, cc) in enumerate(zip(names, class_count)):
            cv2.putText(annotated_frame, f"{name}: {cc}", (20, ((index + 2) * 40)), font, fontRipeness, bgr_colors[index], 2)
        cv2.putText(annotated_frame, f"kastrasi: {kastrasi}", (20, ((len(class_count) + 2) * 40)), font, fontRipeness, bgr_colors[len(class_count)], 2)
                
        cv2.putText(annotated_frame, str(datetime.now(tz=tzInfo).strftime("%A,%d-%m-%Y %H:%M:%S")), (850, 40), font, 1.5, (100, 100, 100), 15)
        cv2.putText(annotated_frame, str(datetime.now(tz=tzInfo).strftime("%A,%d-%m-%Y %H:%M:%S")), (850, 40), font, 1.5, (0, 255, 0), 2)

        if countOnFrame > jum_tertinggi:
                    jum_tertinggi = countOnFrame
        
        print(jum_tertinggi)
        if  countOnFrame >= 2 and nilai > skor_tertinggi:
            skor_tertinggi = round(nilai,2)
            save_img_inference_sampling(annotated_frame,'best.JPG')
            print('tersimpan best')
        elif nilai == skor_tertinggi and countOnFrame > jum_tertinggi:
            skor_tertinggi = round(nilai,2)
            save_img_inference_sampling(annotated_frame, 'best.JPG')
            print('tersimpan best dengan jumlah tertinggi : ', str(jum_tertinggi))
        elif countOnFrame >2 and nilai < skor_terendah:
            skor_terendah = round(nilai,2)
            save_img_inference_sampling(annotated_frame, 'worst.JPG')
            print('tersimpan worst')
        elif nilai == skor_terendah and countOnFrame > jum_tertinggi:
            skor_terendah = round(nilai,2)
            save_img_inference_sampling(annotated_frame,'worst.JPG')
            print('tersimpan worst dengan jumlah tertinggi : ', str(jum_tertinggi))


        # Display the annotated frame
        cv2.imshow("YOLOv8 Tracking", annotated_frame)

        
        # print(class_count)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            class_count.append(kastrasi)

            save_inference_data(class_count, str(date_start),str(datetime.now(tz=tzInfo).strftime("%Y-%m-%d %H:%M:%S")), str(log_inference))
            append_inference_data(class_count, str(date_start),str(datetime.now(tz=tzInfo).strftime("%Y-%m-%d %H:%M:%S")), str(log_inference), no_line_log)
            delete_inference_file(str(log_inference) + '/' + path_plat + '.TXT')

            file_path = str(log_inference) + '/' + formatted_date + '_log.TXT'
                    
            content = ''
            with open(file_path, 'r') as z:
                content = z.readlines()
                content = content[no_line_log]

            date_end = datetime.now(tz=tzInfo).strftime("%Y-%m-%d %H:%M:%S")
            #generate_report(content, Path('/home/grading/Yolov5_DeepSort_Pytorch-master/img_inference'))

            break


    else:
        # Break the loop if the end of the video is reached
        break
    # except:
    #     print("Tidak ada janjang")

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()


