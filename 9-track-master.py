from collections import defaultdict
from unittest import result
import qrcode
import cv2
import numpy as np
import argparse
from ultralytics import YOLO
import datetime
import os
from datetime import datetime
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

parser = argparse.ArgumentParser()
parser.add_argument('--yolo_model', type=str, default='./model/best.pt', help='model.pt path')
parser.add_argument('--source', type=str, default='./video/Sampel Scm.mp4', help='source')  # file/folder, 0 for webcam
parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=1280, help='inference size h,w')
parser.add_argument('--conf_thres', type=float, default=0.05, help='object confidence threshold')
parser.add_argument('--iou_thres', type=float, default=0.5, help='IOU threshold for NMS')
parser.add_argument('--tracker', type=str, default='botsort.yaml', help='bytetrack.yaml or botsort.yaml')
parser.add_argument('--roi', type=float, default=0.43, help='line height')
parser.add_argument('--show', type=bool, default=True, help='line height')
parser.add_argument('--pull_data', type=str, default='-')
parser.add_argument('--mode', type=str, default='sampling')
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
no_tiket = ""
img_dir = None
TotalJjg = 0
timer = 25
stream = None
ip_pattern = r'(\d+\.\d+\.\d+\.\d+)'

# Use regular expression to find the IP address in the source string
ip_match = re.search(ip_pattern, source)

if ip_match:
    extracted_ip = ip_match.group(1)
    stream = f'rtsp://admin:gr4d!ngs@{extracted_ip}/video'
else:
    stream = str(Path(os.getcwd() + '/video/Sampel Scm.mp4'))
    
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

            # Open the file in append mode
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
skor_tertinggi = 0
jum_tertinggi = 0
skor_terendah = 1000
object_ids_passed = set()
object_ids_not_passed = set()
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
grading_total_dir = Path(os.getcwd() + '/hasil/' + formatted_date  + '/'+'grading_total_log.TXT')
if not grading_total_dir.exists():
    log_folder = os.path.dirname(grading_total_dir)
    os.makedirs(log_folder, exist_ok=True)
    grading_total_dir.touch()


date_start = datetime.now(tz=tzInfo).strftime("%Y-%m-%d %H:%M:%S")
date_end = None
date_start_no_space = str(date_start).split(' ')
bt = False
timer_start = datetime.now(tz=tzInfo)
def mouse_callback(event, x, y, flags, param):
    
    global bt  # Declare that you want to modify the global variable bt
    
    if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button click event
        # print(f"Mouse clicked at ({x}, {y})")
        if x > 1720 and y < 200:
            bt = True

def generate_report(content, path, prefix_pdf):

    global img_dir
    
    # arrData = content.split(';')

    prctgUnripe = 0
    prctgRipe = 0
    prctgEmptyBunch = 0
    prctgOverripe = 0
    prctgAbnormal = 0
    prctgKastrasi = 0
    prctgLongStalk = 0
    TotalRipeness = 0

    try:
        no_tiket = str(raw[0])
    except Exception as e:
        print(f"An error occurred-no_tiket: {str(e)}")
        no_tiket = "000000"
    try:
        no_plat = str(raw[1])
    except Exception as e:
        print(f"An error occurred-no_plat: {str(e)}")
        no_plat = "KH 0000 ZZ"
    try:
        nama_driver = str(raw[2])
    except Exception as e:
        print(f"An error occurred-nama_driver: {str(e)}")
        nama_driver = "FULAN"
    try:
        bisnis_unit = str(raw[3])
    except Exception as e:
        print(f"An error occurred-bisnis_unit: {str(e)}")
        bisnis_unit = "SSE"
    try:
        divisi = str(raw[4])
    except Exception as e:
        print(f"An error occurred-divisi: {str(e)}")
        divisi = "OZ"
    try:
        blok = str(raw[5])
    except Exception as e:
        print(f"An error occurred-blok: {str(e)}")
        blok = "Z9999"
    try:
        status = str(raw[7])
    except Exception as e:
        print(f"An error occurred-status: {str(e)}")
        status = "-"

    dateStart = date_start
    dateEnd = date_end
        
    # print("Total janjang : " + str(TotalJjg))
    detectBuah = False
    max_widthQr = 200
    if int(TotalJjg) != 0:
        detectBuah = True
        max_widthQr = 140
        prctgUnripe = round((int(class_count[0]) / int(TotalJjg)) * 100,2)
        prctgRipe =  round((int(class_count[1]) / int(TotalJjg)) * 100,2)
        prctgEmptyBunch =  round((int(class_count[2]) / int(TotalJjg)) * 100,2)
        prctgOverripe =  round((int(class_count[3]) / int(TotalJjg)) * 100,2)
        prctgAbnormal =  round((int(class_count[4]) / int(TotalJjg)) * 100,2)
        prctgKastrasi = round((int(kastrasi) / int(TotalJjg)) * 100,2)
        prctgLongStalk =  round((int(class_count[5]) / int(TotalJjg)) * 100,2)
        
        TotalRipeness = round((int(class_count[1]) / int(TotalJjg)) * 100,2)


    TabelAtas = [
        ['No Tiket',   str(no_tiket),'','','', 'Waktu Mulai',  str(dateStart)],
        ['Bisnis Unit',  str(bisnis_unit),'','','','Waktu Selesai', str(dateEnd)],
        ['Divisi',   str(divisi),'','','','No. Plat',str(no_plat)],
        ['Blok',  str(blok),'','','','Driver',str(nama_driver)],
        ['Status',  str(status)]
    ]

    colEachTable1 = [1.1*inch, 1.4*inch,  0.6*inch, 0.6*inch, 0.6*inch, 1.1*inch, 2.5*inch]

    TabelBawah = [
        ['Total\nJanjang', 'Ripe', 'Overripe', 'Unripe', 'Empty\nBunch','Abnormal','Kastrasi','Tangkai\nPanjang', 'Total\nRipeness'],
        [TotalJjg, int(class_count[1]) , int(class_count[2]) , int(class_count[0]) ,int(class_count[3]) , int(class_count[4]) , kastrasi ,int(class_count[5]) , str(TotalRipeness) + ' % '],
        ['',  str(prctgRipe) + ' %', str(prctgOverripe)+ ' %', str(prctgUnripe) +' %', str(prctgEmptyBunch) +  ' %',  str(prctgAbnormal)+ ' %',  str(prctgKastrasi)+ ' %',str(prctgLongStalk)+ ' %','']
    ]   


    colEachTable2 = [0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch]

    spacer = Spacer(1, 0.25*inch)
    
    # print(prefix_pdf)

    img_dir = str(path) + '/' + str(formatted_date)   + '/' + prefix_pdf 

    print(img_dir)

    checkImgBest = os.path.isfile(str(img_dir) +'best.JPG')
    if checkImgBest:
        image = ImgRl(str(img_dir) + 'best.JPG')
    else:
        image = ImgRl(Path(os.getcwd() + '/default-img/no_image.png'))

    checkImgWorst = os.path.isfile(str(img_dir) +'worst.JPG')  
    if checkImgWorst:
        image2 = ImgRl(str(img_dir) + 'worst.JPG')
    else:
        image2 = ImgRl(Path(os.getcwd() + '/default-img/no_image.png'))
    
    logoCbi = ImgRl(Path(os.getcwd() + '/default-img/Logo CBI.png'))
    imageQr = ImgRl(Path(os.getcwd() + '/default-img/qr.png'))
    max_width = 285  # The maximum allowed width of the image
    max_widthLogo = 70  # The maximum allowed width of the image
    widthLogo = min(logoCbi.drawWidth, max_widthLogo)  # The desired width of the image
    width1 = min(image.drawWidth, max_width)  # The desired width of the image
    width2 = min(image2.drawWidth, max_width)  # The desired width of the image
    widthQr = min(imageQr.drawWidth, max_widthQr)  # The desired width of the image
    image._restrictSize(width1, image.drawHeight)
    image2._restrictSize(width2, image2.drawHeight)
    logoCbi._restrictSize(widthLogo, logoCbi.drawHeight)
    imageQr._restrictSize(widthQr, imageQr.drawHeight)

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

    
    name_pdf = str(path) +'/' + str(formatted_date) + '/'+ str(prefix_pdf) + '.pdf'
    # print(name_pdf)
    doc = SimpleDocTemplate(name_pdf, pagesize=letter,  topMargin=0)
    
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

    qr_data = [[imageQr]]

    tblQr = Table(qr_data, [4.0*inch])
    tblQr.setStyle(TableStyle([
    #    ('GRID', (0, 0), (-1, -1), 1, colorPdf.black), 
       ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
       ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
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
    elements.append(tblQr)
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

    # print(directory_path+name)
    imgP.save( directory_path+name, optimize=True, quality=25)

def change_push_time():
    try:
        # Database connection
        conn = pymssql.connect(
            server='192.168.1.254\DBSTAGING',
            user='usertesting',
            password='Qwerty@123',
            database='skmstagingdb'
        )

        notiket = raw[1]
        # print("no tiket:")
        # print(notiket)
        # print("raw:")
        # print(raw)
        cursor = conn.cursor()

        SQL_UPDATE = """
        UPDATE MOPweighbridgeTicket_Staging
        SET AI_pull_time = GETDATE()
        WHERE WBTicketNo = %s;
        """

        cursor.execute(SQL_UPDATE, (notiket))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"An error occurred-change_push_time: {str(e)}")

def push_grading_quality():
    try:
        conn = pymssql.connect(
            server='192.168.1.254\DBSTAGING',
            user='usertesting',
            password='Qwerty@123',
            database='skmstagingdb',
            as_dict=True
        )

        SQL_QUERY = """
        SELECT Ppro_GradeCode, Ppro_GradeDescription
        FROM MasterGrading_Staging;
        """

        cursor = conn.cursor()
        cursor.execute(SQL_QUERY)

        gradecodes = []
        gradedescriptions = []

        for row in cursor.fetchall():
            gradecodes.append(row['Ppro_GradeCode'])
            gradedescriptions.append(row['Ppro_GradeDescription'])

        conn.close()

        for gradedescription, gradecode in zip(gradedescriptions, gradecodes):
            for index, name in enumerate(names):
                # Convert gradedescription to lowercase and replace spaces with underscores
                cleaned_description = gradedescription.lower().replace(" ", "_")
                
                if cleaned_description == name and int(class_count[index]) != 0:
                    if cleaned_description == "abnormal":  # Check if cleaned_description is "abnormal"
                        push_data(gradecode, int(class_count[index]) + int(kastrasi))
                    else:
                        push_data(gradecode, class_count[index])
                elif cleaned_description == "tangkai_panjang" and name == "long_stalk" and int(class_count[index]) != 0:
                    push_data(gradecode, class_count[index])
    except Exception as e:
        print(f"An error occurred-push_grading_quality: {str(e)}")


def push_data(intCat,intVal):
    conn = pymssql.connect(
        server='192.168.1.254\DBSTAGING',
        user='usertesting',
        password='Qwerty@123',
        database='skmstagingdb',
        as_dict=True
    )

    # Values for the new row
    new_row = {
        'AI_NoTicket': str(raw[0]) if raw else "000000",
        'AI_Grading': str(intCat),
        'AI_JanjangSample': str(TotalJjg), 
        'AI_TotalJanjang': str(TotalJjg),
        'AI_Janjang': str(intVal)
    }

    # Build the SQL INSERT statement
    SQL_INSERT = """
    INSERT INTO MOPQuality_Staging (AI_NoTicket, AI_Grading, AI_JanjangSample, AI_TotalJanjang, AI_push_time, AI_Janjang)
    VALUES (%(AI_NoTicket)s, %(AI_Grading)s, %(AI_JanjangSample)s, %(AI_TotalJanjang)s, GETDATE(),%(AI_Janjang)s);
    """

    # Create a cursor and execute the INSERT statement
    cursor = conn.cursor()
    cursor.execute(SQL_INSERT, new_row)

    # Commit the transaction to save the changes to the database
    conn.commit()

    # Close the database connection
    conn.close()

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
    global img_dir, prefix
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

    if mode == 'sampling':
        push_grading_quality()
        change_push_time()
        append_hasil(str(date_start) + "," + yolo_model_str + "," + str(imgsz) + "," +  str(roi) + "," + str(conf_thres)+ "," + str(class_count[0])+ "," + str(class_count[1])+ "," + str(class_count[2])+ "," + str(class_count[3])+ "," + str(class_count[4])+ "," + str(class_count[5])+ "," + str(kastrasi)+ "," + str(TotalJjg))
        generate_report(raw,  Path(os.getcwd() + '/hasil/') ,prefix)
        data = f"{class_count}${names}${img_dir}"
        save_txt(data)

cv2.namedWindow("Detect FFB Yolov8")
cv2.setMouseCallback("Detect FFB Yolov8", mouse_callback)
    
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


while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()
    if success:
        
        # Run YOLOv8 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True, conf=conf_thres, iou=iou_thres, imgsz=imgsz, tracker=tracker, verbose=False)
        
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
       # Print the value counts
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

            # Check if the object's center point has crossed the line
            if middle_y > y and track_id not in object_ids_passed and track_id not in object_ids_not_passed:
                object_ids_not_passed.add(track_id)

            if len(object_ids_not_passed) > 50:
                del object_ids_not_passed[0]

            if y > middle_y and track_id not in object_ids_passed and track_id in object_ids_not_passed:
                tid = True
                for tis in track_idsArr:
                    # print("track_id: "+str(track_id))
                    # print("tis: "+str(tis))
                    if int(track_id) not in tis:
                        tid = False
                        # print(tid)
                if tid:
                    object_ids_passed.add(track_id)
                    object_ids_not_passed.remove(track_id)
                    last_id = track_id
                    if int(cl) != len(class_count)-1:
                        if wideArea < max_area:
                            kastrasi += 1
                    class_count[int(cl)] += 1 
            
                    if wideArea < max_area:
                        skorTotal += baseScore[-1]
                    elif int(y-(int(h)/2))>50 and int(y+(int(h)/2))<(frame.shape[0]-50):
                        skorTotal += baseScore[int(cl)]
                    countOnFrame += 1    

            if len(track_idsArr) > 10:
                del track_idsArr[0]

        try:
            nilai = skorTotal / countOnFrame / 3 * 100
        except Exception as e:
            #print(f"An error occurred-nilai: {str(e)}")
            nilai = 0
        # print(nilai)        

        # Display the object count on the frame
        TotalJjg = sum(class_count)-int(class_count[5])+int(kastrasi)
        cv2.putText(annotated_frame, f"TOTAL: {TotalJjg}", (20, 40), cv2.FONT_HERSHEY_PLAIN, 3, (100, 100, 100), 15)
        cv2.putText(annotated_frame, f"TOTAL: {TotalJjg}", (20, 40), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 2)
        for index, (name, cc) in enumerate(zip(names, class_count)):
            cv2.putText(annotated_frame, f"{name}: {cc}", (20, ((index + 2) * 40)), font, fontRipeness, bgr_colors[index], 2)
        cv2.putText(annotated_frame, f"kastrasi: {kastrasi}", (20, ((len(class_count) + 2) * 40)), font, fontRipeness, bgr_colors[len(class_count)], 2)
                
        cv2.putText(annotated_frame, str(datetime.now(tz=tzInfo).strftime("%A,%d-%m-%Y %H:%M:%S")), (850, 40), font, 1.5, (100, 100, 100), 15)
        cv2.putText(annotated_frame, str(datetime.now(tz=tzInfo).strftime("%A,%d-%m-%Y %H:%M:%S")), (850, 40), font, 1.5, (0, 255, 0), 2)
        cv2.putText(annotated_frame, str(last_id), (850, 80), font, 1.5, (0, 0, 255), 2)


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
        
        if elapsed_time.total_seconds() > timer and mode != 'sampling':
            
            current_state = list(class_count)
            kastrasi_int = int(kastrasi)
            current_state.append(kastrasi_int) 
            timer_start = datetime.now(tz=tzInfo)
            save_log(current_state, grading_total_dir, timer_start.strftime("%Y-%m-%d %H:%M:%S"))

        # Display the annotated frame
        width, height = 100, 100
        background_color = (255, 255, 255)  # White in BGR format

        # Define the center and radius of the circular stop sign
        center = (width // 2, height // 2)
        radius = width // 2 - 5  # Leave a small border

        cv2.circle(annotated_frame, (1820,100), radius, (0, 0, 255), -1)  # Red in BGR format

        # Create the white border
        cv2.circle(annotated_frame, (1820,100), radius, (255, 255, 255), 5)
        # Display the annotated frame
        cv2.imshow("Detect FFB Yolov8", annotated_frame)

        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q") or bt:
            close()
            break
            

    else:
        # Break the loop if the end of the video is reached
        close()
        break
    # except:
    #     print("Tidak ada janjang")

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()


   
    
  


