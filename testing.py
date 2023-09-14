from itertools import count
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
import re
import hashlib
from urllib.request import urlopen
import json

url = "https://srs-ssms.com/grading_ai/get_list_mill.php"

current_date = datetime.datetime.now()

# Format the date as yyyy-mm-dd
formatted_date = current_date.strftime('%Y-%m-%d')

log_inference = Path(os.getcwd() + '/hasil')

log_inference.mkdir(parents=True, exist_ok=True) 
log_dir = Path(os.getcwd() + '/hasil/' + formatted_date  + '/'+ formatted_date+'_log.TXT')

log_data = Path(os.getcwd() + '/data')
log_mill = Path(str(log_data) + '/mill_mapping.txt')

dir_user = Path(os.getcwd() + '/user')
dir_user.mkdir(parents=True, exist_ok=True)  
log_data_user = Path(str(dir_user) + '/data.txt')

if not log_data_user.exists():
    log_data_user.touch()

log_inference.mkdir(parents=True, exist_ok=True)  
log_dir = Path(os.getcwd() + '/hasil/' + formatted_date  + '/'+ formatted_date+'_log.TXT')

if not log_dir.exists():
    log_dir.touch()


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

        self.password_entry.bind("<Return>", lambda event: self.login())

    def clear_feedback(self):
        if self.feedback_label.winfo_exists():
            self.feedback_label.config(text="")

    def register_clicked(self, event):
        self.master.switch_frame(RegisterFrame)

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
                        print("Login successful")
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
        
        login_label = tk.Label(self, text="Register New User", font=("Times New Roman", 20, "bold"))
        login_label.grid(row=0, column=0, columnspan=2, sticky='w', pady=(40, 0))

        login_label = tk.Label(self, text="Silakan isi untuk menambahkan user ke sistem!", font=("Times New Roman", 12, "italic"))
        login_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=10)

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
        
        login_button = tk.Button(self, text="Submit", command=self.register)
        login_button.grid(row=5, column=0,sticky="w",   pady=(40, 0))
        
        login_button = tk.Button(self, text="Kembali ke Login", command=self.backToLogin)
        login_button.grid(row=5, column=1,sticky="w",   pady=(40, 0))

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
                        print("Data saved successfully to", log_file_path)
                        self.feedback_label_success.config(text="User baru tersimpan", fg="green")
            else:    
                print('Tidak dapat menyimpan User!')
                self.feedback_label.config(text="Tidak dapat menyimpan User!", fg="red")

            self.after(3000, self.clear_feedback)
            

class Frame1(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.output_inference = None  # Initialize output_inference
        self.row_values = None  # Initialize row_values
        self.selected_combobox_value = None  # Initialize the variable
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.grid(row=1, column=1, rowspan=100,sticky="ns")
        
        columns = ('notiket', 'nopol', 'driver', 'b_unit','divisi', 'field', 'bunches', 'ownership', 'pushtime', 'action')
        
        self.tree = ttk.Treeview(self, columns=columns, yscrollcommand=self.scrollbar.set, selectmode="none",  show="headings")
        
        self.style = ttk.Style(self)
        self.row_height = 80  # Set the desired row height
        self.detail_window = None
        
        self.style.configure("Treeview", rowheight=self.row_height)
        
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
  

        self.title_label = tk.Label(self, text=f"Tabel List Truk FFB Grading Sampling {get_list_mill(log_mill,flag=False)[0]}", font=("Helvetica", 16, "bold"))
        self.title_label.grid(row=0, column=0, padx=700, pady=10, sticky="w")
        self.logo_image = tk.PhotoImage(file=Path(os.getcwd() + '/default-img/Logo-CBI(4).png'))  # Replace "logo.png" with your image file path
        self.logo_image = self.logo_image.subsample(2, 2)  # Adjust the subsample values to resize the image
        logo_label = tk.Label(self, image=self.logo_image)
        logo_label.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        self.logo_image2 = tk.PhotoImage(file=Path(os.getcwd() + '/default-img/LOGO-SRS(1).png'))
        self.logo_image2 = self.logo_image2.subsample(2, 2)
        logo_label2 = tk.Label(self, image=self.logo_image2)
        logo_label2.grid(row=0, column=0, padx=160, pady=15, sticky="nw")  # Change column to 0 and sticky to "ne"

        self.mill_var = tk.StringVar()
        cctv_choices = get_list_mill(log_mill, flag=True)
        cctv_choices.append('Video - Test')
        self.cctv_combobox = ttk.Combobox(self, textvariable=self.mill_var, values=cctv_choices)
        self.cctv_combobox.grid(row=0, column=0, padx=200, pady=30, sticky="ne")
        self.mill_var.set(cctv_choices[0])
        self.source = self.mill_var.get()

        self.cctv_combobox.bind("<FocusOut>", self.on_combobox_focus_out)
        
        self.style = ttk.Style()
        self.style.configure("refresh.TButton", padding=6, borderwidth=3, relief="groove", font=("Helvetica", 10))
 
        self.button = ttk.Button(self, text="Refresh", style="refresh.TButton", command=self.refresh_data)
        self.button.grid(row=0, column=0, padx=30, pady=30, sticky="ne")
         # Initialize source

        print(self.source)
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

    def on_combobox_focus_out(self, event):
        selected_value = self.mill_var.get()
        self.selected_combobox_value = selected_value  # Store the selected value in a class variable
        print("Selected value:", selected_value)

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
            
            self.tree.tag_configure(row_id, background="#cccdce")  # Change row color
            self.clicked_buttons.add(row_id)

            self.running_script = True  # Set flag to indicate script is running
            self.button.config(state=tk.DISABLED)  # Disable the button
            
            thread = threading.Thread(target=self.run_script, args=(row_item, row_id, row_values))
            thread.start()

    def run_script(self, row_item, row_id, row_values):
        

        output_inference = None
        try:
            
            result = subprocess.run(['python', '8-track-batas_2.py', '--pull_data', str(row_values)], 
                            capture_output=True, 
                            text=True, 
                            check=True)

            output_inference = result.stdout
     
        except subprocess.CalledProcessError as e:
            print("Error running other_script.py:", str(e))

        # Store output_inference and row_values in instance variables
        # self.output_inference = output_inference
        # self.row_values = row_values


        # Check if the subprocess has finished and switch to Frame3
        if output_inference:
            self.master.switch_frame(Frame3, output_inference, row_values)
        else:
            self.running_script = False
            self.button.config(state=tk.NORMAL)  # Enable the button
    

    def switch_frame(self):
        self.master.switch_frame(Frame2)


def remove_non_numeric(input_str):
    return re.sub(r'[^0-9.]', '', input_str)


class Frame3(tk.Frame):
    def __init__(self, master, output_inference, row_values):
        super().__init__(master)
      
       
        submit_button = tk.Button(self, text="Submit", command=lambda: self.save_and_switch(count_per_class, row_values))
        submit_button.grid(row=19, column=0, columnspan=4, sticky="w", pady=50)


    def save_and_switch(self, count_per_class, row_values):

    
        
        # Switch back to Frame1
        self.master.switch_frame(Frame1)

class Frame2(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

       

    def switch_frame(self):
        self.master.switch_frame(Frame1)

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Aplikasi Pos Grading")
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.login_frame = LoginFrame(self)

        self.current_frame = None  # Initialize current_frame to None
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

        self.current_frame.pack()

        if isinstance(self.current_frame, LoginFrame):
            window_width = 500
            window_height = 500
        elif isinstance(self.current_frame, RegisterFrame):
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
    app.mainloop()