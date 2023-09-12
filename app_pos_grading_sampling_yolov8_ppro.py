import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.messagebox import YES, showinfo
import os
from pathlib import Path
import datetime
import threading
import tkinter.font as tkFont
import subprocess
import pymssql


current_date = datetime.datetime.now()

# Format the date as yyyy-mm-dd
formatted_date = current_date.strftime('%Y-%m-%d')

log_inference = Path(os.getcwd() + '/log_inference_sampling')

log_inference.mkdir(parents=True, exist_ok=True)  # make dir
log_dir = Path(os.getcwd() + '/log_inference_sampling/' + formatted_date  + '_log.TXT')

if not log_dir.exists():
    log_dir.touch()

pdf_dir = Path(os.getcwd() + '/hasil/' + formatted_date)

pdf_dir.mkdir(parents=True, exist_ok=True)  # make dir

def pullDataPPro():
    conn = pymssql.connect(
    server='192.168.1.254\DBSTAGING',
    user='usertesting',
    password='Qwerty@123',
    database='skmstagingdb',
    as_dict=True
        )
    SQL_QUERY = """
    SELECT *
    FROM MOPweighbridgeTicket_Staging
    WHERE AI_pull_time IS NULL;
    """
    cursor = conn.cursor()
    cursor.execute(SQL_QUERY)

    return cursor.fetchall()


def save_info_truk(header, log_inference):
    header_str = str(header) 

    if not os.path.exists(log_inference):
        os.makedirs(log_inference)
    if not os.path.exists(log_inference):
        f = open(log_inference, "a")
        f.write("")
        f.close()
    with open(log_inference, 'r') as z:
        content = z.readlines()
        wr = open(log_inference, "a")
        try:
            if len(content[0].strip()) == 0 | content[0] in ['\n', '\r\n']:
                wr.write(header_str)
            else:
                wr.write(header_str)
        except:
            wr.write(header_str)
        wr.close()

def enter_data(self, tiket,plat, driver, unit, divisi, blok, status, entry_fields):

    tiket = str(tiket).replace(' ', '')
    plat = str(plat).replace(' ', '')
    driver = str(driver).replace(' ', '')
    unit = str(unit).replace(' ', '')
    divisi = str(divisi).replace(' ', '')
    blok = str(blok).replace(' ', '')
    status = str(status).replace(' ', '')


    # if tiket != '' and plat != '' and driver != '' and unit != '' and divisi != '' and blok != '' and status != '':
    save_info_truk(tiket + ";" + plat+ ";" + driver + ";" + unit+ ";" + divisi + ";" +blok+ ";" + status +';Mulai\n', str(log_dir))
    messagebox.showinfo("Success", "Data Tiket " + tiket + " Sukses Tersimpan di Table Utama!")  # Show success message
    # for entry_field in entry_fields:
    #     entry_field.delete(0, tk.END)
    
    self.master.switch_frame(Frame1)
    # else:
    #     messagebox.showinfo("Warning !!!", "Semua Kolom Wajib Tidak Boleh Kosong")

def save_txt(self, info_truk,counter, brondol, brondolBusuk, dirt):
    print(info_truk)
    # print(counter)
    # print(brondol)
    # print(brondolBusuk)
    # print(dirt)
    # print(dir)



    # messagebox.showinfo("Success", "Data Sukses Tersimpan dan Terkirim")  # Show success message

class Frame1(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.grid(row=1, column=1, rowspan=100,sticky="ns")
        
        columns = ('notiket', 'nopol', 'driver', 'b_unit','divisi', 'field', 'bunches', 'ownership', 'pushtime', 'action')
        
        self.tree = ttk.Treeview(self, columns=columns, yscrollcommand=self.scrollbar.set, selectmode="none",  show="headings")
        
        self.style = ttk.Style(self)
        self.row_height = 80  # Set the desired row height
        self.detail_window = None
        
        self.style.configure("Treeview", rowheight=self.row_height)
        # self.tree.heading("#1", text="No")
        self.tree.heading("#1", text="Nomor Tiket")
        self.tree.heading("#2", text="Nomor Polisi")
        self.tree.heading("#3", text="Nama Drvier")
        self.tree.heading("#4", text="Bisnis Unit")
        self.tree.heading("#5", text="Divisi")
        self.tree.heading("#6", text="Field")
        self.tree.heading("#7", text="Bunches")
        self.tree.heading("#8", text="Ownership")
        self.tree.heading("#9", text="Push Time")
        self.tree.heading("#10", text="Aksi")
        

        # Adjust column widths
        # self.tree.column("no", width=50)         
        self.tree.column("notiket") 
        self.tree.column("nopol") 
        self.tree.column("driver") 
        self.tree.column("b_unit") 
        self.tree.column("divisi") 
        self.tree.column("field") 
        self.tree.column("bunches") 
        self.tree.column("ownership") 
        self.tree.column("pushtime") 
        self.tree.column("action") 
        # self.tree.column("eb", width=150) 
        # self.tree.column("ab", width=150) 
        # self.tree.column("tp", width=150)
        

        # self.clicked_buttons = set()  # Set to keep track of clicked buttons

        self.title_label = tk.Label(self, text="Tabel List Truk FFB Grading Sampling SCM", font=("Helvetica", 16, "bold"))
        self.title_label.grid(row=0, column=0, padx=700, pady=10, sticky="w")
        self.logo_image = tk.PhotoImage(file=Path(os.getcwd() + '/default-img/Logo-CBI(4).png'))  # Replace "logo.png" with your image file path
        self.logo_image = self.logo_image.subsample(2, 2)  # Adjust the subsample values to resize the image
        logo_label = tk.Label(self, image=self.logo_image)
        logo_label.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        self.logo_image2 = tk.PhotoImage(file=Path(os.getcwd() + '/default-img/LOGO-SRS(1).png'))
        self.logo_image2 = self.logo_image2.subsample(2, 2)
        logo_label2 = tk.Label(self, image=self.logo_image2)
        logo_label2.grid(row=0, column=0, padx=160, pady=15, sticky="nw")  # Change column to 0 and sticky to "ne"


        # Inside your __init__ method
        self.style = ttk.Style()
        self.style.configure("inputForm.TButton", padding=6, borderwidth=3, relief="groove", background="#2ecc71", font=("Helvetica", 10))

         # Create a styled button
        self.button = ttk.Button(self, text="Input Data Truk Grading", command=self.switch_frame, style="inputForm.TButton")
        self.button.grid(row=0, column=0, padx=30, pady=30, sticky="ne")

        self.style = ttk.Style()
        self.style.configure("refresh.TButton", padding=6, borderwidth=3, relief="groove", font=("Helvetica", 10))

         # Create a styled button
        self.button = ttk.Button(self, text="Refresh", style="refresh.TButton", command=self.refresh_data)
        self.button.grid(row=0, column=0, padx=200, pady=30, sticky="ne")

        self.refresh_data()

        self.tree.grid(row=1, column=0, columnspan=3, sticky="nsew")  # Use columnspan to span all columns

        self.scrollbar.config(command=self.tree.yview)
        self.scrollbar.grid(row=1, column=3, rowspan=1, sticky="ns")  # Adjust rowspan as needed

        self.footer_frame = tk.Frame(self)
        self.footer_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=40)  # Use columnspan to span all columns

        footer_label = tk.Label(self.footer_frame, text="Copyright @ Digital Architect 2023", font=("Helvetica", 14, "bold"))
        footer_label.pack()

        self.last_update_model = tk.Frame(self)
        self.last_update_model.grid(row=2, column=0, columnspan=3, sticky="nw", pady=10)  # Use columnspan to span all columns

        last_model = tk.Label(self.last_update_model, text="Tanggal Update Model AI : 08 Agustus 2023",font=("Helvetica", 12, "italic"))
        last_model.pack()
        
        self.clicked_buttons = set()  # Set to keep track of clicked buttons
        
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.running_script = False  # Flag to track if script is running


    def refresh_data(self):
        self.tree.delete(*self.tree.get_children())
        record = pullDataPPro()

        arrData = []
        for data in record:

            WBTicketNo = data['WBTicketNo']
            VehiclePoliceNO = data['VehiclePoliceNO']
            DriverName = data['DriverName']
            BUnit = data['BUnitCode']
            Divisi = data['DivisionCode']
            Field = data['Field']
            Bunches = data['Bunches']
            Ownership = data['Ownership']
            push_time = data['Ppro_push_time']
            pull_time = data['AI_pull_time']
            
            arrData.append(( WBTicketNo, VehiclePoliceNO, DriverName, BUnit, Divisi, Field,Bunches, Ownership, push_time , pull_time))
           


        self.after(10, lambda: self.populate_treeview(arrData))

    def populate_treeview(self, arrData):

        custom_font = tkFont.Font(family="Helvetica", size=11)
        key = 0
        
        for i, data in enumerate(arrData, start=1):
            item = self.tree.insert("", "end", values=data, tags=i)
            self.tree.tag_bind(i, "<ButtonRelease-1>", lambda event, row_item=item: self.update_row(row_item))

            if "Selesai" in data:
                self.tree.tag_configure(i, background="#94c281", font=custom_font)  # Set background color to green
            else:
                self.tree.tag_configure(i, background="#FFFFFF", font=custom_font)  # Change row color

            key += 1

        
    def update_row(self, row_item):
        row_id = int(self.tree.item(row_item, "tags")[0])  # Get row ID from tags
        
        if row_id not in self.clicked_buttons and not self.running_script:
            
            row_values = self.tree.item(row_item, "values")  # Get values of the row
            


            # self.tree.item(row_item, values=(plat_est,'', "Sedang Berjalan"))
            self.tree.tag_configure(row_id, background="#cccdce")  # Change row color
            self.clicked_buttons.add(row_id)

            self.running_script = True  # Set flag to indicate script is running
            self.button.config(state=tk.DISABLED)  # Disable the button
            
            

            thread = threading.Thread(target=self.run_script, args=(row_item, row_id, row_values))
            thread.start()

    def run_script(self, row_item, row_id, row_values):
        
        # plat_est = row_values[0]

        output_inference = None
        try:
            
            result = subprocess.run(['python', '8-track-batas_2.py', '--pull_data', str(row_values)], 
                            capture_output=True, 
                            text=True, 
                            check=True)

            output_inference = result.stdout
            # script_output = os.popen(shell_command).read()
            # self.running_script = False
            # self.button.config(state=tk.NORMAL)

        except subprocess.CalledProcessError as e:
            print("Error running other_script.py:", str(e))
        # finally:    
       
            

            # try:
            #     subprocess.run(['python', str(Path(os.getcwd())) +'/send_pdf_inference.py'], check=True)
            # except subprocess.CalledProcessError as e:
            #     print("Error running other_script.py:", str(e))
            
            # if os.path.exists(log_dir):
            #         with open(log_dir, 'r') as z:
            #             content = z.readlines()   
            #             targetLine = content[line_txt]
                        
            #             # print(targetLine)
            #             wr = open(log_dir, "w")
            #             content[line_txt]  = targetLine.replace("Mulai", "Selesai")
            #             wr.writelines(content)
            #             wr.close()

            # self.tree.tag_configure(row_id, background="#94c281")
            # self.running_script = False  # Reset the flag
            # self.button.config(state=tk.NORMAL)  # Enable the button back

            # if os.path.exists(log_dir):
            #         with open(log_dir, 'r') as z:
            #             content = z.readlines()   
            #             targetLine = content[line_txt]
                        
            #             parts = targetLine.strip().split(';')

            #             status_ramp = parts[7]
            #             waktu_mulai = parts[15]
            #             waktu_selesai = parts[16]
            #             rp = int(parts[8])
            #             ur = int(parts[9])
            #             ovr = int(parts[10])
            #             eb = int(parts[11])
            #             ab = int(parts[12])
            #             ks = int(parts[13])
            #             tp = int(parts[14])
            #             total_deteksi = rp + ur + ovr + eb + ab + ks
                        
            # self.tree.item(row_item, values=(plat_est, '',status_ramp, waktu_mulai, waktu_selesai, total_deteksi, rp, ur, ovr, eb, ab, tp))
# Create a new tkinter Toplevel window
        new_window = tk.Toplevel(self.master)
        new_window.title("New Window")

        # Disable all widgets within Frame1
        self.disable_widgets(self.master.frame1)

        # Create Frame3 for the new window content
        frame3 = Frame3(new_window, row_values, output_inference)
        frame3.pack()

        # Grab focus and disable interactions with the new window
        new_window.grab_set()

        # Wait for the new window to be closed
        new_window.wait_window()

    def disable_widgets(self, parent):
        for widget in parent.winfo_children():
            if isinstance(widget, (tk.Entry, tk.Button, tk.Checkbutton)):
                widget.configure(state="disabled")
            else:
                self.disable_widgets(widget)

    def switch_frame(self):
        self.master.switch_frame(Frame2)
class Frame3(tk.Frame):
    def __init__(self, master, row_values, output_inference):
        super().__init__(master)

        self.master.geometry("800x700")

        first_list_end = output_inference.index("]") + 1

        # Split the string into two parts based on the first list end index
        count_per_class = eval(output_inference[:first_list_end])
        class_names = eval(output_inference[first_list_end:])

        totalJjg = sum(count_per_class)

        WBTicketNo = row_values[0]
        VehiclePoliceNO = row_values[1]
        DriverName = row_values[2]
        BUnit = row_values[3]
        Divisi = row_values[4]
        Field = row_values[5]
        Bunches = row_values[6]
        Ownership = row_values[7]
        push_time = row_values[8]
        pull_time = row_values[9]

        # Title for Frame3
        title_label = tk.Label(self, text="Rekap Data Deteksi FFB Grading dengan AI ", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(20, 10))

        
        subtitle1 = tk.Label(self, text="Informasi Truk : ",  font=("Helvetica", 13, "italic"))
        subtitle1.grid(row=1, column=0,columnspan=4, sticky="w", pady=5)

        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=2, column=0, columnspan=4, sticky="ew")
        
        label1 = tk.Label(self, text="Nomor Tiket : ")
        label1.grid(row=3, column=0, sticky="w", pady=5)

        param_label1 = tk.Label(self, text=WBTicketNo)
        param_label1.grid(row=3, column=1,sticky="w", pady=5)

        label2 = tk.Label(self, text="Nomor Polisi : ")
        label2.grid(row=3, column=2, sticky="w", pady=5)

        param_label2 = tk.Label(self, text=VehiclePoliceNO)
        param_label2.grid(row=3, column=3,sticky="w", pady=5)

       
        label3 = tk.Label(self, text="Nama Driver : ")
        label3.grid(row=4, column=0, sticky="w", pady=5)

       
        param_label3 = tk.Label(self, text=DriverName)
        param_label3.grid(row=4, column=1,sticky="w", pady=5)

        label4 = tk.Label(self, text="Bisnis Unit : ")
        label4.grid(row=4, column=2, sticky="w", pady=5)

       
        param_label4 = tk.Label(self, text=BUnit)
        param_label4.grid(row=4, column=3,sticky="w", pady=5)

       
        label5 = tk.Label(self, text="Divisi : ")
        label5.grid(row=5, column=0, sticky="w",  pady=5)

        param_label5 = tk.Label(self, text=Divisi)
        param_label5.grid(row=5, column=1,sticky="w",  pady=5)

        label6 = tk.Label(self, text="Field : ")
        label6.grid(row=5, column=2, sticky="w",  pady=5)

        param_label6 = tk.Label(self, text=Field)
        param_label6.grid(row=5, column=3, sticky="w", pady=5)

        label7 = tk.Label(self, text="Bunches : ")
        label7.grid(row=6, column=0, sticky="w",  pady=5)

        param_label7 = tk.Label(self, text=Bunches)
        param_label7.grid(row=6, column=1, sticky="w", pady=5)

        label8 = tk.Label(self, text="Ownership : ")
        label8.grid(row=6, column=2, sticky="w",  pady=5)

        param_label8 = tk.Label(self, text=Ownership)
        param_label8.grid(row=6, column=3,sticky="w",  pady=5)

        label9 = tk.Label(self, text="Pull Time : ")
        label9.grid(row=7, column=0, sticky="w",  pady=5)

        param_label9 = tk.Label(self, text=pull_time)
        param_label9.grid(row=7, column=1,sticky="w",  pady=5)
        

        subtitle2 = tk.Label(self, text="Hasil Deteksi Per Kategori : ",  font=("Helvetica", 13, "italic"))
        subtitle2.grid(row=8, column=0,columnspan=4, sticky="w",  pady=5)

        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=9, column=0, columnspan=4, sticky="ew")
        
        label9 = tk.Label(self, text="Total Janjang : ")
        label9.grid(row=10, column=0, sticky="w",  pady=5)

        param_label9 = tk.Label(self, text=str(totalJjg))
        param_label9.grid(row=10, column=1, sticky="w",  pady=5)

        label10 = tk.Label(self, text="Unripe : ")
        label10.grid(row=10, column=2, sticky="w",  pady=5)

        param_label10 = tk.Label(self, text=count_per_class[0])
        param_label10.grid(row=10, column=3,  sticky="w", pady=5)

        label11 = tk.Label(self, text="Ripe : ")
        label11.grid(row=11, column=0, sticky="w",  pady=5)

        param_label11 = tk.Label(self, text=count_per_class[1])
        param_label11.grid(row=11, column=1, sticky="w",  pady=5)

        label12 = tk.Label(self, text="Overripe : ")
        label12.grid(row=11, column=2, sticky="w",  pady=5)

        param_label12 = tk.Label(self, text=count_per_class[2])
        param_label12.grid(row=11, column=3,  sticky="w", pady=5)

        label13 = tk.Label(self, text="Empty Bunch : ")
        label13.grid(row=12, column=0, sticky="w",  pady=5)

        param_label13 = tk.Label(self, text=count_per_class[3])
        param_label13.grid(row=12, column=1, sticky="w",  pady=5)

        label14 = tk.Label(self, text="Abnormal : ")
        label14.grid(row=12, column=2, sticky="w",  pady=5)

        param_label14 = tk.Label(self, text=count_per_class[4])
        param_label14.grid(row=12, column=3, sticky="w",  pady=5)

        label15 = tk.Label(self, text="Tangkai Panjang : ")
        label15.grid(row=13, column=0, sticky="w",  pady=5)

        param_label15 = tk.Label(self, text=count_per_class[5])
        param_label15.grid(row=13, column=1, sticky="w",  pady=5)

        label16 = tk.Label(self, text="Kastrasi : ")
        label16.grid(row=13, column=2, sticky="w",  pady=5)

        param_label16 = tk.Label(self, text=count_per_class[6])
        param_label16.grid(row=13, column=3, sticky="w",  pady=5)

        subtitle3 = tk.Label(self, text="Input Tambahan : ",  font=("Helvetica", 13, "italic"))
        subtitle3.grid(row=14, column=0,columnspan=4, sticky="w",  pady=5)

        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=15, column=0, columnspan=4, sticky="ew")

        label17 = tk.Label(self, text="Brondolan : ")
        label17.grid(row=16, column=0, sticky="w",  pady=5)

        brondolanEntry = tk.Entry(self)
        brondolanEntry.grid(row=16, column=1, sticky="w", pady=5)

        unit_label = tk.Label(self, text="kg")
        unit_label.grid(row=16, column=2, sticky="w", pady=5)

        label18 = tk.Label(self, text="Brondolan Busuk : ")
        label18.grid(row=17, column=0, sticky="w",  pady=5)

        brondoalBusukEntry = tk.Entry(self)
        brondoalBusukEntry.grid(row=17, column=1, sticky="w", pady=5)

        unit_label = tk.Label(self, text="kg")
        unit_label.grid(row=17, column=2, sticky="w", pady=5)

        label19 = tk.Label(self, text="Dirt/Kotoran : ")
        label19.grid(row=18, column=0, sticky="w",  pady=5)

        dirtEntry = tk.Entry(self)
        dirtEntry.grid(row=18, column=1,  sticky="w",pady=5)

        unit_label = tk.Label(self, text="kg")
        unit_label.grid(row=18, column=2, sticky="w", pady=5)

        submit_button = tk.Button(self, text="Submit", command=lambda: save_txt(row_values, count_per_class, brondolanEntry.get(), brondoalBusukEntry.get(), dirtEntry.get(), pdf_dir))
        submit_button.grid(row=19, column=0, columnspan=4,sticky="w", pady=50)


        
class Frame2(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

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
            ("Status", 5, 0)
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

        status_entry = ttk.Combobox(user_info_frame, values=["Inti", "Eksternal"], font=entry_font, width=20)
        status_entry.grid(row=6, column=0, pady=(0, label_padding))  # Span 3 columns and add bottom margin

        entry_fields = [no_tiket_entry, no_plat_entry, driver_entry, unit_entry, divisi_entry, blok_entry, status_entry]

        style = ttk.Style()
        self.style.configure("Custom.TButton", padding=6, borderwidth=3, relief="groove", background="#2ecc71", font=("Helvetica", 10))

        button = ttk.Button(user_info_frame, style="Custom.TButton", width=widget_width, text="Simpan Data", command=lambda:  enter_data(self, no_tiket_entry.get(), no_plat_entry.get(), driver_entry.get(), unit_entry.get(), divisi_entry.get(), blok_entry.get(), status_entry.get(), entry_fields))
        button.grid(row=8, column=1, pady=(20, 30))

    def switch_frame(self):
        self.master.switch_frame(Frame1)

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Aplikasi Pos Grading")  # Set the title here
        
        # Set the desired width and height for the window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 1)  # 90% of the screen width
        window_height = int(screen_height * 1)  # 90% of the screen height
        
        self.geometry(f"{window_width}x{window_height}")
        
        self.frame1 = Frame1(self)
        self.frame2 = Frame2(self)
        self.current_frame = self.frame1
        self.current_frame.pack()

    def switch_frame(self, new_frame_class):
        self.current_frame.destroy()
        self.current_frame = new_frame_class(self)
        self.current_frame.pack()

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()