from itertools import count
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.messagebox import YES, showinfo
import os
from pathlib import Path
import datetime
from datetime import datetime as dt
import threading
import tkinter.font as tkFont
import subprocess
from unicodedata import name
from unittest import result
import argparse
import ast
import pymssql
import bcrypt
import sqlite3
import re
import argparse
import socket
from urllib.request import urlopen
import json
import hashlib
import asyncio
from PIL import Image, ImageTk, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib import colors as colorPdf
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Image as ImgRl,  PageBreak
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.platypus import Spacer
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

parser = argparse.ArgumentParser()
parser.add_argument('--mode', type=str, default='single-inference')
opt = parser.parse_args()
mode_app = opt.mode
url = "https://srs-ssms.com/grading_ai/get_list_mill.php"

columns = ('no', 'notiket', 'nopol', 'driver', 'b_unit','divisi', 'field', 'bunches', 'ownership', 'pushtime', 'action')

current_date = datetime.datetime.now()

# Format the date as yyyy-mm-dd
formatted_date = current_date.strftime('%Y-%m-%d')
status_mode = None
log_data = Path(os.getcwd() + '/data')
data_bunit = Path(str(log_data) + '/bunit_mapping.txt')
data_div = Path(str(log_data) + '/div_mapping.txt')
data_block = Path(str(log_data) + '/blok_mapping.txt')
log_mill = Path(str(log_data) + '/mill_mapping.txt')

dir_user = Path(os.getcwd() + '/user')
dir_user.mkdir(parents=True, exist_ok=True)  
log_data_user = Path(str(dir_user) + '/data.txt')
date_start_conveyor = None
date_end_conveyor = None
connection = None 
accent2 = "#d2d7fc"
id_mill_dir = Path(os.getcwd() + '/config/id_mill.TXT')
isClosedFrame3 = False
id_mill = None
with open(id_mill_dir, 'r') as z:
    id_mill = z.readline()

if not log_data_user.exists():
    log_data_user.touch()

log_inference = Path(os.getcwd() + '/hasil')

log_inference.mkdir(parents=True, exist_ok=True)  # make dir
save_dir_txt = Path(os.getcwd() + '/hasil/temp.TXT')
if not save_dir_txt.exists():
    log_folder = os.path.dirname(save_dir_txt)
    os.makedirs(log_folder, exist_ok=True)
    save_dir_txt.touch()

log_dir = Path(os.getcwd() + '/hasil/' + formatted_date  + '/'+ formatted_date+'_log.TXT')

if not log_dir.exists():
    log_folder = os.path.dirname(log_dir)
    os.makedirs(log_folder, exist_ok=True)
    log_dir.touch()

offline_log_dir = Path(os.getcwd() + '/hasil/' + formatted_date  + '/offline_log.TXT')

if not offline_log_dir.exists():
    log_folder = os.path.dirname(offline_log_dir)
    os.makedirs(log_folder, exist_ok=True)
    offline_log_dir.touch()

def remove_non_numeric(input_str):
    return re.sub(r'[^0-9.]', '', input_str)

def create_datetime(date, hour, minute, second):
    return dt(date.year, date.month, date.day, hour, minute, second)

def generate_report(raw, img_dir,class_count_dict,class_names, brondol, brondolBusuk, dirt, editData = None):

    global totalJjg
    
    class_dict = {name: 'Tangkai\nPanjang' if name == 'long_stalk' else 'Empty Bunch' if name == 'empty_bunch' else name.capitalize() for name in class_names}
    
    totalJjg = 0
    for key, value in class_count_dict.items():
        if key != 'long_stalk':
            totalJjg += value

    try:
        no_tiket = str(raw[1])
    except Exception as e:
        print(f"An error occurred-no_tiket: {str(e)}")
        no_tiket = "000000"
    try:
        no_plat = str(raw[2])
    except Exception as e:
        print(f"An error occurred-no_plat: {str(e)}")
        no_plat = "KH 0000 ZZ"
    try:
        nama_driver = str(raw[3])
    except Exception as e:
        print(f"An error occurred-nama_driver: {str(e)}")
        nama_driver = "FULAN"
    try:
        bisnis_unit = str(raw[4])
    except Exception as e:
        print(f"An error occurred-bisnis_unit: {str(e)}")
        bisnis_unit = "SSE"
    try:
        divisi = str(raw[5])
    except Exception as e:
        print(f"An error occurred-divisi: {str(e)}")
        divisi = "OZ"
    try:
        blok = str(raw[6])
    except Exception as e:
        print(f"An error occurred-blok: {str(e)}")
        blok = "Z9999"
    try:
        status = str(raw[8])
    except Exception as e:
        print(f"An error occurred-status: {str(e)}")
        status = "-"

    dateStart = date_start_conveyor
    dateEnd = date_end_conveyor
    TotalRipeness = 0
    max_widthQr = 140

    

    TabelAtas = [
            ['No Tiket',   str(no_tiket),'','','', 'Waktu Mulai',  str(dateStart)],
            ['Bisnis Unit',  str(bisnis_unit),'','','','Waktu Selesai', str(dateEnd)],
            ['Divisi',   str(divisi),'','','','No. Plat',str(no_plat)],
            ['Blok',  str(blok),'','','','Driver',str(nama_driver)],
            ['Status',  str(status)]
        ]
    
    default_value = 0
    TabelBawah = [
        ['Total\nJanjang', default_value, default_value, default_value, default_value, default_value, default_value, default_value, 'Total\nRipeness'],
        [default_value, default_value, default_value, default_value, default_value, default_value, default_value, default_value, '0.00 %'],
        ['', '0.00 %', '0.00 %', '0.00 %', '0.00 %', '0.00 %', '0.00 %', '0.00 %', '0.00 %']
    ]

    colEachTable1 = [1.0 * inch, 2.4 * inch, 0.6 * inch, 0.6 * inch, 0.6 * inch, 1.2 * inch, 1.7 * inch]
    if int(totalJjg) != 0:
        max_widthQr =150
        
        
       
        percentages = [(class_count_dict[class_name] / totalJjg) * 100 for class_name in class_names]
        formatted_percentages = [f"{percentage:.2f} %" if percentage != 0 else '0 %' for percentage in percentages]
        prctg_per_class = dict(zip(class_names, formatted_percentages))

        TabelBawah = [
            ['Total\nJanjang', class_dict['ripe'], class_dict['unripe'], class_dict['overripe'], class_dict['empty_bunch'],class_dict['abnormal'],class_dict['kastrasi'], class_dict['long_stalk'], 'Total\nRipeness'],
            [totalJjg, class_count_dict['ripe'], class_count_dict['unripe'], class_count_dict['overripe'], class_count_dict['empty_bunch'], class_count_dict['abnormal'], class_count_dict['kastrasi'],class_count_dict['long_stalk'],prctg_per_class['ripe']],
            ['',  prctg_per_class['ripe'] , prctg_per_class['unripe'], prctg_per_class['overripe'], prctg_per_class['empty_bunch'],  prctg_per_class['abnormal'],  prctg_per_class['kastrasi'],prctg_per_class['long_stalk'] , prctg_per_class['ripe']]
        ]

    
    
    page_width_points, page_height_points = letter

        # Convert the page width from points to inches
    page_width_inches = page_width_points / inch

    colEachTableInput = [1.3*inch, 1.3*inch, 1.3*inch]


    colEachTable2 = [0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch]

    spacer = Spacer(1, 0.25*inch)

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
    max_width = 240  # The maximum allowed width of the image
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

    qr_data = [[imageQr]]

    tblQr = Table(qr_data, [4.0*inch])
    tblQr.setStyle(TableStyle([
    #    ('GRID', (0, 0), (-1, -1), 1, colorPdf.black), 
       ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
       ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))

    TabelInputTambahan = [
        ['Brondolan\n(kg)', 'Brondolan Busuk\n(kg)', 'Dirt/Kotoran\n(kg)'],
        [brondol,brondolBusuk,dirt],
        ['','',''],
        ['','',''],
        ['','',''],
        ['','',''],
        ['','','']
    ]

    
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

    dataP1 = [['1. KONDISI TBS : ']]
    tblP1 = Table(dataP1,[8*inch])
    tblP1.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTITALIC', (0, 0), (-1, -1), 1),
    ]))

    if mode_app == 'multi-inference':
        name_pdf = './hasil/' + formatted_date + '/' + no_tiket.replace('/','-') + '/result_deteksi.pdf'
    else:
        name_pdf = str(img_dir) +  '.pdf'
    

    if editData:
        name_pdf = str(Path(os.getcwd() + '/hasil/' + formatted_date)) + '/' + str(raw[1].replace('/','_')) + '_' + str(raw[4]) + '_' + str(raw[5]) + '.pdf'
    
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

    HasilParagraph = [['2. Hasil Deteksi AI : ']]
    hasilGrid = Table(HasilParagraph,[8*inch])
    hasilGrid.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTITALIC', (0, 0), (-1, -1), 1),
    ]))

    

    inputTambahan = [['3. Input Tambahan : ']]
    inputGrid = Table(inputTambahan,[8*inch])
    inputGrid.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTITALIC', (0, 0), (-1, -1), 1),
    ]))

    tableInput = Table(TabelInputTambahan, colWidths=colEachTableInput)
    tableInput.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (3, 0), 'MIDDLE'),
        ('ALIGN', (0, 0), (3, 0), 'CENTER'),
        ('GRID', (0, 0), (2, 1), 1, colorPdf.black),
    ]))

    side_by_side_tables = Table([[tableInput, tblQr]], colWidths=[4 * inch, 4.3 * inch])

    elements = []
    elements.append(titleImg)
    elements.append(spacer)
    elements.append(table1)
    elements.append(spacer)
    elements.append(tblP1)
    
    elements.append(tblImg)
    elements.append(spacer)
    elements.append(hasilGrid)
    elements.append(spacer)
    elements.append(table2)
    elements.append(spacer)
    elements.append(inputGrid)
    elements.append(side_by_side_tables)
    elements.append(PageBreak())
    
    doc.build(elements)

def get_list_mill(dir_mill, flag):

    mill_names = []
    if not dir_mill.exists():
        dir_mill.touch()

    with open(dir_mill, 'r') as file:
        mill_names = [line.strip() for line in file]

    if len(mill_names) == 0:
        try:
            response = urlopen(url)
            get_mill_arr = json.loads(response.read())

            print(get_mill_arr)
            mill_names = [f"{data['mill']};{data['ip']}" for data in get_mill_arr]
        except Exception as e:
            print("An error occurred while fetching the server data:", str(e))
       
    
        with open(dir_mill, 'w') as file:
            for data in mill_names:
                file.write(f"{data}\n")

    if flag:
        mill_names = [f"CCTV {index + 1} ({entry.split(';')[1]})" for index, entry in enumerate(mill_names)]
        return mill_names
    
    mill_names = [entry.split(';')[0] for entry in mill_names]


    mill_names = list(set(mill_names))
    return mill_names

def get_mill_ip():

    conn = sqlite3.connect('./db/grading_sampling.db')
    cursor = conn.cursor()

    cursor.execute("SELECT mill, ip FROM cctv")
    records = cursor.fetchall()

    formatted_records = []


    if not records:
        print("No records found in the table.")
    else:
        for record in records:
            formatted_record = f"{record[0]};{record[1]}"
            formatted_records.append(formatted_record)
                

    conn.close()

    return formatted_records

class ConfigFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        conn = sqlite3.connect('./db/grading_sampling.db')
        cursor = conn.cursor()
        cursor.execute("SELECT server, user, password, database FROM config WHERE id = 1")
        record = cursor.fetchone()

        conn.close()

        server, user, password, database = record

        register_label = tk.Label(self, text="Konfigurasi Server Database", font=("Times New Roman", 20, "bold"))
        register_label.grid(row=0, column=0, columnspan=2, sticky='w', pady=(40, 0))

        register_label = tk.Label(self, text="Silakan isi untuk mengganti konfigurasi server sistem!", font=("Times New Roman", 12, "italic"))
        register_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=10)

        user_root = tk.Label(self, text="User Root:")
        user_root.grid(row=2, column=0, sticky="w", pady=5)
        self.useroot_entry = tk.Entry(self)
        self.useroot_entry.grid(row=2, column=1, pady=5, sticky="ew")

        server_label = tk.Label(self, text="Server")
        server_label.grid(row=3, column=0, sticky="w", pady=5)
        self.server_entry = tk.Entry(self )
        self.server_entry.grid(row=3, column=1, pady=5, sticky="ew")
        self.server_entry.insert(0, server)

        database_label = tk.Label(self, text="Database")
        database_label.grid(row=6, column=0, sticky="w", pady=5)
        self.database_entry = tk.Entry(self) 
        self.database_entry.grid(row=6, column=1, sticky="ew")
        self.database_entry.insert(0, database)

        user_label = tk.Label(self, text="User")
        user_label.grid(row=4, column=0, sticky="w", pady=4)
        self.user_entry = tk.Entry(self) 
        self.user_entry.grid(row=4, column=1, sticky="ew")
        self.user_entry.insert(0, user)
    
        password_label = tk.Label(self, text="Password")
        password_label.grid(row=5, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(self) 
        self.password_entry.grid(row=5, column=1, sticky="ew")
        self.password_entry.insert(0, password)

        mill_label = tk.Label(self, text="Mill")
        mill_label.grid(row=7, column=0, sticky="w", pady=5)
        mill_choices = get_list_mill(log_mill, flag=False)
        self.mill_var = tk.StringVar()
        self.mill_combobox = ttk.Combobox(self, textvariable=self.mill_var, values=mill_choices)

        if len(mill_choices) ==1:
            self.mill_var.set(mill_choices[0])
        self.mill_combobox.grid(row=7, column=1, pady=5, sticky="ew")
        
        submit_button = tk.Button(self, text="Submit", command=self.change_config)
        submit_button.grid(row=8, column=0,sticky="w",   pady=(40, 0))
        
        back_button = tk.Button(self, text="Kembali ke Login", command=self.backToLogin)
        back_button.grid(row=8, column=1,sticky="w",   pady=(40, 0))

        self.feedback_label = tk.Label(self, text="", fg="red")
        self.feedback_label.grid(row=9, column=0, columnspan=2, pady=(30, 10))

        self.feedback_label_success = tk.Label(self, text="", fg="green")
        self.feedback_label_success.grid(row=9, column=0, columnspan=2, pady=(30, 10))

    def change_config(self):
        server = self.server_entry.get()
        userRoot = self.useroot_entry.get()
        user = self.user_entry.get()
        password = self.password_entry.get()
        database = self.database_entry.get()
        mill = self.mill_combobox.get()
        if not server or not user or not userRoot or not password or not database or not mill:
                self.feedback_label.config(text="Semua kolom harus diisi", fg="red")
                self.after(3000, self.clear_feedback)
                return  # Stop further execution

        if userRoot == 'grading':

            conn = sqlite3.connect('./db/grading_sampling.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM config WHERE id = 1")
            record_count = cursor.fetchone()[0]

            if record_count == 0:
                cursor.execute("INSERT INTO config (id, mill, server, user, password, database) VALUES (?, ?, ?, ?, ?, ?)",
                            (1, mill, server, user, password, database))
                self.feedback_label_success.config(text="Berhasil Menambahkan Konfigurasi!")
            else:
                # update db config
                cursor.execute("UPDATE config SET mill=?, server=?, user=?, password=?, database=? WHERE id=1",
                            (mill, server, user, password, database))

                url = "https://srs-ssms.com/grading_ai/get_list_mill.php"

                arr = None
                try:
                    response = urlopen(url)
                    arr = json.loads(response.read())
                except Exception as e:
                    print("Anda membutuhkan internet untuk fetching ID mill dari server")

                target_mill = mill  # The mill value you want to find
                found_record = None

                for record in arr:
                    if record.get('mill') == target_mill:
                        found_record = record
                        break

                
                if found_record:
                    # update db cctv
                    other_table_data = (mill, found_record['ip'])
                    cursor.execute("UPDATE cctv SET mill=?, ip=? WHERE id=1", other_table_data)

                    with open(id_mill_dir, 'w') as file:
                        file.write(found_record['id_mill'])

                self.feedback_label_success.config(text="Berhasil Memperbarui Konfigurasi!")

            conn.commit()
            conn.close()
        
        else:
            self.feedback_label.config(text="User Root Salah", fg="red")
            self.after(3000, self.clear_feedback)
            

    def clear_feedback(self):
        if self.feedback_label.winfo_exists():
            self.feedback_label.config(text="")

        elif self.feedback_label_success.winfo_exists():
            self.feedback_label_success.config(text="")

    def toggle_password_visibility(self, event=None):
        current_show_value = self.password_entry.cget("show")
        if current_show_value == "":
            # Currently showing password, so hide it
            self.password_entry.config(show="*")
        else:
            # Currently hiding password, so show it
            self.password_entry.config(show="")

    def backToLogin(self):
        self.master.switch_frame(LoginFrame)


class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        login_label = tk.Label(self, text="Login", font=("Times New Roman", 20, "bold"))
        login_label.grid(row=0, column=0, columnspan=2, sticky='w', pady=(40, 0))

        login_label = tk.Label(self, text="Masukkan user dan password untuk mengakses sistem!", font=("Times New Roman", 12, "italic"))
        login_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=10)

        username_label = tk.Label(self, text="Username:")
        username_label.grid(row=2, column=0, sticky="w", pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=2, column=1, pady=5, sticky="ew")

        password_label = tk.Label(self, text="Password:")
        password_label.grid(row=3, column=0, sticky="w")
        self.password_entry = tk.Entry(self, show="*") 
        self.password_entry.grid(row=3, column=1, pady=5, sticky="ew")


        self.feedback_label = tk.Label(self, text="", fg="red")
        self.feedback_label.grid(row=7, column=0, columnspan=2, pady=(30, 10))

        register_label = tk.Label(self, text="Belum memiliki akun ?", font=("Times New Roman", 12, "italic"), fg="blue", cursor="hand2")
        register_label.grid(row=5, column=0, columnspan=2, sticky="e")
        register_label.bind("<Button-1>", self.register_clicked)
        
        login_button = tk.Button(self, text="Login", command=self.login)
        login_button.grid(row=6, column=0, columnspan=2, sticky="w", pady=(40, 0))

        login_button = tk.Button(self, text="Config Server", command=self.config_server)
        login_button.grid(row=6, column=1, columnspan=2, sticky="w", pady=(40, 0))

        self.password_entry.bind("<Return>", lambda event: self.login())

    def clear_feedback(self):
        if self.feedback_label.winfo_exists():
            self.feedback_label.config(text="")

    def register_clicked(self, event):
        self.master.switch_frame(RegisterFrame)

    def config_server(self):
        self.master.switch_frame(ConfigFrame)

    def login(self):
        user = self.username_entry.get()
        password = self.password_entry.get()

        conn = sqlite3.connect('./db/grading_sampling.db')
        cursor = conn.cursor()

        cursor.execute("SELECT user, password FROM auth WHERE user = ?", (user,))
        user_data = cursor.fetchone()

        if user_data:
            stored_user, stored_password = user_data
            stored_password = stored_password.encode('utf-8')

            if stored_user == user and bcrypt.checkpw(password.encode('utf-8'), stored_password):
                print("Login successful. Welcome,", user)
                self.master.switch_frame(Frame1)
            else:
                print("Login failed. Invalid credentials.")
                self.feedback_label.config(text="Incorrect password", fg="red")
        else:
            print("User not found.")
            self.feedback_label.config(text="User not found", fg="red")
        conn.close()

        self.after(3000, self.clear_feedback)


class RegisterFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        register_label = tk.Label(self, text="Register New User", font=("Times New Roman", 20, "bold"))
        register_label.grid(row=0, column=0, columnspan=2, sticky='w', pady=(40, 0))

        register_label = tk.Label(self, text="Silakan isi untuk menambahkan user ke sistem!", font=("Times New Roman", 12, "italic"))
        register_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=10)

        user_root = tk.Label(self, text="User Root:")
        user_root.grid(row=2, column=0, sticky="w", pady=5)
        self.useroot_entry = tk.Entry(self)
        self.useroot_entry.grid(row=2, column=1, pady=5, sticky="ew")

        username_label = tk.Label(self, text="Username:")
        username_label.grid(row=3, column=0, sticky="w", pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=3, column=1, pady=5, sticky="ew")

        password_label = tk.Label(self, text="Password:")
        password_label.grid(row=4, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(self, show="*") 
        self.password_entry.grid(row=4, column=1, sticky="ew")
        
        register_button = tk.Button(self, text="Submit", command=self.register)
        register_button.grid(row=5, column=0,sticky="w",   pady=(40, 0))
        
        register_button = tk.Button(self, text="Kembali ke Login", command=self.backToLogin)
        register_button.grid(row=5, column=1,sticky="w",   pady=(40, 0))

        self.feedback_label = tk.Label(self, text="", fg="green")
        self.feedback_label.grid(row=6, column=0, columnspan=2, pady=(30, 10))

        self.feedback_label_success = tk.Label(self, text="", fg="red")
        self.feedback_label_success.grid(row=6, column=0, columnspan=2, pady=(30, 10))

    def backToLogin(self):
            self.master.switch_frame(LoginFrame)

    def clear_feedback(self):
        if self.feedback_label.winfo_exists():
            self.feedback_label.config(text="")

        elif self.feedback_label_success.winfo_exists():
            self.feedback_label_success.config(text="")

    def register(self):
            userRoot = self.useroot_entry.get()
            user = self.username_entry.get()
            password = self.password_entry.get()

            if not user or not password or not userRoot:
                self.feedback_label.config(text="Semua kolom harus diisi", fg="red")
                self.after(3000, self.clear_feedback)
                return  # Stop further execution

            if userRoot == 'grading':
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                conn = sqlite3.connect('./db/grading_sampling.db')
                cursor = conn.cursor()

                cursor.execute("SELECT user FROM auth WHERE user = ?", (user,))
                existing_user = cursor.fetchone()
                if existing_user:
                    print('User already exists!')
                    self.feedback_label.config(text="User tersebut sudah terdaftar", fg="red")
                else:
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                    cursor.execute("INSERT INTO auth (user, password) VALUES (?, ?)", (user, hashed_password.decode('utf-8')))

                    conn.commit()

                    print('User registered successfully')
                    self.feedback_label_success.config(text="User baru tersimpan", fg="green")

                conn.close()
            else:    
                print('Tidak dapat menyimpan User!')
                self.feedback_label.config(text="Tidak dapat menyimpan User!", fg="red")

def process_data_offline( data):
        arr_data = []
        index = 1
        for item in data:
            item_dict = eval(item)
            extracted_data = [
                index,
                item_dict.get('no_tiket', ''),
                item_dict.get('no_plat', ''),
                item_dict.get('nama_driver', ''),
                item_dict.get('bunit', ''),
                item_dict.get('divisi', ''),
                item_dict.get('blok', ''),
                item_dict.get('bunches', ''),
                item_dict.get('ownership', ''),
                item_dict.get('waktu_input', ''),
                item_dict.get('status_inference', ''),
            ]

            arr_data.append(extracted_data)
            index +=1
        sorted_data = sorted(arr_data, key=lambda x: x[9])
        return sorted_data
        
def copy_img_edit_mode(tiket):
        path_img = str(Path(os.getcwd() + '/hasil/' + formatted_date + '/'))
        
        files = os.listdir(path_img)

        WBTicketNo_modified = tiket.replace('/', '_')

        # Filter out only the image files (you can adjust the list of valid extensions as needed)
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

        # Remove "_best" or "_worst" dynamically while maintaining the original casing
        cleaned_filenames = [
            file.rsplit('best', 1)[0].rsplit('worst', 1)[0]  # remove both "best" and "worst"
            for file in files if any(file.lower().endswith(ext) for ext in image_extensions)
        ]
        found_files = [cleaned_file for cleaned_file in cleaned_filenames if WBTicketNo_modified in cleaned_file]
        img_dir = ''
        if found_files:
            for found_file in found_files:
                img_dir = str(path_img)  + '/' + found_file

        return img_dir

def info_truk(tiket, plat, driver, unit, divisi, blok, bunches, ownership,  status_inference):
    keyInfoTruk =  ['no_tiket', 'no_plat', 'nama_driver', 'bunit','divisi','blok','bunches', 'ownership', 'status_inference']
    valInfoTruk = [tiket, plat, driver, unit, divisi, blok, bunches, ownership, status_inference]

    return dict(zip(keyInfoTruk, valInfoTruk))

def connect_to_database():
    global status_mode
    
    try:
        conn = sqlite3.connect('./db/grading_sampling.db')
        cursor = conn.cursor()
        cursor.execute("SELECT server, user, password, database FROM config WHERE id = 1")
        record = cursor.fetchone()
        conn.close()

        server, user, password, database = record
        
        timeout = 2
        def try_connect():
            global connection
            try:
                connection = pymssql.connect(
                    server=server,
                    user=user,
                    password=password,
                    database=database,
                    as_dict=True
                )

            except Exception as e:
                # print(f"Error connecting to the database: {str(e)}")
                print(f"Error connecting to the database")
                connection = None
                 
        connection_thread = threading.Thread(target=try_connect)
        connection_thread.start()

        connection_thread.join(timeout)
        
        if isinstance(connection, pymssql.Connection):
            status_mode = 'online'
            return  connection
        else:
            status_mode = 'offline'
            with open(offline_log_dir, 'r') as file:
                    data = file.readlines()
                    return process_data_offline(data)

    except Exception as e:
        status_mode = 'offline'
        with open(offline_log_dir, 'r') as file:
                data = file.readlines()
                print(data)
                return process_data_offline(data)

source = None  # Initialize source to None initially
class Frame1(tk.Frame):
    
   

    def __init__(self, master):
        super().__init__(master)
        global source
        self.clicked_buttons = []
        
        self.make_tree()

        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky='ew')

        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_columnconfigure(2, weight=200)
        top_frame.grid_columnconfigure(3, weight=20)
        top_frame.grid_columnconfigure(4, weight=20)
        self.top_frame = top_frame
        self.refresh_data()
        
        self.title_label = tk.Label(top_frame, text=f"TABEL LIST TRUK FFB GRADING PER TRUK {get_list_mill(log_mill,flag=False)[0]}", font=("Helvetica", 16, "bold"))
        self.title_label.grid(row=0, column=2)
        self.logo_image = tk.PhotoImage(file=Path(os.getcwd() + '/default-img/Logo-CBI(4).png'))  # Replace "logo.png" with your image file path
        self.logo_image = self.logo_image.subsample(2, 2)  # Adjust the subsample values to resize the image
        logo_label = tk.Label(top_frame, image=self.logo_image)
        logo_label.grid(row=0, column=0)

        self.logo_image2 = tk.PhotoImage(file=Path(os.getcwd() + '/default-img/LOGO-SRS(1).png'))
        self.logo_image2 = self.logo_image2.subsample(2, 2)
        logo_label2 = tk.Label(top_frame, image=self.logo_image2)
        logo_label2.grid(row=0, column=1)  # Change column to 0 and sticky to "ne"

        self.mill_var = tk.StringVar()
        cctv_choices = get_mill_ip()
        cctv_choices.append('Video - Test')
        self.cctv_combobox = ttk.Combobox(self, textvariable=self.mill_var, values=cctv_choices)
        self.mill_var.set(cctv_choices[0])
        source = self.mill_var.get()
        self.cctv_combobox.grid(row=0, column=5)

        self.cctv_combobox.bind("<FocusOut>", self.on_combobox_focus_out)

        # self.mode_label = tk.Label(top_frame, text="", font=("Helvetica", 16, "bold"))
        # self.mode_label.grid(row=0, column=3)

        self.refresh_button = ttk.Checkbutton(top_frame, text="EDIT DATA", variable=tk.IntVar(value=1), style="ToggleButton", command=self.password_frame)
        self.refresh_button.grid(row=0, column=5)
        
        self.refresh_button = ttk.Checkbutton(top_frame, text="REFRESH", variable=tk.IntVar(value=1), style="ToggleButton", command=self.refresh_data)
        self.refresh_button.grid(row=0, column=6)       
        
        top_frame.grid_columnconfigure(6, weight=20)

        
        # self.button_input = ttk.Button(top_frame, text="Input Data Truk", style="Accent.TButton", command=self.switch_frame2)
        # self.button_input.grid(row=0, column=5)
        

        self.tree.grid(row=1, column=0, columnspan=6, sticky="nsew")  # Use columnspan to span all columns

        self.footer_frame = tk.Frame(self)
        self.footer_frame.grid(row=2, column=0, columnspan=6, sticky="ew", pady=40)  # Use columnspan to span all columns

        footer_label = tk.Label(self.footer_frame, text="Copyright @ Digital Architect SRS 2023", font=("Helvetica", 14, "bold"))
        footer_label.pack()

        self.last_update_model = tk.Frame(self)
        self.last_update_model.grid(row=2, column=0, columnspan=3, sticky="nw", pady=10)  # Use columnspan to span all columns

        last_model = tk.Label(self.last_update_model, text="Tanggal Update Model AI : 08 Agustus 2023",font=("Helvetica", 12, "italic"))
        last_model.pack()
                
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.running_script = False  # Flag to track if script is running

    def make_tree(self):
        self.tree = ttk.Treeview(self, columns=columns, selectmode="none", show="headings")
        self.style = ttk.Style(self)
        self.row_height = 100  # Set the desired row height
        self.detail_window = None

        self.style.configure("Treeview", rowheight=self.row_height)
        self.tree.heading("#1", text="No")
        self.tree.heading("#2", text="NOMOR TIKET")
        self.tree.heading("#3", text="NOMOR POLISI")
        self.tree.heading("#4", text="NAMA DRIVER")
        self.tree.heading("#5", text="BISNIS UNIT")
        self.tree.heading("#6", text="DIVISI")
        self.tree.heading("#7", text="FIELD")
        self.tree.heading("#8", text="BUNCHES")
        self.tree.heading("#9", text="OWNERSHIP")
        self.tree.heading("#10", text="PUSH TIME")
        self.tree.heading("#11", text="ACTION")
        
        # Adjust column widths
        self.tree.column("no", width=50)         
        self.tree.column("notiket", width=250) 
        self.tree.column("nopol", width=100, anchor="center") 
        self.tree.column("driver") 
        self.tree.column("b_unit") 
        self.tree.column("divisi") 
        self.tree.column("field") 
        self.tree.column("bunches", width=70) 
        self.tree.column("ownership", anchor="center") 
        self.tree.column("pushtime", anchor="center") 
        self.tree.column("action", anchor="center") 
    def password_frame(self):
        
        password_overlay = tk.Toplevel(self.master)
        password_overlay.title("Konfirmasi")
        
        # Set the size of the overlay frame
        overlay_width = 200
        overlay_height = 200
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - overlay_width) // 2
        y = (screen_height - overlay_height) // 2
        password_overlay.geometry(f"{overlay_width}x{overlay_height}+{x}+{y}")
        
        # Create a frame within the Toplevel for grid placement
        password_frame = ttk.Frame(password_overlay)
        password_frame.grid(row=0, column=0, padx=10, pady=10)

        # Example: Add a Submit button
        label_button = ttk.Label(password_frame, text="Password Root")
        label_button.grid(row=0, column=0, padx=10, pady=10)
        
        # Example: Add an Entry widget for password input
        self.password_entry = ttk.Entry(password_frame, show="*")  # Use show="*" to hide the password characters
        self.password_entry.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")  # Center vertically with sticky
        
        # Example: Add a Submit button
        submit_button = ttk.Button(password_frame, text="SUBMIT", command=lambda: self.switch_frame_edit_data(password_overlay))
        submit_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.feedback_label = tk.Label(password_frame, text="", fg="red")
        self.feedback_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)


    def switch_frame_edit_data(self, password_overlay):
        
        password = self.password_entry.get()

        if password == 'grading':
            password_overlay.destroy()
            self.master.switch_frame(EditBridgeFrame)
        else:
            self.feedback_label.config(text="Error Password Root!", fg="red")

        self.after(3000, self.clear_feedback)
        
    def clear_feedback(self):
        if self.feedback_label.winfo_exists():
            self.feedback_label.config(text="")

    def on_combobox_focus_out(self, event):
        global source  # Declare 'source' as a global variable
        selected_value = self.mill_var.get()
        self.selected_combobox_value = selected_value  # Store the selected value in a class variable
        
        # Update 'source' to the current combobox value
        source = selected_value


    def populate_treeview(self, arrData):
        
        custom_font = tkFont.Font(family="Helvetica", size=11)
        # print(arrData)
        for i, data in enumerate(arrData, start=1):
            item = self.tree.insert("", "end", values=data, tags=i)
            self.tree.set(item, "#1", str(i))
            if status_mode == 'offline':
                self.tree.set(item, "#8", '')
                
            status_inference = data[10]
            if status_inference == None or status_inference == 'None':
                self.tree.set(item, "#11", "READY")
                self.tree.tag_configure(i, background="#FFFFFF", font=custom_font)
            else:
                self.tree.tag_configure(i, background="#94c281", font=custom_font)
                self.tree.set(item, "#11", "Done")
            self.tree.tag_bind(i, "<Double-Button-1>", lambda event, row_item=item: self.update_row(row_item, event))     

    def pull_master(self, connection,  table, code, name, file_name):

        if isinstance(connection, pymssql.Connection):
            sql_query = f"SELECT {str(code)} , {str(name)}  FROM {str(table)} WHERE AI_pull_time IS NULL"
            cursor = connection.cursor()
            cursor.execute(sql_query)
            records = cursor.fetchall()
            # connection.close()
            
            if len(records) > 0 or not file_name.exists():
                sql_query = f"SELECT {str(code)} , {str(name)}  FROM {str(table)}"
                # connection = connect_to_database()  
                cursor = connection.cursor()
                cursor.execute(sql_query)
                records = cursor.fetchall()
                # connection.close()
                mapping = {r[str(code)]: r[str(name)] for r in records}
                
                file_name.touch()
                with open(file_name, 'w') as file:
                    for code, name in mapping.items():
                        file.write(f"{code}:{name}\n")
                # connection = connect_to_database()
                update_query = f"UPDATE {str(table)} SET AI_pull_time = GETDATE() WHERE AI_pull_time IS NULL"
                cursor = connection.cursor()
                try:
                    cursor.execute(update_query)
                    connection.commit()  # Commit the transaction                
                except Exception as e:
                    connection.rollback()  # Rollback the transaction in case of an error
                    print(f"Error executing update query: {str(e)}")
                # connection.close()
                return mapping
            else:
                mapping = {}
                with open(file_name, 'r') as file:
                    lines = file.readlines()
                    for line in lines:
                        code, name = line.strip().split(':')
                        mapping[int(code)] = name
                return mapping

        else:
            return connection

    def pull_data_ppro(self, connection, date_today=None):
        # start_date = datetime.datetime(2023, 10, 30, 7, 0, 0)
        current_date = datetime.datetime.now().date()
        start_time = datetime.time(7, 0, 0)
        start_date = datetime.datetime.combine(current_date, start_time)
        
        end_date = start_date + datetime.timedelta(days=1)

        if date_today != None:
            tommorow = date_today + datetime.timedelta(days=1)
        
        # connection = connect_to_database()
        
        if isinstance(connection, pymssql.Connection):
            sql_query = "SELECT * FROM MOPweighbridgeTicket_Staging WHERE Ppro_push_time >= %s AND Ppro_push_time < %s"
            if date_today:
                sql_query += " AND AI_pull_time >= %s AND AI_pull_time < %s"
             
            cursor = connection.cursor()
            if date_today:
                cursor.execute(sql_query, (start_date, end_date, date_today, tommorow))
            else:
                cursor.execute(sql_query, (start_date, end_date))
            records = cursor.fetchall()
            # connection.close()
            return records
        else:
            return connection

    def process_data(self, record, master_bunit, master_div, master_block):
        arr_data = []
        for index, data in enumerate(record):

            bunit = data['BUnitCode']
            if bunit != 'None':
                ppro_bunit_name = master_bunit.get(bunit, bunit)
            else:
                ppro_bunit_name = bunit

            div = data['DivisionCode']
            if div != 'None':
                ppro_div_name = master_div.get(div, div)
            else:
                ppro_div_name = div

            block = data['Field']
            if block != 'None':
                ppro_block_name = master_block.get(block, block)
            else:
                ppro_block_name = block

            try:
                # Parse the input string into a datetime object
                input_datetime = dt.strptime(str(data['Ppro_push_time']), "%Y-%m-%d %H:%M:%S.%f")

                # Format the datetime object as a string in the desired format
                output_datetime_str = input_datetime.strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                print(f"Error executing update query 2: {str(e)}")
                output_datetime_str = str(data['Ppro_push_time'])
            try:
                ai_pull_time = data['AI_pull_time']
            except Exception as e:
                print(f"Error getting AI PULL TIME: {str(e)}")
                ai_pull_time = "None"

            found = False
            idx = 0

            for idk, item in enumerate(arr_data):
                if data['WBTicketNo'] in item:
                    found = True
                    idx = idk
                    break

            if not found:
                arr_data.append([
                    str(index+1),
                    data['WBTicketNo'],
                    data['VehiclePoliceNO'],
                    data['DriverName'],
                    ppro_bunit_name,
                    ppro_div_name,
                    ppro_block_name,
                    data['Bunches'],
                    data['Ownership'],
                    output_datetime_str,
                    ai_pull_time
                ])
            else:
                arr_data[idx][6] = str(arr_data[idx][6]) + "\n" + str(ppro_block_name)
                arr_data[idx][7] = int(arr_data[idx][7]) + int(data['Bunches'])   

        

        sorted_data = sorted(arr_data, key=lambda x: x[9], reverse=True)
        
        return sorted_data

    def remove_input_button(self):
        if hasattr(self, 'button_input'):
            self.button_input.grid_remove()

    def create_and_grid_input_button(self):
        if hasattr(self, 'button_input'):
            self.button_input.grid_remove()  # Remove the button if it already exists

        self.button_input = ttk.Button(self.top_frame, text="INPUT DATA TRUK", style="Accent.TButton", command=self.switch_frame2)
        self.button_input.grid(row=0, column=4)

    def refresh_data(self):
        self.tree.delete(*self.tree.get_children())

        database_connection = connect_to_database()
        master_bunit = self.pull_master(database_connection, 'MasterBunit_Staging', 'Ppro_BUnitCode', 'Ppro_BUnitName', data_bunit)
        master_div = self.pull_master(database_connection, 'MasterDivisi_Staging', 'Ppro_DivisionCode', 'Ppro_DivisionName', data_div)
        master_block = self.pull_master(database_connection, 'MasterBlock_Staging', 'Ppro_FieldCode', 'Ppro_FieldName', data_block)
        record = self.pull_data_ppro(database_connection)
        if status_mode == 'online':
            database_connection.close()
        self.master.title(f"Sistem Aplikasi Pos Grading - {status_mode.capitalize()} - {mode_app.capitalize()}")
        if status_mode == 'online':
            arr_data = self.process_data(record, master_bunit, master_div, master_block)

            self.refresh_button = ttk.Checkbutton(self.top_frame, text="EDIT DATA", variable=tk.IntVar(value=1), style="ToggleButton", command=self.password_frame)
            self.refresh_button.grid(row=0, column=5)
            
            self.refresh_button = ttk.Checkbutton(self.top_frame, text="REFRESH", variable=tk.IntVar(value=1), style="ToggleButton", command=self.refresh_data)
            self.refresh_button.grid(row=0, column=6)

            self.remove_input_button()
        else:
            arr_data = record
            self.create_and_grid_input_button()
        self.populate_treeview(arr_data)
    
    def update_row(self, row_item, event):
        row_id = int(self.tree.item(row_item, "tags")[0])  # Get row ID from tags

        column = self.tree.identify_column(event.x)  # Identify the column clicked
        status_row = self.tree.item(row_item, "values")[-1]
        row_values = self.tree.item(row_item, "values")  # Get values of the row
        # Extract the column name from the column identifier
        column = column.split("#")[-1]
        #print(self.clicked_buttons)
        for cb in self.clicked_buttons:
            
            self.tree.tag_configure(cb, background="#ffffff")  # Change row color
            self.clicked_buttons.remove(cb)
        
        #print("column:" + str(column) + "|columns:"+ str(len(columns)))
        if status_row == "READY" and row_id not in self.clicked_buttons and not self.running_script:

            self.tree.tag_configure(row_id, background=accent2)  # Change row color
            self.clicked_buttons.append(row_id)

            if int(column) == len(columns):

                confirmation = messagebox.askyesno("Konfirmasi", f"Apakah baris SPB nomor {row_values[0]} ini sudah benar dan siap untuk dijalankan ?")
                if confirmation:
                                
                    self.running_script = True  # Set flag to indicate script is running

                    thread = threading.Thread(target=self.run_script, args=(row_item, row_id, row_values))
                    thread.start()
        else:
            if int(column) == len(columns):
                row_val = self.tree.item(row_item, "values")
                
                tiket = str(row_val[1].replace("/", "_"))
                bunit = str(row_val[4]).replace(' ','')
                div = str(row_val[5])
                pdf_path = str(Path(os.getcwd() + '/hasil/' + formatted_date)) + '/'  + tiket+ '_' + bunit + '_' + div + '_' +'.pdf'
                
                if os.path.exists(pdf_path) and os.access(pdf_path, os.R_OK):
                    try:
                        subprocess.Popen(["xdg-open", pdf_path])
                    except Exception as e:
                        print(f"Error opening PDF: {e}")
                else:
                    bunit = str(row_val[4])
                    pdf_path = str(Path(os.getcwd() + '/hasil/' + formatted_date)) + '/'  + tiket+ '_' + bunit + '_' + div + '_' +'.pdf'
                    print(pdf_path)
                    try:
                        subprocess.Popen(["xdg-open", pdf_path])
                    except Exception as e:
                        print(f"Error opening PDF: {e}")
                        messagebox.showinfo("Alert", f"File Tidak dapat ditemukan")  # Show success message


    def run_script(self, row_item, row_id, row_values):
        
        if mode_app == 'multi-inference':
            tiket = row_values[1].replace('/','-')
            path_avg_cctv = Path(os.getcwd() + '/hasil/' + formatted_date  + '/' + tiket)
            path_avg_cctv.mkdir(parents=True, exist_ok=True)  # make dir
        
        global source, date_start_conveyor
        date_start_conveyor = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output_inference = None
        try:
            if mode_app == 'multi-inference':
                result = subprocess.run(['python', 'multiple_inference.py', '--tiket', str(tiket), '--mode', 'multi-inference'], 
                                capture_output=True, 
                                text=True, 
                                check=True)
            else:
                result = subprocess.run(['python', '9-track-master.py', '--pull_data', str(row_values), '--source', str(source)], 
                            capture_output=True, 
                            text=True, 
                            check=True)

            output_inference = result.stdout
     
        except subprocess.CalledProcessError as e:
            print("Error running other_script.py:", str(e))

        if output_inference:
            self.master.switch_frame(Frame3, output_inference, row_values)
        else:
            self.running_script = False
            self.refresh_button.config(state=tk.NORMAL)  # Enable the button

    def switch_frame2(self):
        self.master.switch_frame(Frame2)

WBTicketNo = None
totalJjg = 0
class Frame3(tk.Frame):
    
    def __init__(self, master, output_inference, row_values):
        super().__init__(master)

        self.master.title(f"Sistem Aplikasi Pos Grading - {status_mode.capitalize()} - {mode_app.capitalize()}")

        counter_per_class = None
        img_dir = None
        raw = None
        tiket_folder = None
        global WBTicketNo 
        global totalJjg
        self.submit_clicked = False
        
        with open(save_dir_txt,  'r') as file:
            raw = file.readline()
            

        if mode_app == 'multi-inference':
            tiket_folder = raw
            folder_inference = Path(os.getcwd() + '/hasil/' + formatted_date + '/' + tiket_folder + '/' + 'result_average_hasil_cctv.TXT')
            
            with open(folder_inference, 'r') as file:
                content = file.read()

            # Use ast.literal_eval to safely parse the content
            hasil_deteksi = ast.literal_eval(content)    

            class_name = list(hasil_deteksi.keys())
            counter_per_class = list(hasil_deteksi.values())   
        else:
            parts = raw.split('$')

            parts = [part.strip() for part in parts]

            counter_per_class = eval(parts[0])

            class_name = eval(parts[1])
            img_dir = parts[2]

        filtered_list = [counter_per_class[i] for i in range(len(counter_per_class)) if i != 5]

        totalJjg = sum(filtered_list)
        # if output_inference is not None:
        #     print(output_inference)
        
        try:
            image_path = self.check_img(img_dir)
        except Exception as e:
            print(f"Error loading and displaying image: {e}")
        
        self.image_best = tk.Label(self)
        self.image_best.grid(row=0, column=0, rowspan=27, padx=(0, 60), pady=(100,100))

        width, height = 950, 700  # Set your desired width and height
        
        try:
            # Open the image using PIL
            original_image = Image.open(image_path)
            border_width = 10  # Adjust the border width as needed
            border_color = "#cccdce"  # Set the border color (in RGB, here it's red)
            bordered_image = ImageOps.expand(original_image, border=border_width, fill=border_color)

            # Resize the image to the specified width and height using LANCZOS resampling
            resized_image = bordered_image.resize((width, height), Image.LANCZOS)

            #   Convert the resized PIL image to a Tkinter PhotoImage
            photo = ImageTk.PhotoImage(resized_image)

            # Set the PhotoImage as the image for the Label widget
            self.image_best.config(image=photo)
            self.image_best.image = photo  # Keep a reference to prevent garbage collection

        except Exception as e:
            print(f"Error loading and displaying image: {e}")

        WBTicketNo = row_values[1] if row_values else ''
        VehiclePoliceNO = row_values[2]if row_values else ''
        DriverName = row_values[3]if row_values else ''
        BUnit = row_values[4]if row_values else ''
        Divisi = row_values[5]if row_values else ''
        Field = row_values[6]if row_values else ''
        Bunches = row_values[7]if row_values else ''
        Ownership = row_values[8]if row_values else ''
        push_time = row_values[9]if row_values else ''
        statusInference = row_values[10]if row_values else ''

        info_truk_dict = info_truk(WBTicketNo, VehiclePoliceNO, DriverName, BUnit, Divisi, Field, Bunches, Ownership, statusInference)

        title_label = tk.Label(self, text="Rekap Data Deteksi FFB Grading dengan AI ", font=("Helvetica", 19, "bold"))
        title_label.grid(row=0, column=1, columnspan=5, pady=(100,0))

        subtitle1 = tk.Label(self, text="Informasi Truk : ",  font=("Helvetica", 13, "italic "))
        subtitle1.grid(row=1, column=1,columnspan=4, sticky="w")

        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=2, column=1, columnspan=4, sticky="ew")
        
        label1 = tk.Label(self, text="Nomor Tiket : ")
        label1.grid(row=3, column=1, sticky="w")

        param_label1 = tk.Label(self, text=WBTicketNo)
        param_label1.grid(row=3, column=2,sticky="w")

        label2 = tk.Label(self, text="Nomor Polisi : ")
        label2.grid(row=3, column=3, sticky="w")

        param_label2 = tk.Label(self, text=VehiclePoliceNO)
        param_label2.grid(row=3, column=4,sticky="w")

       
        label3 = tk.Label(self, text="Nama Driver : ")
        label3.grid(row=4, column=1, sticky="w")

       
        param_label3 = tk.Label(self, text=DriverName)
        param_label3.grid(row=4, column=2,sticky="w")

        label4 = tk.Label(self, text="Bisnis Unit : ")
        label4.grid(row=4, column=3, sticky="w")

       
        param_label4 = tk.Label(self, text=BUnit)
        param_label4.grid(row=4, column=4,sticky="w")

       
        label5 = tk.Label(self, text="Divisi : ")
        label5.grid(row=5, column=1, sticky="w")

        param_label5 = tk.Label(self, text=Divisi)
        param_label5.grid(row=5, column=2,sticky="w")

        label6 = tk.Label(self, text="Field : ")
        label6.grid(row=5, column=3, sticky="w")

        param_label6 = tk.Label(self, text=Field)
        param_label6.grid(row=5, column=4, sticky="w")

        label7 = tk.Label(self, text="Bunches : ")
        label7.grid(row=6, column=1, sticky="w")

        param_label7 = tk.Label(self, text=Bunches)
        param_label7.grid(row=6, column=2, sticky="w")

        label8 = tk.Label(self, text="Ownership : ")
        label8.grid(row=6, column=3, sticky="w")

        param_label8 = tk.Label(self, text=Ownership)
        param_label8.grid(row=6, column=4,sticky="w")

        label9 = tk.Label(self, text="Pull Time : ")
        label9.grid(row=7, column=1, sticky="w")

        param_label9 = tk.Label(self, text=push_time)
        param_label9.grid(row=7, column=2,sticky="w")
        

        subtitle2 = tk.Label(self, text="Hasil Deteksi Per Kategori : ",  font=("Helvetica", 13, "italic "))
        subtitle2.grid(row=8, column=1,columnspan=4, sticky="w")

        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=9, column=1, columnspan=4, sticky="ew")
        
        label9 = tk.Label(self, text="Total Janjang : ")
        label9.grid(row=10, column=1, sticky="w")

        param_label9 = tk.Label(self, text=str(totalJjg))
        param_label9.grid(row=10, column=2, sticky="w")

        label10 = tk.Label(self, text=f"{class_name[0]} :")
        label10.grid(row=10, column=3, sticky="w")

        if counter_per_class and len(counter_per_class) > 0:
            param_label10 = tk.Label(self, text=counter_per_class[0])
        else:
            param_label10 = tk.Label(self, text="N/A")  # Provide a default value when count_per_class is empty or None
        param_label10.grid(row=10, column=4,  sticky="w")

        label11 = tk.Label(self, text=f"{class_name[1]} :")
        label11.grid(row=11, column=1, sticky="w")

        if counter_per_class and len(counter_per_class) > 1:
            param_label11 = tk.Label(self, text=counter_per_class[1])
        else:
            param_label11 = tk.Label(self, text="N/A")  # Provide a default value when count_per_class is empty or has less than 2 elements
        param_label11.grid(row=11, column=2, sticky="w")

        label12 = tk.Label(self, text=f"{class_name[2]} :")
        label12.grid(row=11, column=3, sticky="w")

        if counter_per_class and len(counter_per_class) > 2:
            param_label12 = tk.Label(self, text=counter_per_class[2])
        else:
            param_label12 = tk.Label(self, text="N/A")  # Provide a default value when counter_per_class is empty or has less than 3 elements
        param_label12.grid(row=11, column=4,  sticky="w")

        label13 = tk.Label(self, text=f"{class_name[3]} :")
        label13.grid(row=12, column=1, sticky="w")

        if counter_per_class and len(counter_per_class) > 2:
            param_label13 = tk.Label(self, text=counter_per_class[3])
        else:
            param_label13 = tk.Label(self, text="N/A")  # Provide a default value when counter_per_class is empty or has less than 3 elements
        param_label13.grid(row=12, column=2,  sticky="w")

        label14 = tk.Label(self, text=f"{class_name[4]} :")
        label14.grid(row=12, column=3, sticky="w")

        if counter_per_class and len(counter_per_class) > 2:
            param_label12 = tk.Label(self, text=counter_per_class[4])
        else:
            param_label12 = tk.Label(self, text="N/A")  # Provide a default value when counter_per_class is empty or has less than 3 elements
        param_label12.grid(row=12, column=4,  sticky="w")

        label15 = tk.Label(self, text=f"{class_name[5]} :")
        label15.grid(row=13, column=1, sticky="w")

        if counter_per_class and len(counter_per_class) > 2:
            param_label12 = tk.Label(self, text=counter_per_class[5])
        else:
            param_label12 = tk.Label(self, text="N/A")  # Provide a default value when counter_per_class is empty or has less than 3 elements
        param_label12.grid(row=13, column=2,  sticky="w")

        label16 = tk.Label(self, text=f"{class_name[6]} :")
        label16.grid(row=13, column=3, sticky="w")

        if counter_per_class and len(counter_per_class) > 2:
            param_label12 = tk.Label(self, text=counter_per_class[6])
        else:
            param_label12 = tk.Label(self, text="N/A")  # Provide a default value when count_per_class is empty or has less than 3 elements
        param_label12.grid(row=13, column=4,  sticky="w")

        subtitle3 = tk.Label(self, text="Input Tambahan : ",  font=("Helvetica", 13, "italic "))
        subtitle3.grid(row=14, column=1,columnspan=4, sticky="w")

        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=15, column=1, columnspan=4, sticky="ew")

        label17 = tk.Label(self, text="Brondolan : ")
        label17.grid(row=16, column=1, sticky="w")

        self.brondolanEntry = tk.Entry(self)
        self.brondolanEntry.grid(row=16, column=2, sticky="w")

        unit_label = tk.Label(self, text="kg")
        unit_label.grid(row=16, column=3, sticky="w")

        label18 = tk.Label(self, text="Brondolan Busuk : ")
        label18.grid(row=17, column=1, sticky="w")

        self.brondoalBusukEntry = tk.Entry(self)
        self.brondoalBusukEntry.grid(row=17, column=2, sticky="w")

        unit_label = tk.Label(self, text="kg")
        unit_label.grid(row=17, column=3, sticky="w")

        label19 = tk.Label(self, text="Dirt/Kotoran : ")
        label19.grid(row=18, column=1, sticky="w")

        self.dirtEntry = tk.Entry(self)
        self.dirtEntry.grid(row=18, column=2,  sticky="w")

        unit_label = tk.Label(self, text="kg")
        unit_label.grid(row=18, column=3, sticky="w")
        
        if status_mode == 'online':
            submit_button = tk.Button(self, text="SUBMIT", command=lambda: self.save_and_switch(class_name, counter_per_class, row_values,info_truk_dict, img_dir))
        else:
            submit_button = tk.Button(self, text="SUBMIT", command=lambda: self.save_offline_and_switch(class_name, counter_per_class, row_values[1:-1], row_values,info_truk_dict, img_dir))
        
        submit_button.grid(row=19, column=1, columnspan=4, sticky="ew")

        self.bind("<Destroy>", lambda event: self.on_close(event, class_name, counter_per_class, row_values,info_truk_dict, img_dir))

    def on_close(self, event, class_name, counter_per_class, row_values, info_truk_dict,img_dir ):
        global isClosedFrame3

        isClosedFrame3 = True

        if not self.submit_clicked:
            if status_mode == 'online':
                self.save_and_switch(class_name, counter_per_class, row_values,info_truk_dict, img_dir)
            else:
                self.save_offline_and_switch(class_name, counter_per_class, row_values[1:-1], row_values, info_truk_dict, img_dir)

    def check_img(self, dir):
        image = None
        checkImgBest = os.path.exists(str(dir) +'best.JPG')
        checkImgWorst = os.path.exists(str(dir) +'worst.JPG')
        if checkImgBest:
            image = str(dir)+'best.JPG'
        elif checkImgWorst:
            image = str(dir) +'worst.JPG'
        else:
            image = Path(os.getcwd() + '/default-img/no_image.png')

        return image

    def push_data(self, intCat,intVal):
        connection = connect_to_database()

        global WBTicketNo 
 
        # Get the current datetime
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Values for the new row
        new_row = {
            'AI_NoTicket': str(WBTicketNo),
            'AI_Grading': str(intCat),
            'AI_JanjangSample': str(totalJjg), 
            'AI_TotalJanjang': str(totalJjg),
            'AI_Janjang': str(intVal)
        }

        sqlite_conn = sqlite3.connect('./db/grading_sampling.db')
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_insert_query = '''
        INSERT INTO quality (AI_NoTicket, AI_JanjangSample, AI_TotalJanjang, AI_Janjang, AI_push_time)
        VALUES (?, ?, ?, ?, ?)
        '''
        
        # Create a cursor and execute the INSERT statement for SQLite
        sqlite_cursor.execute(sqlite_insert_query, (
            new_row['AI_NoTicket'], new_row['AI_JanjangSample'], new_row['AI_TotalJanjang'],
            new_row['AI_Janjang'], current_time
        ))

         # Commit the changes to the SQLite database
        sqlite_conn.commit()
    
        # Close the cursor (not necessary, but recommended)
        sqlite_cursor.close()

        # Build the SQL INSERT statement
        SQL_INSERT = """
        INSERT INTO MOPQuality_Staging (AI_NoTicket, AI_Grading, AI_JanjangSample, AI_TotalJanjang, AI_push_time, AI_Janjang)
        VALUES (%(AI_NoTicket)s, %(AI_Grading)s, %(AI_JanjangSample)s, %(AI_TotalJanjang)s, GETDATE(),%(AI_Janjang)s);
        """

        # Create a cursor and execute the INSERT statement
        cursor = connection.cursor()
        cursor.execute(SQL_INSERT, new_row)

        # Commit the transaction to save the changes to the database
        connection.commit()

        # Close the database connection
        connection.close()

    def save_and_switch(self, class_name, count_per_class, row_values,info_truk_dict, img_dir):
        global date_end_conveyor
        self.submit_clicked = True
        class_count_dict = dict(zip(class_name, count_per_class))
        
        date_end_conveyor = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        waktu_mulai =  date_start_conveyor
        waktu_selesai =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        brondol = 0
        brondolBusuk = 0
        dirt = 0
        
        if self.submit_clicked and isClosedFrame3 == False:
            brondol_input = self.brondolanEntry.get()
            brondolBusuk_input = self.brondoalBusukEntry.get()
            dirt_input = self.dirtEntry.get()

            # Remove non-numeric characters
            brondol_input = remove_non_numeric(brondol_input)
            brondolBusuk_input = remove_non_numeric(brondolBusuk_input)
            dirt_input = remove_non_numeric(dirt_input)

            # Set values based on user input or keep the default values
            if brondol_input:
                brondol = int(brondol_input)
            if brondolBusuk_input:
                brondolBusuk = int(brondolBusuk_input)
            if dirt_input:
                dirt = int(dirt_input)


        tambahan ={
            'brondolan' : brondol,
            'brondolan_busuk' : brondolBusuk,
            'dirt':dirt,
            'waktu_mulai':waktu_mulai,
            'waktu_selesai':waktu_selesai
        }

        merged_dict = info_truk_dict.copy()  
        merged_dict.update(class_count_dict) 
        merged_dict.update(tambahan)


        result = ';'.join(map(str, row_values)) + ';'
        result += ';'.join(map(str, count_per_class)) + ';'
        result += str(brondol) + ';'
        result += str(brondolBusuk ) + ';'
        result += str(dirt)
        
        log_file_path = log_dir  

        try:
            with open(log_file_path, 'a') as log_file:
                log_file.write(str(merged_dict) + '\n')  # Append the result to the log file with a newline character
                # print("Data saved successfully to", log_file_path)
        except Exception as e:
            print("Error saving data to", log_file_path, ":", str(e))

        #convert data dari string ke array
        result = result.split(";")
        
        try:
            connection = connect_to_database()

            sql_query = """
            SELECT Ppro_GradeCode, Ppro_GradeDescription
            FROM MasterGrading_Staging;
            """

            cursor = connection.cursor()
            cursor.execute(sql_query)
            
            gradecodes = []
            gradedescriptions = []

            for row in cursor.fetchall():
                gradecodes.append(row['Ppro_GradeCode'])
                gradedescriptions.append(row['Ppro_GradeDescription'])

            for gradedescription, gradecode in zip(gradedescriptions, gradecodes):
                for index, name in enumerate(class_name):
                    cleaned_description = gradedescription.lower().replace(" ", "_")
                    
                    if cleaned_description == name and int(count_per_class[index]) != 0:
                        if cleaned_description == "abnormal":
                            self.push_data(gradecode, int(count_per_class[index]))
                        else:
                            self.push_data(gradecode, count_per_class[index])
                    elif cleaned_description == "tangkai_panjang" and name == "long_stalk" and int(count_per_class[index]) != 0:
                        self.push_data(gradecode, count_per_class[index])

                if gradedescription == "Brondolan" and brondol != 0:
                    self.push_data(gradecode, brondol)
                elif gradedescription == "DIRT/KOTORAN" and dirt != 0:
                    self.push_data(gradecode, dirt)
                elif gradedescription == "Brondolan Busuk" and brondolBusuk != 0:
                    self.push_data(gradecode, brondolBusuk)

            self.change_push_time(row_values)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            try:
                connection.close()
            except Exception as e:
                # Handle any closing connection exceptions here
                print(f"Error closing connection: {e}")

        messagebox.showinfo("Success", "Data Sukses Tersimpan !")  # Show success message

        generate_report(result, img_dir,class_count_dict,class_name, brondol, brondolBusuk, dirt)

        threading.Thread(target=self.run_send_pdf_in_background).start()
        if self.submit_clicked:
            self.master.switch_frame(Frame1)

    def change_push_time(self, raw):
        connection = connect_to_database()

        if isinstance(connection, pymssql.Connection):    
            notiket = raw[1]
            cursor = connection.cursor()

            SQL_UPDATE = """
            UPDATE MOPweighbridgeTicket_Staging
            SET AI_pull_time = GETDATE()
            WHERE WBTicketNo = %s;
            """

            cursor.execute(SQL_UPDATE, (notiket))
            connection.commit()
            connection.close()

            # Update in SQLite
            sqlite_conn = sqlite3.connect('./db/grading_sampling.db')
            sqlite_cursor = sqlite_conn.cursor()
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            sqlite_update_query = '''
            UPDATE weight_bridge
            SET AI_pull_time = ?
            WHERE WBTicketNo = ?;
            '''
            sqlite_cursor.execute(sqlite_update_query, (current_time, notiket))
            sqlite_conn.commit()
            sqlite_conn.close()

            return "Push time changed successfully."
        else:
            return "Failed to changed time"

    async def send_pdf_async(self):
        try:
            process = await asyncio.create_subprocess_exec(
                'python', str(Path(os.getcwd())) + '/send_pdf_inference.py',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                print("send_pdf_inference.py completed successfully")
            else:
                print(f"send_pdf_inference.py failed with return code {process.returncode}")
                print(f"stdout: {stdout.decode()}")
                print(f"stderr: {stderr.decode()}")
        except Exception as e:
            print("Error running send_pdf_inference.py:", str(e))

    def run_send_pdf_in_background(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.send_pdf_async())
        loop.close()

    def save_offline_and_switch(self, class_name, count_per_class, row_values, row_values_full, info_truk_dict, img_dir):
        self.submit_clicked = True
        global date_end_conveyor

        brondol = 0
        brondolBusuk = 0
        dirt = 0
        
        # Check if the Entry widgets still exist before accessing their values
        if self.submit_clicked and isClosedFrame3 == False:
            brondol_input = self.brondolanEntry.get()
            brondolBusuk_input = self.brondoalBusukEntry.get()
            dirt_input = self.dirtEntry.get()

            # Remove non-numeric characters
            brondol_input = remove_non_numeric(brondol_input)
            brondolBusuk_input = remove_non_numeric(brondolBusuk_input)
            dirt_input = remove_non_numeric(dirt_input)

            # Set values based on user input or keep the default values
            if brondol_input:
                brondol = int(brondol_input)
            if brondolBusuk_input:
                brondolBusuk = int(brondolBusuk_input)
            if dirt_input:
                dirt = int(dirt_input)

        row_values_subset = ';'.join(map(str, row_values))
        class_count_dict = dict(zip(class_name, count_per_class))
        mill_id = id_mill
        WBTicketNo = row_values[0] if row_values else ''
        VehiclePoliceNO = row_values[1]if row_values else ''
        DriverName = row_values[2]if row_values else ''
        BUnit = row_values[3]if row_values else ''
        Divisi = row_values[4]if row_values else ''
        Field = row_values[5]if row_values else ''
        Status = row_values[7]if row_values else ''
        waktu_mulai =  date_start_conveyor
        waktu_selesai =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date_end_conveyor =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        unripe = class_count_dict['unripe']
        ripe = class_count_dict['ripe']
        overripe = class_count_dict['overripe']
        empty_bunch = class_count_dict['empty_bunch']
        abnormal = class_count_dict['abnormal']
        tp = class_count_dict['long_stalk']
        kastrasi = class_count_dict['kastrasi']
        
        tambahan ={
            'brondolan' : brondol,
            'brondolan_busuk' : brondolBusuk,
            'dirt':dirt,
            'waktu_mulai':waktu_mulai,
            'waktu_selesai':waktu_selesai
        }

        merged_dict = info_truk_dict.copy()  
        merged_dict.update(class_count_dict) 
        merged_dict.update(tambahan)


        sqlite_conn = sqlite3.connect('./db/grading_sampling.db')
        sqlite_cursor = sqlite_conn.cursor()

        insert_record_query = '''
        INSERT INTO log_sampling (
            mill_id, waktu_mulai, waktu_selesai, no_tiket, no_plat, nama_driver, bisnis_unit, divisi, blok, status, 
            unripe, ripe, overripe, empty_bunch, abnormal, kastrasi, tp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''

        record_data = (
            mill_id, waktu_mulai, waktu_selesai, WBTicketNo, VehiclePoliceNO, DriverName, BUnit, Divisi, Field, Status, 
            unripe, ripe, overripe, empty_bunch, abnormal, kastrasi, tp
        )


        try:
            sqlite_cursor.execute(insert_record_query, record_data)
            sqlite_conn.commit()

            sqlite_conn.close()
            print("New record inserted successfully.")
        except Exception as e:
            print("An error occurred while inserting the record:", str(e))
        
       

        result = list(row_values_full)

        strInputan = str(brondol) + ';'
        strInputan += str(brondolBusuk) + ';'
        strInputan += str(dirt)
        
        # count_class = ';'.join(map(str, count_per_class)) + ';'
        # with open(offline_log_dir, 'r') as log_file:
        #     data = log_file.readlines()

        # for line_number, line in enumerate(data, start=1):
        #     values = line.strip().split(';')
        #     tuple_val = tuple(values[:-1]) 
        #     #membandingkan row clicked dgn row didalam txt jika sama ubah status None jadi ready
        #     if tuple_val == row_values:
        #         data[line_number - 1] = row_values_subset + ';READY;' + count_class + strInputan  + '\n'
        #         with open(offline_log_dir, 'w') as log_file:
        #             log_file.writelines(data)
        #         break
        
        with open(offline_log_dir, 'r') as file:
            lines = file.readlines()

        for line_number, line in enumerate(lines):
            try:
                # Replace single quotes with double quotes in the line
                line_with_double_quotes = line.replace("'", "\"")

                # Parse the line as a dictionary using json.loads
                line_dict = json.loads(line_with_double_quotes)

                # Check if the specified fields match
                if line_dict.get('no_tiket') == merged_dict['no_tiket'] and line_dict.get('no_plat') == merged_dict['no_plat'] and line_dict.get('status_inference') != 'READY':

                    original_waktu_input = line_dict.get('waktu_input')
                    merged_dict['waktu_input'] = original_waktu_input
                    lines[line_number] = str(merged_dict) + '\n'
                    # print(f"Variable replaced with line {line_number}: {line_dict}")
                    break  # Assuming you want to stop after the first match, remove if you want to continue checking the rest of the lines
                # else:
                #     print(f"Fields do not match in line {line_number}")
            except json.JSONDecodeError:
                print(f"Error decoding JSON in line {line_number}")
        
        with open(offline_log_dir, 'w') as file:
            file.writelines(lines)

        messagebox.showinfo("Success", "Data Sukses Tersimpan !")  # Show success message
        generate_report(result, img_dir,class_count_dict, class_name, brondol, brondolBusuk, dirt)

        threading.Thread(target=self.run_send_pdf_in_background).start()

        if self.submit_clicked:
            self.master.switch_frame(Frame1)    
           
class EditBridgeFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.clicked_buttons = []

        frame1_instance = Frame1(master)

        self.tree = ttk.Treeview(self, columns=columns, selectmode="none", show="headings")
        self.style = ttk.Style(self)
        self.row_height = 100  # Set the desired row height
        self.detail_window = None

        self.style.configure("Treeview", rowheight=self.row_height)
        self.tree.heading("#1", text="No")
        self.tree.heading("#2", text="NOMOR TIKET")
        self.tree.heading("#3", text="NOMOR POLISI")
        self.tree.heading("#4", text="NAMA DRIVER")
        self.tree.heading("#5", text="BISNIS UNIT")
        self.tree.heading("#6", text="DIVISI")
        self.tree.heading("#7", text="FIELD")
        self.tree.heading("#8", text="BUNCHES")
        self.tree.heading("#9", text="OWNERSHIP")
        self.tree.heading("#10", text="PUSH TIME")
        self.tree.heading("#11", text="ACTION")

        self.tree.column("no", width=50)
        self.tree.column("notiket", width=250)
        self.tree.column("nopol", width=100, anchor="center")
        self.tree.column("driver")
        self.tree.column("b_unit")
        self.tree.column("divisi")
        self.tree.column("field")
        self.tree.column("bunches", width=70)
        self.tree.column("ownership", anchor="center")
        self.tree.column("pushtime", anchor="center")
        self.tree.column("action", anchor="center")

        connection = connect_to_database()

        if isinstance(connection, pymssql.Connection):
            
            master_bunit = frame1_instance.pull_master(connection, 'MasterBunit_staging','Ppro_BUnitCode','Ppro_BUnitName',data_bunit)
            master_div = frame1_instance.pull_master(connection,'MasterDivisi_Staging','Ppro_DivisionCode','Ppro_DivisionName',data_div)
            master_block = frame1_instance.pull_master(connection,'MasterBlock_Staging','Ppro_FieldCode','Ppro_FieldName',data_block)
            
            current_date = datetime.datetime.now().date()

            start_time = datetime.time(7, 0, 0)
            date_today = datetime.datetime.combine(current_date, start_time)
            record = frame1_instance.pull_data_ppro(connection, date_today)
            connection.close()

            frame1_instance.master.title(f"Sistem Aplikasi Pos Grading - {status_mode.capitalize()} - {mode_app.capitalize()}")
            arr_data = frame1_instance.process_data(record, master_bunit, master_div, master_block)
        else:
            # Connect to the SQLite3 database
            sqlite_conn = sqlite3.connect('./db/grading_sampling.db')
            sqlite_cursor = sqlite_conn.cursor()

            # Calculate the start and end datetime objects
            current_date = datetime.datetime.now().date()
            start_time = create_datetime(current_date, 7, 0, 0)
            end_time = start_time + datetime.timedelta(days=1)

            # Query records where waktu_mulai is between start_time and end_time
            query = '''
            SELECT id, no_tiket, no_plat, nama_driver, bisnis_unit, divisi, blok, status, status, waktu_mulai FROM log_sampling
            WHERE waktu_mulai >= ? AND waktu_mulai <= ?
            '''
            sqlite_cursor.execute(query, (start_time, end_time))
            results = sqlite_cursor.fetchall()            
            arr_data = results

        
        for i, data in enumerate(arr_data, start=1):
            item = self.tree.insert("", "end", values=data, tags=i)
            
            self.tree.set(item, "#1", str(i))
            if status_mode == 'offline':
                self.tree.set(item, "#8", '')
            self.tree.set(item, "#11", "EDIT")
            self.tree.tag_bind(i, "<Double-Button-1>", lambda event, row_item=item: self.edit_row(row_item, event))     
   
       

        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky='ew')

        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_columnconfigure(2, weight=200)
        top_frame.grid_columnconfigure(3, weight=20)
        top_frame.grid_columnconfigure(4, weight=20)
        self.top_frame = top_frame
        
        self.button = ttk.Button(self, text="Kembali", command=self.switch_frame)
        self.button.grid(row=0, column=0, sticky="ne")


        self.title_label = tk.Label(top_frame, text=f"LIST TRUK SETELAH PROSES DETEKSI AI {get_list_mill(log_mill,flag=False)[0]}", font=("Helvetica", 16, "bold"))
        self.title_label.grid(row=0, column=2)
        self.logo_image = tk.PhotoImage(file=Path(os.getcwd() + '/default-img/Logo-CBI(4).png'))  # Replace "logo.png" with your image file path
        self.logo_image = self.logo_image.subsample(2, 2)  # Adjust the subsample values to resize the image
        logo_label = tk.Label(top_frame, image=self.logo_image)
        logo_label.grid(row=0, column=0)

        self.logo_image2 = tk.PhotoImage(file=Path(os.getcwd() + '/default-img/LOGO-SRS(1).png'))
        self.logo_image2 = self.logo_image2.subsample(2, 2)
        logo_label2 = tk.Label(top_frame, image=self.logo_image2)
        logo_label2.grid(row=0, column=1)  # Change column to 0 and sticky to "ne"

        self.tree.grid(row=1, column=0, columnspan=6, sticky="nsew")

        top_frame.grid_columnconfigure(6, weight=20)

        self.tree.grid(row=1, column=0, columnspan=6, sticky="nsew")  # Use columnspan to span all columns

        self.footer_frame = tk.Frame(self)
        self.footer_frame.grid(row=2, column=0, columnspan=6, sticky="ew", pady=40)  # Use columnspan to span all columns

        footer_label = tk.Label(self.footer_frame, text="Copyright @ Digital Architect SRS 2023", font=("Helvetica", 14, "bold"))
        footer_label.pack()

        self.last_update_model = tk.Frame(self)
        self.last_update_model.grid(row=2, column=0, columnspan=3, sticky="nw", pady=10)  # Use columnspan to span all columns

        last_model = tk.Label(self.last_update_model, text="Tanggal Update Model AI : 08 Agustus 2023",font=("Helvetica", 12, "italic"))
        last_model.pack()
                
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

    def switch_frame(self):
        self.master.switch_frame(Frame1)

    def edit_row(self, row_item, event ):

        row_id = int(self.tree.item(row_item, "tags")[0])  # Get row ID from tags

        column = self.tree.identify_column(event.x)  # Identify the column clicked
        status_row = self.tree.item(row_item, "values")[-1]
        row_values = self.tree.item(row_item, "values")  # Get values of the row
        
        
        column = column.split("#")[-1]
        for cb in self.clicked_buttons:
            
            self.tree.tag_configure(cb, background="#ffffff")  # Change row color
            self.clicked_buttons.remove(cb)
        
        confirmation = messagebox.askyesno("Konfirmasi", f"Apakah benar akan melakukan edit pada SPB nomor {row_values[0]}?")
        if confirmation:
            self.edit_field(row_values)

    def edit_field(self, row_values):
        WBTicketNo = row_values[1] if row_values else ''
        VehiclePoliceNO = row_values[2]if row_values else ''
        DriverName = row_values[3]if row_values else ''
        BUnit = row_values[4].strip() if row_values else ''
        Divisi = row_values[5]if row_values else ''
        Field = row_values[6]if row_values else ''
        Bunches = row_values[7]if row_values else ''
        
        edit_data_overlay = tk.Toplevel(self.master)
        edit_data_overlay.title("Edit Data " + str(WBTicketNo))
        
        overlay_width = 580
        overlay_height = 500
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - overlay_width) // 2
        y = (screen_height - overlay_height) // 2
        edit_data_overlay.geometry(f"{overlay_width}x{overlay_height}+{x}+{y}")
        
        overlay_frame = ttk.Frame(edit_data_overlay)
        overlay_frame.grid(row=0, column=0, padx=10, pady=10)

        tiket_label = ttk.Label(overlay_frame, text="Nomor Tiket")
        tiket_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.tiket_entry = ttk.Entry(overlay_frame, width=30)

        tiket = []
        if status_mode == 'online':
            # start_date = datetime.datetime(2023, 10, 30, 7, 0, 0)
            current_date = datetime.datetime.now().date()
            start_time = datetime.time(7, 0, 0)
            start_date = datetime.datetime.combine(current_date, start_time)
            
            end_date = start_date + datetime.timedelta(days=1)
            connection = connect_to_database()

            sql_query = "SELECT  DISTINCT WBTicketNo FROM MOPweighbridgeTicket_Staging WHERE Ppro_push_time >= %s AND Ppro_push_time < %s AND WBTicketNo <> %s AND AI_pull_time IS NULL"
            cursor = connection.cursor()
            cursor.execute(sql_query, (start_date, end_date, WBTicketNo))
            records = cursor.fetchall()

            tiket = [record['WBTicketNo'] for record in records]
            connection.close()
        else:
            with open(offline_log_dir, 'r') as file:
                    data = file.readlines()

                    for line in data:
                        convert_line = eval(line)
                        status = convert_line['status_inference']
                        
                        if str(status) ==  'None':
                            tiket.append(convert_line['no_tiket'])
                        
        self.tiket_combobox = ttk.Combobox(overlay_frame, values=tiket, width=30)  # Adjust the width value as needed
        self.tiket_combobox.grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.tiket_combobox.bind("<<ComboboxSelected>>", lambda event=None: update_label())
 
        def update_label():
            selected_value = self.tiket_combobox.get()
            connection = connect_to_database()

            if isinstance(connection, pymssql.Connection):
                sql_query = "SELECT * FROM MOPweighbridgeTicket_Staging WHERE WBTicketNo = %s AND AI_pull_time IS NULL"
                cursor = connection.cursor()
                cursor.execute(sql_query, (selected_value,))
                records = cursor.fetchall()

                if records:
                    nopol_values = [record['VehiclePoliceNO'] for record in records]
                    driver_names = [record['DriverName'] for record in records]
                    bunit_codes = [record['BUnitCode'] for record in records]
                    division_codes = [record['DivisionCode'] for record in records]
                    fields = [record['Field'] for record in records]
                    bunches = [record['Bunches'] for record in records]
                    ownership = [record['Ownership'] for record in records]

                    unique_nopol_values = list(set(nopol_values))
                    unique_driver_names = list(set(driver_names))
                    unique_bunit_names = list(set(bunit_codes))
                    unique_division_names = list(set(division_codes))
                    unique_bunches_names = [str(item) for item in list(set(bunches))]
                    unique_field_names = list(set(fields))
                    unique_ownership_names = list(set(ownership))
                    
                    additional_sql_query = "SELECT Ppro_BUnitName FROM MasterBunit_staging WHERE Ppro_BUnitCode IN %s"
                    cursor.execute(additional_sql_query, (tuple(unique_bunit_names),))
                    additional_records = cursor.fetchall()
                    bunit_name = [record['Ppro_BUnitName'] for record in additional_records]
                    final_bunit =  list(set(bunit_name))

                    additional_sql_query = "SELECT Ppro_DivisionName FROM MasterDivisi_Staging WHERE Ppro_DivisionCode IN %s"
                    cursor.execute(additional_sql_query, (tuple(unique_division_names),))
                    additional_records = cursor.fetchall()
                    divisi_name = [record['Ppro_DivisionName'] for record in additional_records]
                    final_divisi =  list(set(divisi_name))

                    additional_sql_query = "SELECT Ppro_FieldName FROM MasterBlock_Staging WHERE Ppro_FieldCode IN %s"
                    cursor.execute(additional_sql_query, (tuple(unique_field_names),))
                    additional_records = cursor.fetchall()
                    blok_name = [record['Ppro_FieldName'] for record in additional_records]
                    final_blok =  list(set(blok_name))

                    self.nopol_val.delete(0, "end")  # Clear the existing value in the Entry widget
                    self.nopol_val.insert(0, ", ".join(unique_nopol_values))  # Set the new value
                    self.driver_val.delete(0, "end")  # Clear the existing value in the Entry widget
                    self.driver_val.insert(0, ", ".join(unique_driver_names))  # Set the new value
                    bunit_val.config(text=", ".join(final_bunit))
                    divisi_val.config(text=", ".join(final_divisi))
                    bunches_val.config(text=", ".join(unique_bunches_names))
                    if not final_blok:
                        blok_val.config(text="-")
                    else:
                        blok_val.config(text="\n".join(final_blok))
                    ownership_val.config(text=", ".join(unique_ownership_names))
            else:
                with open(offline_log_dir, 'r') as file:
                    data = file.readlines()
                    
                for line in data:
                    convert_line = eval(line)
                    no_tiket_line = convert_line['no_tiket']
                    if str(no_tiket_line) ==  selected_value:
                        nopol = convert_line.get('no_plat', '-')
                        driver = convert_line.get('nama_driver', '-')
                        bunit = convert_line.get('bunit', '-')
                        divisi = convert_line.get('divisi', '-')
                        blok = convert_line.get('blok', '-')
                        bunches = convert_line.get('bunches','-')
                        ownership = convert_line.get('ownership', '-')
                       
                            # bunit_val.config(text=tiket)
                        self.nopol_val.delete(0, "end")  # Clear the existing value in the Entry widget
                        self.nopol_val.insert(0, nopol)  # Set the new value
                        self.driver_val.delete(0, "end")  # Clear the existing value in the Entry widget
                        self.driver_val.insert(0, driver)  # Set the new value
                        bunit_val.config(text=bunit)
                        divisi_val.config(text=divisi)
                        blok_val.config(text=blok)
                        bunches_val.config(text=bunches)
                        ownership_val.config(text=ownership)
                        # bunit_val.config(text=status)
            

            if status_mode == 'online':
                connection.close()
            
            return selected_value

        

        
        bold_font = ("Arial", 10, "bold")
    
        nopol_label = ttk.Label(overlay_frame, text="Nomor Polisi")
        nopol_label.grid(row=0, column=1, padx=10, pady=10, sticky='w')

        self.nopol_val = ttk.Entry(overlay_frame, width=30)
        self.nopol_val.insert(0, "-") 
        self.nopol_val.grid(row=1, column=1, padx=10, pady= 10, sticky='w')

        driver_label = ttk.Label(overlay_frame, text="Nama Driver")
        driver_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')

        self.driver_val = ttk.Entry(overlay_frame, width=30)
        self.driver_val.insert(0, "-")
        self.driver_val.grid(row=3, column=0, padx=10, pady= 10, sticky='w')

        bunit_label = ttk.Label(overlay_frame, text="Bisnis Unit")
        bunit_label.grid(row=2, column=1, padx=10, pady=10, sticky='w')

        bunit_val = ttk.Label(overlay_frame, text="-",  font=bold_font)
        bunit_val.grid(row=3, column=1, padx=10, pady=10, sticky='w')

        divisi_label = ttk.Label(overlay_frame, text="Divisi")
        divisi_label.grid(row=4, column=0, padx=10, pady=10, sticky='w')

        divisi_val = ttk.Label(overlay_frame, text="-",  font=bold_font)
        divisi_val.grid(row=5, column=0, padx=10, pady=10, sticky='w')

        # if status_mode == 'online':
        bunches_label = ttk.Label(overlay_frame, text="Bunches")
        bunches_label.grid(row=4, column=1, padx=10, pady=10, sticky='w')

        bunches_val = ttk.Label(overlay_frame, text="-",  font=bold_font)
        bunches_val.grid(row=5, column=1, padx=10, pady=10, sticky='w')

        blok_label = ttk.Label(overlay_frame, text="Blok")
        blok_label.grid(row=6, column=0, padx=10, pady=10, sticky='w')

        blok_val = ttk.Label(overlay_frame, text="-" ,  font=bold_font)
        blok_val.grid(row=7, column=0, padx=10, pady=10, sticky='w')


        owndership_label = ttk.Label(overlay_frame, text="Status")
        owndership_label.grid(row=6, column=1, padx=10, pady=10, sticky='w')

        ownership_val = ttk.Label(overlay_frame, text="-" ,  font=bold_font)
        ownership_val.grid(row=7, column=1, padx=10, pady=10, sticky='w')

        # blok_entries = []
        # if '\n' in Field:
        if status_mode == 'online':

            submit_button = ttk.Button(overlay_frame, text="Submit", command=lambda: self.update_data(WBTicketNo, edit_data_overlay))
            submit_button.grid(row=12, column=0, padx=10, pady=20, sticky='w')
        else:
            submit_button = ttk.Button(overlay_frame, text="Submit", command=lambda: self.update_data_offline( self.nopol_val.get(), self.driver_val.get(), bunit_val.cget("text"), divisi_val.cget("text"),blok_val.cget("text"),ownership_val.cget("text"), edit_data_overlay, WBTicketNo))
            submit_button.grid(row=12, column=0, padx=10, pady=20, sticky='w')

        # else:
        #     blok_label = ttk.Label(overlay_frame, text="Blok")
        #     blok_label.grid(row=7, column=0, padx=10, pady=10, sticky='w')

        #     blok_entry = ttk.Entry(overlay_frame, width=30)
        #     blok_entry.insert(0, Field)
        #     blok_entry.grid(row=8, column=0, padx=10, pady=10)

        #     blok_entries.append(blok_entry)
        #     if status_mode == 'online':
        #         submit_button = ttk.Button(overlay_frame, text="Submit", command=lambda: self.update_data(blok_entries, WBTicketNo, edit_data_overlay))
        #     else:
        #         submit_button = ttk.Button(overlay_frame, text="Submit", command=lambda: self.update_data_offline( blok_entries, edit_data_overlay, row_values[0]))
        #     submit_button.grid(row=9, column=0, padx=10, pady=20, sticky='w')
    

    def update_data_offline(self, nopol, driver, bunit, divisi, blok, ownership, edit_data_overlay, tiket_lama):

        classAll = ['unripe','ripe','overripe','empty_bunch','abnormal','long_stalk', 'kastrasi']
        
        new_tiket = self.tiket_combobox.get()        
        sqlite_conn = sqlite3.connect('./db/grading_sampling.db')
        sqlite_cursor = sqlite_conn.cursor()

        current_date = datetime.datetime.now().date()
        start_time = create_datetime(current_date, 7, 0, 0)
        end_time = start_time + datetime.timedelta(days=1)

        query = '''
        UPDATE log_sampling
        SET 
            no_tiket = ?,
            no_plat = ?,
            nama_driver = ?,
            bisnis_unit = ?,
            divisi = ?,
            blok = ?,
            status = ?
        WHERE waktu_mulai >= ? AND waktu_mulai <= ? AND no_tiket = ?
        '''

        try:
            sqlite_cursor.execute(query, (new_tiket, nopol, driver, bunit, divisi, blok, ownership, start_time, end_time, tiket_lama))

            rows_affected = sqlite_cursor.rowcount

            sqlite_conn.commit()

            if rows_affected > 0:
                print(f"Update successful. {rows_affected} row(s) updated.")
            else:
                print("No rows were updated. Check if the specified 'no_tiket' exists within the specified time range.")

        except sqlite3.Error as e:
            print(f"Update failed. Error: {e}")

        finally:
            sqlite_conn.close()

        tic_old = None
        tic_new = None
        line_number_old = None 
        line_number_new = None 

        with open(offline_log_dir, 'r') as file:
            data = file.readlines()

            index = 0
            for line in data:
                convert_line = eval(line)
                no_tiket_line = convert_line['no_tiket']
                if no_tiket_line == tiket_lama:
                    tic_old = convert_line
                    line_number_old = index

                if no_tiket_line == new_tiket:
                    tic_new = convert_line
                    line_number_new = index
                index += 1

            tic_new.update({
                'unripe': tic_old['unripe'],
                'ripe': tic_old['ripe'],
                'overripe': tic_old['overripe'],
                'abnormal': tic_old['abnormal'],
                'empty_bunch': tic_old['empty_bunch'],
                'long_stalk': tic_old['long_stalk'],
                'kastrasi': tic_old['kastrasi'],
                'brondolan': tic_old['brondolan'],
                'brondolan_busuk': tic_old['brondolan_busuk'],
                'dirt': tic_old['dirt'],
                'waktu_mulai': tic_old['waktu_mulai'],
                'waktu_selesai': tic_old['waktu_selesai'],
                'status_inference':'READY'
            })
            
            raw = info_truk(tic_old['no_tiket'], tic_old['no_plat'],tic_old['nama_driver'], tic_old['bunit'],tic_old['divisi'], tic_old['blok'],tic_old['bunches'], tic_old['ownership'],'None')
            raw['waktu_input'] = tic_old['waktu_input']
            replacement_line_old = str(raw) + '\n'
        
            if 0 <= line_number_old <= len(data):
                data[line_number_old] = replacement_line_old

            if 0 <= line_number_new <= len(data):
                data[line_number_new] = str(tic_new) + '\n'

        with open(offline_log_dir, 'w') as file:
            for line in data:
                file.write(line)
            
        rawData = []
        rawData.append(new_tiket)
        rawData.append(nopol)
        rawData.append(driver)
        rawData.append(bunit)
        rawData.append(divisi)
        
        blok_modified = blok.replace(' ', '\n')
        rawData.append(blok_modified)
        rawData.append(ownership)

        img_dir = copy_img_edit_mode(tiket_lama)

        class_count = [tic_old['unripe'],tic_old['ripe'],tic_old['overripe'], tic_old['abnormal'],tic_old['empty_bunch'],tic_old['long_stalk'],tic_old['kastrasi']]
        class_name_values = {key: value for key, value in zip(classAll, class_count)}

        generate_report(rawData, img_dir,class_name_values, classAll, tic_old['brondolan'],  tic_old['brondolan_busuk'],  tic_old['dirt'] ,1)        
        messagebox.showinfo("Success", "Data Tiket " + tiket_lama + " Berhasil terupdate")  
        edit_data_overlay.destroy()
        self.master.switch_frame(EditBridgeFrame)
        
            
    def update_data(self, WBTicketNo, edit_data_overlay):

        classAll = ['unripe','ripe','overripe','empty_bunch','abnormal','long_stalk', 'kastrasi', 'Brondolan', 'Brondolan Busuk','DIRT/KOTORAN']

        class_totals = {class_name: 0 for class_name in classAll}

        new_tiket_value = self.tiket_combobox.get()

        nopol = self.nopol_val.get()
        driver = self.driver_val.get()

        connection = connect_to_database()

        # raw data untuk pdf
        sql_query = "SELECT * FROM MOPweighbridgeTicket_Staging WHERE WBTicketNo = %s"
        cursor = connection.cursor()
        cursor.execute(sql_query, (new_tiket_value,))
        records = cursor.fetchall()
        rawData = []
        if records:
            nopol_values = [record['VehiclePoliceNO'] for record in records]
            driver_names = [record['DriverName'] for record in records]
            bunit_codes = [record['BUnitCode'] for record in records]
            division_codes = [record['DivisionCode'] for record in records]
            fields = [record['Field'] for record in records]
            bunches = [record['Bunches'] for record in records]
            status = [record['Ownership'] for record in records]

            unique_nopol_values = list(set(nopol_values))
            unique_driver_names = list(set(driver_names))
            unique_bunit_names = list(set(bunit_codes))
            unique_division_names = list(set(division_codes))
            unique_bunches_names = [str(item) for item in list(set(bunches))]
            unique_field_names = list(set(fields))
            unique_status_names = list(set(status))
            
            additional_sql_query = "SELECT Ppro_BUnitName FROM MasterBunit_Staging WHERE Ppro_BUnitCode IN %s"
            cursor.execute(additional_sql_query, (tuple(unique_bunit_names),))
            additional_records = cursor.fetchall()
            bunit_name = [record['Ppro_BUnitName'] for record in additional_records]
            final_bunit =  list(set(bunit_name))

            additional_sql_query = "SELECT Ppro_DivisionName FROM MasterDivisi_Staging WHERE Ppro_DivisionCode IN %s"
            cursor.execute(additional_sql_query, (tuple(unique_division_names),))
            additional_records = cursor.fetchall()
            divisi_name = [record['Ppro_DivisionName'] for record in additional_records]
            final_divisi =  list(set(divisi_name))

            additional_sql_query = "SELECT Ppro_FieldName FROM MasterBlock_Staging WHERE Ppro_FieldCode IN %s"
            cursor.execute(additional_sql_query, (tuple(unique_field_names),))
            additional_records = cursor.fetchall()
            blok_name = [record['Ppro_FieldName'] for record in additional_records]
            final_blok =  list(set(blok_name))
            rawData.append(new_tiket_value)
            rawData.append("; ".join(unique_nopol_values))
            rawData.append("; ".join(unique_driver_names))
            rawData.append("; ".join(final_bunit))
            rawData.append("; ".join(final_divisi))
            
            if not final_blok:
                rawData.append("-")
            else:
                rawData.append("\n".join(final_blok))
            rawData.append("; ".join(unique_bunches_names))
            rawData.append("; ".join(unique_status_names))
        
        rawData.insert(0, "")

        img_dir = copy_img_edit_mode(WBTicketNo)

        try:
            cursor = connection.cursor()

            # Update the old WBTicketNo
            update_old_query = """
            UPDATE MOPweighbridgeTicket_Staging
            SET AI_pull_time = NULL
            WHERE WBTicketNo = %s
            """
            cursor.execute(update_old_query, (WBTicketNo,))
            connection.commit()

            # Update the new WBTicketNo with the current date and time
            current_datetime = datetime.datetime.now()
            
            update_new_query = """
                UPDATE MOPweighbridgeTicket_Staging
                SET AI_pull_time = %s,
                    VehiclePoliceNO = %s,
                    DriverName = %s
                WHERE WBTicketNo = %s
            """
            cursor.execute(update_new_query, (current_datetime, nopol, driver, new_tiket_value))
            connection.commit()

        except pymssql.Error as e:
            messagebox.showinfo("Error", f"An error occurred while updating the database MOPweighbridgeTicket_Staging: {e}")  
        
        # update sql set ai_pull_time old tiket ke null
        sqlite_conn = sqlite3.connect('./db/grading_sampling.db')
        sqlite_cursor = sqlite_conn.cursor()
        # Update the weight_bridge table with AI_pull_time set to NULL for the specified WBTicketNo
        update_sql = "UPDATE weight_bridge SET AI_pull_time = NULL WHERE WBTicketNo = ?;"
        sqlite_cursor.execute(update_sql, (WBTicketNo,))
        sqlite_conn.commit()
        sqlite_cursor.close()
        sqlite_conn.close()

        # udpate sql wb new tiket new ai_pull_time
        sqlite_conn = sqlite3.connect('./db/grading_sampling.db')
        sqlite_cursor = sqlite_conn.cursor()

        # Update the weight_bridge table with the new values
        update_sql = "UPDATE weight_bridge SET AI_pull_time = ?, VehiclePoliceNO = ?, DriverName = ? WHERE WBTicketNo = ?;"
        sqlite_cursor.execute(update_sql, (current_datetime, nopol, driver, new_tiket_value))

        sqlite_conn.commit()
        sqlite_cursor.close()
        sqlite_conn.close()

        try:

            select_query = """
            SELECT AI_NoTicket, AI_Grading, AI_Janjang  FROM MOPQuality_Staging
            WHERE AI_NoTicket = %s
            """
            cursor = connection.cursor()
            cursor.execute(select_query, (WBTicketNo,))
            result = cursor.fetchall()

            grade_codes = []
            for row in result:
                AI_Grading = row['AI_Grading']
                Jumlah_AI_Grading = row['AI_Janjang']

                SQL_QUERY = """
                SELECT *
                FROM MasterGrading_Staging
                WHERE Ppro_GradeCode = %s
                """
                cursor.execute(SQL_QUERY, (AI_Grading,))
                inner_result = cursor.fetchall()

                inner_data = []
                for inner_row in inner_result:
                    Ppro_GradeName = inner_row['Ppro_GradeDescription']
                    
                    matched_class = None
                    if "long_stalk" in classAll:
                        if Ppro_GradeName.lower() == "Tangkai Panjang".lower():
                            matched_class = "long_stalk"

                    if "empty_bunch" in classAll:
                        if Ppro_GradeName.lower() == "Empty Bunch".lower():
                            matched_class = "empty_bunch"

                    if not matched_class:
                        # Check for other class names in classAll      
                        matched_class = next((class_name for class_name in classAll if class_name.lower() == Ppro_GradeName.lower()), None)

                    if matched_class:
        
                        class_totals[matched_class] += int(Jumlah_AI_Grading)

            class_original = ['unripe','ripe','overripe','empty_bunch','abnormal','long_stalk', 'kastrasi']

            class_name_values = {}

            for index in class_original:
                class_name_values[index] = class_totals.get(index, 0)

            generate_report(rawData, img_dir,class_name_values, class_original, class_totals['Brondolan'], class_totals['Brondolan Busuk'],class_totals['DIRT/KOTORAN'] ,1)
        except Exception as e:
            messagebox.showinfo("Error", f"An error occurred while fetch data MOPQuality_Staging: {e}")  

        try:
            # update quality
            SQL_UPDATE = """
            UPDATE MOPQuality_Staging
            SET AI_NoTicket = %(new_AI_NoTicket)s
            WHERE AI_NoTicket = %(old_AI_NoTicket)s;
            """

            update_values = {
                'new_AI_NoTicket': new_tiket_value,  # Join blok values into a single string
                'old_AI_NoTicket': WBTicketNo
            }

            # Create a cursor and execute the UPDATE statement
            cursor = connection.cursor()
            cursor.execute(SQL_UPDATE, update_values)

            # Commit the changes to the database
            connection.commit()

            # Close the cursor and connection
            cursor.close()
                    
            messagebox.showinfo("Success", "Data Tiket " + new_tiket_value + " Berhasil terupdate")  
            edit_data_overlay.destroy()
            self.master.switch_frame(EditBridgeFrame)
        except Exception as e:
            messagebox.showinfo("Error", f"An error occurred while updating the database MOPQuality_Staging: {e}")  

        # update db lokal table quality
        sqlite_conn = sqlite3.connect('./db/grading_sampling.db')
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute("UPDATE quality SET AI_NoTicket = ? WHERE AI_NoTicket = ?;", (new_tiket_value, WBTicketNo))
        sqlite_conn.commit()
        sqlite_cursor.close()
        sqlite_conn.close()

        
        connection.close()
        
class Frame2(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        connection = connect_to_database()

        if isinstance(connection, pymssql.Connection):
            self.master.switch_frame(Frame1)
        

        self.logo_image = tk.PhotoImage(file=Path(os.getcwd() + '/default-img/Logo-CBI(4).png'))  # Replace "logo.png" with your image file path
        self.logo_image = self.logo_image.subsample(2, 2)  # Adjust the subsample values to resize the image
        logo_label = tk.Label(self, image=self.logo_image)
        logo_label.grid(row=0, column=0, padx=40, pady=10, sticky="nw")

        self.logo_image2 = tk.PhotoImage(file=Path(os.getcwd() + '/default-img/LOGO-SRS(1).png'))
        self.logo_image2 = self.logo_image2.subsample(2, 2)
        logo_label2 = tk.Label(self, image=self.logo_image2)
        logo_label2.grid(row=0, column=0, padx=190, pady=15, sticky="nw")  # Change column to 0 and sticky to "ne"

        self.style = ttk.Style()
        self.style.configure("back.TButton", padding=6, borderwidth=3, relief="groove", font=("Helvetica", 10))

         # Create a styled button
        self.button = ttk.Button(self, text="Kembali", command=self.switch_frame, style="back.TButton")
        self.button.grid(row=0, column=0, padx=120, pady=30, sticky="ne")

        label_font = ("Helvetica", 11)  # Define a larger font for labels
        entry_font = ("Helvetica", 11)  # Define a larger font for entry fields

        user_info_frame =tk.LabelFrame(self, text="Form Informasi Truk FFB Grading", font=("Helvetica", 16, "bold"))
        user_info_frame.grid(row= 0, column=0, padx=700, pady=40, sticky="w")

        label_padding = 10  # Adjust the padding value as needed

        labels = [
            ("No Tiket", 1, 0),
            ("No Plat", 1, 1),
            ("Nama Driver", 1, 2),
            ("Bisnis Unit", 3, 0),
            ("Divisi", 3, 1),
            ("Blok", 3, 2),
            ("Bunches", 5, 0),
            ("Status", 5, 1)
        ]

        for label_text, row, col in labels:
            label = tk.Label(user_info_frame, text=label_text, font=label_font)
            label.grid(row=row, column=col, pady=(label_padding, 0))  # Add top margin

        widget_width = 25  # Adjust the width as needed

        no_tiket_entry = tk.Entry(user_info_frame, width=widget_width)
        no_tiket_entry.grid(row=2, column=0, pady=(0, label_padding))  # Add bottom margin

        no_plat_entry = tk.Entry(user_info_frame, width=widget_width)
        no_plat_entry.grid(row=2, column=1, pady=(0, label_padding))  # Add bottom margin

        driver_entry = tk.Entry(user_info_frame, width=widget_width)
        driver_entry.grid(row=2, column=2, pady=(0, label_padding))  # Add bottom margin

        unit_entry = tk.Entry(user_info_frame, width=widget_width)
        unit_entry.grid(row=4, column=0, pady=(0, label_padding))  # Add bottom margin

        divisi_entry = tk.Entry(user_info_frame, width=widget_width)
        divisi_entry.grid(row=4, column=1, pady=(0, label_padding))  # Add bottom margin

        blok_entry = tk.Entry(user_info_frame, width=widget_width)
        blok_entry.grid(row=4, column=2, pady=(0, label_padding))  # Add bottom margin

        bunches_entry = tk.Entry(user_info_frame, width=widget_width)
        bunches_entry.grid(row=6, column=0, pady=(0, label_padding))  # Add bottom margin

        status_entry = ttk.Combobox(user_info_frame, values=["Inti", "Pihak Ketiga"], font=entry_font, width=18)
        status_entry.grid(row=6, column=1, pady=(0, label_padding))  # Span 3 columns and add bottom margin

        if not status_entry.get():
            status_entry.set("Inti")
    
        entry_fields = [no_tiket_entry, no_plat_entry, driver_entry, unit_entry, divisi_entry, blok_entry, bunches_entry, status_entry]

        style = ttk.Style()
        self.style.configure("Custom.TButton", padding=6, borderwidth=3, relief="groove", background="#2ecc71", font=("Helvetica", 10))

        button = ttk.Button(user_info_frame, style="Custom.TButton", width=widget_width, text="Simpan Data", command=lambda:  self.save_offline_log(no_tiket_entry.get(), no_plat_entry.get(), driver_entry.get(), unit_entry.get(), divisi_entry.get(), blok_entry.get(), bunches_entry.get(), status_entry.get(), entry_fields))
        button.grid(row=8, column=1, pady=(20, 30))

    def switch_frame(self):
        self.master.switch_frame(Frame1)

    def save_offline_log(self, tiket,plat, driver, unit, divisi, blok, bunches,  status, entry_fields):

        tiket = str(tiket).replace(' ', '')
        plat = str(plat).replace(' ', '')
        driver = str(driver).replace(' ', '')
        unit = str(unit).replace(' ', '')
        divisi = str(divisi).replace(' ', '')
        blok = str(blok).replace(' ', '')
        bunches = str(bunches).replace(' ', '')
        ownership = str(status)

        raw = info_truk(tiket, plat, driver, unit, divisi, blok, bunches, ownership,'None')
        raw['waktu_input'] = current_date.strftime('%Y-%m-%d %H:%M:%S')

        result = tiket + ';' + plat + ';'+ driver + ';'+ unit + ';'+ divisi  + ';'+ blok +';'+ bunches +';' + ownership + ';' + current_date.strftime('%Y-%m-%d %H:%M:%S') + ';None'
        
        try:
            with open(offline_log_dir, 'a') as file:
                file.write(str(raw) + '\n')
        except Exception as e:
            print("Error saving data to", offline_log_dir, ":", str(e))
                
        messagebox.showinfo("Success", "Data Tiket " + tiket + " Sukses Tersimpan di Table Utama!")  
        
        self.master.switch_frame(Frame1)

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Aplikasi Pos Grading")
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.login_frame = LoginFrame(self)

        self.current_frame = None  # Initialize current_frame to None
        # self.current_frame.pack(padx=50, pady=50)
        self.switch_frame(LoginFrame)  # Start with LoginFrame

        # Set the main window size and position based on the initial frame
        window_width = 500
        window_height = 500
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        

    def switch_frame(self, new_frame_class, output_inference=None, row_values=None):
        if self.current_frame is not None:
            self.current_frame.destroy()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        if new_frame_class == Frame3:
            self.current_frame = Frame3(self, output_inference, row_values)
        elif new_frame_class == RegisterFrame:
            self.current_frame = RegisterFrame(self)
        else:
            self.current_frame = new_frame_class(self)

        if isinstance(self.current_frame, Frame1):
            self.current_frame.pack(padx=50, pady=50)  # Add padding for Frame1
        elif isinstance(self.current_frame, EditBridgeFrame):
            self.current_frame.pack(padx=50, pady=50)
        else:
            self.current_frame.pack()

        if isinstance(self.current_frame, LoginFrame):
            window_width = 500
            window_height = 500
        elif isinstance(self.current_frame, RegisterFrame):
            window_width = 500
            window_height = 500
        elif isinstance(self.current_frame, ConfigFrame):
            window_width = 500
            window_height = 500
        else:
            window_width = screen_width
            window_height = screen_height

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

if __name__ == "__main__":
    app = MainWindow()
    app.option_add("*tearOff", False) # This is always a good idea
    # Create a style
    style = ttk.Style(app)

    # Import the tcl file
    app.tk.call("source", "forest-light.tcl")

    # Set the theme with the theme_use method
    style.theme_use("forest-light")
    app.mainloop()