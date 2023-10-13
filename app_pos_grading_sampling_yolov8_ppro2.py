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
import pymssql
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

def generate_report(raw, img_dir,class_count, totalJjg, brondol, brondolBusuk, dirt):

    prctgUnripe = 0
    prctgRipe = 0
    prctgEmptyBunch = 0
    prctgOverripe = 0
    prctgAbnormal = 0
    prctgKastrasi = 0
    prctgLongStalk = 0
    TotalRipeness = 0

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
    
    max_widthQr = 140
    if int(totalJjg) != 0:
        max_widthQr =150
        prctgUnripe = round((int(class_count[0]) / int(totalJjg)) * 100,2)
        prctgRipe =  round((int(class_count[1]) / int(totalJjg)) * 100,2)
        prctgEmptyBunch =  round((int(class_count[2]) / int(totalJjg)) * 100,2)
        prctgOverripe =  round((int(class_count[3]) / int(totalJjg)) * 100,2)
        prctgAbnormal =  round((int(class_count[4]) / int(totalJjg)) * 100,2)
        prctgLongStalk =  round((int(class_count[5]) / int(totalJjg)) * 100,2)
        prctgKastrasi = round((int(class_count[6]) / int(totalJjg)) * 100,2)
        
        TotalRipeness = round((int(class_count[1]) / int(totalJjg)) * 100,2)


    TabelAtas = [
        ['No Tiket',   str(no_tiket),'','','', 'Waktu Mulai',  str(dateStart)],
        ['Bisnis Unit',  str(bisnis_unit),'','','','Waktu Selesai', str(dateEnd)],
        ['Divisi',   str(divisi),'','','','No. Plat',str(no_plat)],
        ['Blok',  str(blok),'','','','Driver',str(nama_driver)],
        ['Status',  str(status)]
    ]

    colEachTable1 = [1.0*inch, 2.4*inch,  0.6*inch, 0.6*inch, 0.6*inch, 1.2*inch, 1.6*inch]
    page_width_points, page_height_points = letter

    # Convert the page width from points to inches
    page_width_inches = page_width_points / inch

    # print(f"Page width in inches: {page_width_inches:.2f} inches")
    TabelBawah = [
        ['Total\nJanjang', 'Ripe', 'Overripe', 'Unripe', 'Empty\nBunch','Abnormal','Kastrasi','Tangkai\nPanjang', 'Total\nRipeness'],
        [totalJjg, int(class_count[1]) , int(class_count[2]) , int(class_count[0]) ,int(class_count[3]) , int(class_count[4]) , int(class_count[6]) ,int(class_count[5]) , str(TotalRipeness) + ' % '],
        ['',  str(prctgRipe) + ' %', str(prctgOverripe)+ ' %', str(prctgUnripe) +' %', str(prctgEmptyBunch) +  ' %',  str(prctgAbnormal)+ ' %',  str(prctgKastrasi)+ ' %',str(prctgLongStalk)+ ' %','']
    ]

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

    
    name_pdf = str(img_dir) +  '.pdf'
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

    #untuk mengambil satu value dari duplicate value txt
    mill_names = list(set(mill_names))
    return mill_names

def store_list_mill(dir_mill, mill):

    if not dir_mill.exists():
        dir_mill.touch()

    selected_mill = mill.split(';')[0]

    with open(dir_mill, 'r') as file:
        lines = file.readlines()

    filtered_lines = [line for line in lines if line.strip().split(';')[0] == selected_mill]

    with open(dir_mill, 'w') as file:
        file.writelines(filtered_lines)

class Frame4(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

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
        self.server_entry = tk.Entry(self)
        self.server_entry.grid(row=3, column=1, pady=5, sticky="ew")

        database_label = tk.Label(self, text="Database")
        database_label.grid(row=4, column=0, sticky="w", pady=5)
        self.database_entry = tk.Entry(self) 
        self.database_entry.grid(row=4, column=1, sticky="ew")

        user_label = tk.Label(self, text="User")
        user_label.grid(row=5, column=0, sticky="w", pady=5)
        self.user_entry = tk.Entry(self) 
        self.user_entry.grid(row=5, column=1, sticky="ew")
        
        password_label = tk.Label(self, text="Password")
        password_label.grid(row=6, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(self, show="*") 
        self.password_entry.grid(row=6, column=1, sticky="ew")

        # toggle_button = tk.Button(self, text="", command=self.toggle_password_visibility)
        # toggle_button.grid(row=6, column=2, columnspan=2, pady=5)
        
        submit_button = tk.Button(self, text="Submit", command=self.change_config)
        submit_button.grid(row=7, column=0,sticky="w",   pady=(40, 0))
        
        back_button = tk.Button(self, text="Kembali ke Login", command=self.backToLogin)
        back_button.grid(row=7, column=1,sticky="w",   pady=(40, 0))

        self.feedback_label = tk.Label(self, text="", fg="red")
        self.feedback_label.grid(row=8, column=0, columnspan=2, pady=(30, 10))

        self.feedback_label_success = tk.Label(self, text="", fg="green")
        self.feedback_label_success.grid(row=8, column=0, columnspan=2, pady=(30, 10))

    def change_config(self):
        server = self.server_entry.get()
        userRoot = self.useroot_entry.get()
        user = self.user_entry.get()
        password = self.password_entry.get()
        database = self.database_entry.get()
        if not server or not user or not userRoot or not password or not database:
                self.feedback_label.config(text="Semua kolom harus diisi", fg="red")
                self.after(3000, self.clear_feedback)
                return  # Stop further execution
        # Define the default configuration
        default_config = {
            "server": "192.168.1.254\\DBSTAGING",
            "user": "usertesting",
            "password": "Qwerty@123",
            "database": "skmstagingdb"
        }

        if userRoot == 'grading':
            # Check if the configuration file exists
            config_file_path = Path(os.getcwd() + '/config/server.txt')  # Change this to your desired file path
            if os.path.isfile(config_file_path):
                # If the file exists, load the existing configuration
                with open(config_file_path, "r") as config_file:
                    existing_config = json.load(config_file)
            else:
                existing_config = default_config

            # Update the configuration with the values from Entry widgets
            
            existing_config["server"] = server
            existing_config["user"] = user
            existing_config["password"] = password
            existing_config["database"] = database

            # Save the updated configuration back to the file
            with open(config_file_path, "w") as config_file:
                json.dump(existing_config, config_file, indent=4)

            # Provide feedback to the user
            self.feedback_label_success.config(text="Configuration saved successfully!")

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

        # Add a dropdown field
        mill_label = tk.Label(self, text="Mill:")
        mill_label.grid(row=4, column=0, sticky="w", pady=5)
        self.mill_var = tk.StringVar()
        mill_choices = get_list_mill(log_mill, flag=False)
        self.mill_combobox = ttk.Combobox(self, textvariable=self.mill_var, values=mill_choices)

        if len(mill_choices) ==1:
            self.mill_var.set(mill_choices[0])
        self.mill_combobox.grid(row=4, column=1, pady=5, sticky="ew")

        self.feedback_label = tk.Label(self, text="", fg="red")
        self.feedback_label.grid(row=6, column=0, columnspan=2, pady=(30, 10))

        register_label = tk.Label(self, text="Belum memiliki akun ?", font=("Times New Roman", 12, "italic"), fg="blue", cursor="hand2")
        register_label.grid(row=5, column=0, columnspan=2, sticky="e")
        register_label.bind("<Button-1>", self.register_clicked)
        
        login_button = tk.Button(self, text="Login", command=self.login)
        login_button.grid(row=7, column=0, columnspan=2, sticky="w", pady=(40, 0))

        login_button = tk.Button(self, text="Config Server", command=self.config_server)
        login_button.grid(row=7, column=1, columnspan=2, sticky="w", pady=(40, 0))

        self.password_entry.bind("<Return>", lambda event: self.login())

    def clear_feedback(self):
        if self.feedback_label.winfo_exists():
            self.feedback_label.config(text="")

    def register_clicked(self, event):
        self.master.switch_frame(RegisterFrame)

    def config_server(self):
        self.master.switch_frame(Frame4)

    def login(self):
        user = self.username_entry.get()
        password = self.password_entry.get()
        mill = self.mill_combobox.get()

        if not user or not password or not mill:
            self.feedback_label.config(text="Semua kolom harus diisi", fg="red")
            self.after(3000, self.clear_feedback)
            return

        user_exists = False
        with open(log_data_user, 'r') as log_file:
            for line in log_file:
                stored_user, stored_hashed_password = line.strip().split(';')
                if stored_user == user:
                    user_exists = True

                    hashed_password = hashlib.sha256(password.encode()).hexdigest()
                    if hashed_password == stored_hashed_password:
                        # print("Login successful")
                        store_list_mill(log_mill, mill)
                        self.master.switch_frame(Frame1)
                    else:
                        print("Incorrect password")
                        self.feedback_label.config(text="Incorrect password", fg="red")
                    break

        if not user_exists:
            print("User not found")
            self.feedback_label.config(text="User not found", fg="red")

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
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                strUser = user + ';' + hashed_password

                log_file_path = log_data_user
                user_exists = False

                with open(log_file_path, 'r') as log_file:
                    for line in log_file:
                        stored_user, _ = line.strip().split(';')
                        if stored_user == user:
                            user_exists = True
                            break

                if user_exists:
                    self.feedback_label.config(text="User tersebut sudah terdaftar", fg="red")
                else:
                    with open(log_file_path, 'a') as log_file:
                        log_file.write(strUser + '\n')  # Append the result to the log file with a newline character
                        # print("Data saved successfully to", log_file_path)
                        self.feedback_label_success.config(text="User baru tersimpan", fg="green")
            else:    
                print('Tidak dapat menyimpan User!')
                self.feedback_label.config(text="Tidak dapat menyimpan User!", fg="red")

            self.after(3000, self.clear_feedback)

def process_data_offline( data):
        arr_data  = []
        index = 1
        for line in data:
            values = line.strip().split(';')
            values.insert(0, index)
            arr_data.append(tuple(values))
            index += 1

        sorted_data = sorted(arr_data, key=lambda x: x[9], reverse=True)
        return sorted_data

def connect_to_database():
    global status_mode
    
    try:
        with open(Path(os.getcwd() + '/config/server.txt'), "r") as file:
            config = json.load(file)

        server = config["server"]
        user = config["user"]
        password = config["password"]
        database = config["database"]

        timeout = 0.5
        
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
                print(f"Error connecting to the database: {str(e)}")
                 
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
                return process_data_offline(data)

source = None  # Initialize source to None initially
class Frame1(tk.Frame):
    
    def __init__(self, master):
        super().__init__(master)
        global source
        self.clicked_buttons = []
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
        cctv_choices = get_list_mill(log_mill, flag=True)
        cctv_choices.append('Video - Test')
        self.cctv_combobox = ttk.Combobox(self, textvariable=self.mill_var, values=cctv_choices)
        self.mill_var.set(cctv_choices[0])
        source = self.mill_var.get()
        self.cctv_combobox.grid(row=0, column=5)

        self.cctv_combobox.bind("<FocusOut>", self.on_combobox_focus_out)

        self.mode_label = tk.Label(top_frame, text="", font=("Helvetica", 16, "bold"))
        self.mode_label.grid(row=0, column=3)
        
        self.refresh_button = ttk.Checkbutton(top_frame, text="REFRESH", variable=tk.IntVar(value=1), style="ToggleButton", command=self.refresh_data)
        self.refresh_button.grid(row=0, column=5)       
        
        top_frame.grid_columnconfigure(5, weight=20)

        
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
        
    

    def on_combobox_focus_out(self, event):
        global source  # Declare 'source' as a global variable
        selected_value = self.mill_var.get()
        self.selected_combobox_value = selected_value  # Store the selected value in a class variable
        # print("Selected value:", selected_value)
        
        # Update 'source' to the current combobox value
        source = selected_value


    def populate_treeview(self, arrData):
        
        custom_font = tkFont.Font(family="Helvetica", size=11)
        
        for i, data in enumerate(arrData, start=1):
            # print('lazy')
            # print(data[-1])
            item = self.tree.insert("", "end", values=data, tags=i)
            self.tree.set(item, "#1", str(i))
            if data[-1] == None or data[-1] == 'None':
                self.tree.set(item, "#11", "READY")
                self.tree.tag_configure(i, background="#FFFFFF", font=custom_font)  # Change row color 
            else:
                self.tree.tag_configure(i, background="#94c281", font=custom_font)  # Set background color to green
                self.tree.set(item, "#11", "DONE")
            self.tree.tag_bind(i, "<Double-Button-1>", lambda event, row_item=item: self.update_row(row_item, event))     

    def pull_master(self, table, code, name, file_name):
        connection = connect_to_database()

        if isinstance(connection, pymssql.Connection):
            sql_query = f"SELECT {str(code)} , {str(name)}  FROM {str(table)} WHERE AI_pull_time IS NULL"
            cursor = connection.cursor()
            cursor.execute(sql_query)
            records = cursor.fetchall()
            connection.close()
            
            if len(records) > 0 or not file_name.exists():
                sql_query = f"SELECT {str(code)} , {str(name)}  FROM {str(table)}"
                connection = connect_to_database()  
                cursor = connection.cursor()
                cursor.execute(sql_query)
                records = cursor.fetchall()
                connection.close()
                mapping = {r[str(code)]: r[str(name)] for r in records}
                
                file_name.touch()
                with open(file_name, 'w') as file:
                    for code, name in mapping.items():
                        file.write(f"{code}:{name}\n")
                connection = connect_to_database()
                update_query = f"UPDATE {str(table)} SET AI_pull_time = GETDATE() WHERE AI_pull_time IS NULL"
                cursor = connection.cursor()
                try:
                    cursor.execute(update_query)
                    connection.commit()  # Commit the transaction                
                except Exception as e:
                    connection.rollback()  # Rollback the transaction in case of an error
                    print(f"Error executing update query: {str(e)}")
                connection.close()
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

    def pull_data_ppro(self):
        start_date = datetime.datetime(2023, 8, 24, 7, 0, 0)
        current_date = datetime.datetime.now().date()
        start_time = datetime.time(7, 0, 0)
        #start_date = datetime.datetime.combine(current_date, start_time)
        # print(start_date)
        end_date = start_date + datetime.timedelta(days=1)
        # print(end_date)
        connection = connect_to_database()
        
        if isinstance(connection, pymssql.Connection):
            sql_query = "SELECT * FROM MOPweighbridgeTicket_Staging WHERE Ppro_push_time >= %s AND Ppro_push_time < %s"
            cursor = connection.cursor()
            cursor.execute(sql_query, (start_date, end_date))
            records = cursor.fetchall()
            connection.close()
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

        self.button_input = ttk.Button(self.top_frame, text="Input Data Truk", style="Accent.TButton", command=self.switch_frame2)
        self.button_input.grid(row=0, column=4)

    def refresh_data(self):
        self.tree.delete(*self.tree.get_children())
        master_bunit = self.pull_master('MasterBunit_staging','Ppro_BUnitCode','Ppro_BUnitName',data_bunit)
        master_div = self.pull_master('MasterDivisi_Staging','Ppro_DivisionCode','Ppro_DivisionName',data_div)
        master_block = self.pull_master('MasterBlock_Staging','Ppro_FieldCode','Ppro_FieldName',data_block)
        record = self.pull_data_ppro()
        self.master.title(f"Sistem Aplikasi Pos Grading - {status_mode.capitalize()}")
        if status_mode == 'online':
            arr_data = self.process_data(record, master_bunit, master_div, master_block)
            self.refresh_button = ttk.Checkbutton(self.top_frame, text="REFRESH", variable=tk.IntVar(value=1), style="ToggleButton", command=self.refresh_data)
            self.refresh_button.grid(row=0, column=5)

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
                    messagebox.showinfo("Alert", f"File Tidak dapat ditemukan")  # Show success message


    def run_script(self, row_item, row_id, row_values):

        global source, date_start_conveyor
        date_start_conveyor = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output_inference = None
        try:
            
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

        self.master.title(f"Sistem Aplikasi Pos Grading - {status_mode.capitalize()}")

        counter_per_class = None
        img_dir = None
        raw = None
        global WBTicketNo 
        global totalJjg
        
        with open(save_dir_txt, 'r') as file:
            raw = file.readline()
    
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
            submit_button = tk.Button(self, text="SUBMIT", command=lambda: self.save_and_switch(class_name, counter_per_class, row_values, img_dir))
        else:
            submit_button = tk.Button(self, text="SUBMIT", command=lambda: self.save_offline_and_switch(counter_per_class, row_values[1:-1], row_values, img_dir))
        
        submit_button.grid(row=19, column=1, columnspan=4, sticky="ew")

    #     self.master.protocol("WM_DELETE_WINDOW", lambda: self.on_closing())
    
    # def on_closing(self):
    #     messagebox.showinfo("Alert", "Submit Data terlebih dahulu !")  # Show success message
        
    #     pass

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
        global totalJjg

        # Values for the new row
        new_row = {
            'AI_NoTicket': str(WBTicketNo),
            'AI_Grading': str(intCat),
            'AI_JanjangSample': str(totalJjg), 
            'AI_TotalJanjang': str(totalJjg),
            'AI_Janjang': str(intVal)
        }

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

    def save_and_switch(self, class_name, count_per_class, row_values, img_dir):
        global date_end_conveyor
        date_end_conveyor = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        brondol = self.brondolanEntry.get()
        brondolBusuk = self.brondoalBusukEntry.get()
        dirt = self.dirtEntry.get()
        
        brondol = remove_non_numeric(brondol)
        brondolBusuk = remove_non_numeric(brondolBusuk)
        dirt = remove_non_numeric(dirt)

        if not brondol:
            brondol = 0
        if not brondolBusuk:
            brondolBusuk = 0
        if not dirt:
            dirt = 0

        result = ';'.join(map(str, row_values)) + ';'
        result += ';'.join(map(str, count_per_class)) + ';'
        result += str(brondol) + ';'
        result += str(brondolBusuk ) + ';'
        result += str(dirt)
        
        log_file_path = log_dir  

        try:
            with open(log_file_path, 'a') as log_file:
                log_file.write(result + '\n')  # Append the result to the log file with a newline character
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

        generate_report(result, img_dir,count_per_class, totalJjg, brondol, brondolBusuk, dirt)

        threading.Thread(target=self.run_send_pdf_in_background).start()

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

    def save_offline_and_switch(self, count_per_class, row_values, row_values_full,  img_dir):
        row_values_subset = ';'.join(map(str, row_values))
        brondol = self.brondolanEntry.get()
        brondolBusuk = self.brondoalBusukEntry.get()
        dirt = self.dirtEntry.get()

        brondol = remove_non_numeric(brondol)
        brondolBusuk = remove_non_numeric(brondolBusuk)
        dirt = remove_non_numeric(dirt)

        result = list(row_values_full)

        if not brondol:
            brondol = 0
        if not brondolBusuk:
            brondolBusuk = 0
        if not dirt:
            dirt = 0

        strInputan = str(brondol) + ';'
        strInputan += str(brondolBusuk) + ';'
        strInputan += str(dirt)
        
        count_class = ';'.join(map(str, count_per_class)) + ';'
        with open(offline_log_dir, 'r') as log_file:
            data = log_file.readlines()

        for line_number, line in enumerate(data, start=1):
            values = line.strip().split(';')
            tuple_val = tuple(values[:-1]) 
            #membandingkan row clicked dgn row didalam txt jika sama ubah status None jadi ready
            if tuple_val == row_values:
                data[line_number - 1] = row_values_subset + ';READY;' + count_class + strInputan  + '\n'
                with open(offline_log_dir, 'w') as log_file:
                    log_file.writelines(data)
                break
        
        messagebox.showinfo("Success", "Data Sukses Tersimpan !")  # Show success message
        generate_report(result, img_dir,count_per_class, totalJjg, brondol, brondolBusuk, dirt)

        threading.Thread(target=self.run_send_pdf_in_background).start()

        self.master.switch_frame(Frame1)
        
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
        status = str(status)

        result = tiket + ';' + plat + ';'+ driver + ';'+ unit + ';'+ divisi  + ';'+ blok +';'+ bunches +';' + status + ';' + current_date.strftime('%Y-%m-%d %H:%M:%S') + ';None'

        try:
            with open(offline_log_dir, 'a') as file:
                file.write(result + '\n')
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
        else:
            self.current_frame.pack()

        if isinstance(self.current_frame, LoginFrame):
            window_width = 500
            window_height = 500
        elif isinstance(self.current_frame, RegisterFrame):
            window_width = 500
            window_height = 500
        elif isinstance(self.current_frame, Frame4):
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