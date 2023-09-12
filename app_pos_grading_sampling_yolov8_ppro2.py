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

log_data = Path(os.getcwd() + '/data')
data_bunit = Path(str(log_data) + '/bunit_mapping.txt')
data_div = Path(str(log_data) + '/div_mapping.txt')
data_block = Path(str(log_data) + '/blok_mapping.txt')


log_inference.mkdir(parents=True, exist_ok=True)  # make dir
log_dir = Path(os.getcwd() + '/log_inference_sampling/' + formatted_date  + '_log.TXT')

if not log_dir.exists():
    log_dir.touch()

pdf_dir = Path(os.getcwd() + '/hasil/' + formatted_date)

pdf_dir.mkdir(parents=True, exist_ok=True)  # make dir


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

    def connect_to_database(self):
        return pymssql.connect(
            server='192.168.1.254\DBSTAGING',
            user='usertesting',
            password='Qwerty@123',
            database='skmstagingdb',
            as_dict=True
        )

    def pull_master(self, table, code, name, file_name):
        connection = self.connect_to_database()
        sql_query = f"SELECT {str(code)} , {str(name)}  FROM {str(table)} WHERE AI_pull_time IS NULL"
        cursor = connection.cursor()
        cursor.execute(sql_query)
        records = cursor.fetchall()
        connection.close()

        if len(records) > 0 or not file_name.exists():
            sql_query = f"SELECT {str(code)} , {str(name)}  FROM {str(table)}"
            connection = self.connect_to_database()  
            cursor = connection.cursor()
            cursor.execute(sql_query)
            records = cursor.fetchall()
            connection.close()
            mapping = {r[str(code)]: r[str(name)] for r in records}
            
            file_name.touch()
            with open(file_name, 'w') as file:
                for code, name in mapping.items():
                    file.write(f"{code}:{name}\n")
            connection = self.connect_to_database()
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

    def pull_data_ppro(self):
        connection = self.connect_to_database()
        #sql_query = "SELECT * FROM MOPweighbridgeTicket_Staging WHERE AI_pull_time IS NULL"
        sql_query = "SELECT * FROM MOPweighbridgeTicket_Staging" #TRIGGER
        cursor = connection.cursor()
        cursor.execute(sql_query)
        records = cursor.fetchall()
        connection.close()
        
        return records

    def process_data(self, record, master_bunit, master_div, master_block):
        arr_data = []
        for data in record:

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

            arr_data.append((
                data['WBTicketNo'],
                data['VehiclePoliceNO'],
                data['DriverName'],
                ppro_bunit_name,
                ppro_div_name,
                ppro_block_name,
                data['Bunches'],
                data['Ownership'],
                data['Ppro_push_time']
            ))
        
        return arr_data

    def refresh_data(self):
        self.tree.delete(*self.tree.get_children())
        master_bunit = self.pull_master('MasterBunit_staging','Ppro_BUnitCode','Ppro_BUnitName',data_bunit)
        master_div = self.pull_master('MasterDivisi_Staging','Ppro_DivisionCode','Ppro_DivisionName',data_div)
        master_block = self.pull_master('MasterBlock_Staging','Ppro_FieldCode','Ppro_FieldName',data_block)
        record = self.pull_data_ppro() 
        arr_data = self.process_data(record, master_bunit, master_div, master_block)
        self.after(10, lambda: self.populate_treeview(arr_data))

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

        try:
            
            subprocess.run(['python', '9-track-master.py', '--pull_data', str(row_values)], check=True)

        except subprocess.CalledProcessError as e:
            print("Error running other_script.py:", str(e))


    def switch_frame(self):
        self.master.switch_frame(Frame2)



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