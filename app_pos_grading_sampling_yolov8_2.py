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


current_date = datetime.datetime.now()

# Format the date as yyyy-mm-dd
formatted_date = current_date.strftime('%Y-%m-%d')

log_inference = Path(os.getcwd() + '/log_inference_sampling')

log_inference.mkdir(parents=True, exist_ok=True)  # make dir
log_dir = Path(os.getcwd() + '/log_inference_sampling/' + formatted_date  + '_log.TXT')

if not log_dir.exists():
    log_dir.touch()

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

    tiket = str(tiket)
    plat = str(plat)
    driver = str(driver)
    unit = str(unit)
    divisi = str(divisi)
    blok = str(blok)
    status = str(status)


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
        
        columns = ('plat_estate', 'cam', 'ramp', 'wkt_mulai','wkt_selesai', 'jjg', 'rp', 'ur', 'ov', 'eb', 'ab', 'tp')
        
        self.tree = ttk.Treeview(self, columns=columns, yscrollcommand=self.scrollbar.set, selectmode="none",  show="headings")
        
        self.style = ttk.Style(self)
        self.row_height = 80  # Set the desired row height
        self.detail_window = None
        
        self.style.configure("Treeview", rowheight=self.row_height)
        # self.tree.heading("#1", text="No")
        self.tree.heading("#1", text="Plat & Estate")
        self.tree.heading("#2", text="Camera")
        self.tree.heading("#3", text="Loading Ramp")
        self.tree.heading("#4", text="Waktu Mulai")
        self.tree.heading("#5", text="Waktu Selesai")
        self.tree.heading("#6", text="Total Janjang")
        self.tree.heading("#7", text="Ripe")
        self.tree.heading("#8", text="Unripe")
        self.tree.heading("#9", text="Overripe")
        self.tree.heading("#10", text="Empty Bunch")
        self.tree.heading("#11", text="Abnormal")
        self.tree.heading("#12", text="Tangkai Panjang")
        

        # Adjust column widths
        # self.tree.column("no", width=50)         
        self.tree.column("plat_estate", width=150) 
        self.tree.column("cam", width=150) 
        self.tree.column("ramp", width=150) 
        self.tree.column("wkt_mulai", width=160) 
        self.tree.column("wkt_selesai", width=160) 
        self.tree.column("jjg", width=150) 
        self.tree.column("rp", width=150) 
        self.tree.column("ur", width=150) 
        self.tree.column("ov", width=150) 
        self.tree.column("eb", width=150) 
        self.tree.column("ab", width=150) 
        self.tree.column("tp", width=150)
        

        # self.clicked_buttons = set()  # Set to keep track of clicked buttons

        self.title_label = tk.Label(self, text="Tabel List Truk FFB Grading Sampling SCM", font=("Helvetica", 16, "bold"))
        self.title_label.grid(row=0, column=0, padx=700, pady=10, sticky="w")
        self.logo_image = tk.PhotoImage(file="/home/sdz/grading/inference/github/yolov8ffb/default-img/Logo-CBI(4).png")  # Replace "logo.png" with your image file path
        self.logo_image = self.logo_image.subsample(2, 2)  # Adjust the subsample values to resize the image
        logo_label = tk.Label(self, image=self.logo_image)
        logo_label.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        self.logo_image2 = tk.PhotoImage(file="/home/sdz/grading/inference/github/yolov8ffb/default-img/LOGO-SRS(1).png")
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

       
        if os.path.exists(log_dir):
            with open(log_dir, 'r') as z:
                content = z.readlines()

                arrData = []
                # key = 1
                # for line in content:
                #     parts = line.strip().split(';')  # Split line by semicolon
                    
                #     plat = parts[1]  
                #     bisnis_unit = parts[3]  
                #     ramp_status = parts[7]  
                #     rp = ''
                #     ur = ''
                #     ovr = ''
                #     eb = ''
                #     ab = ''
                #     ks = ''
                #     tp = ''
                #     total_deteksi = ''
                #     waktu_mulai = ''
                #     waktu_selesai = ''
                #     if len(parts) >8 :
                #         waktu_mulai = parts[15]
                #         waktu_selesai = parts[16]
                #         rp = int(parts[8])
                #         ur = int(parts[9])
                #         ovr = int(parts[10])
                #         eb = int(parts[11])
                #         ab = int(parts[12])
                #         ks = int(parts[13])
                #         tp = int(parts[14])
                #         total_deteksi = rp + ur + ovr + eb + ab + ks
                    

                #     arrData.append(( key, plat + ' / ' + bisnis_unit , '', ramp_status, waktu_mulai, waktu_selesai, total_deteksi, rp, ur, ovr, eb, ab, tp))
                #     key = key +1


                arr_ramp_belum_proses = []
                arr_ramp_sudah_proses = []
                key = 0
                lines = []
                key_a = []
                key_b = []
                for line in content:
                    parts = line.strip().split(';')
                    plat = parts[1]
                    bisnis_unit = parts[3]
                    
                    ramp_status = parts[7]
                    rp, ur, ovr, eb, ab, ks, tp = '', '', '', '', '', '', ''
                    total_deteksi = ''
                    waktu_mulai = ''
                    waktu_selesai = ''
                    if len(parts) >= 9:
                        waktu_mulai = parts[15]
                        waktu_selesai = parts[16]
                        rp = int(parts[8])
                        ur = int(parts[9])
                        ovr = int(parts[10])
                        eb = int(parts[11])
                        ab = int(parts[12])
                        ks = int(parts[13])
                        tp = int(parts[14])
                        total_deteksi = rp + ur + ovr + eb + ab + ks
                    
                    # print(waktu_mulai)
                    data = (plat + ' / ' + bisnis_unit, '', ramp_status, waktu_mulai, waktu_selesai, total_deteksi, rp, ur, ovr, eb, ab, tp)
                    if "Mulai" in ramp_status:  # Check for "Mulai" in the value
                        arr_ramp_belum_proses.append( data)
                        key_a.append(key)
                    else:
                        arr_ramp_sudah_proses.append( data)
                        key_b.append(key)

                    lines.append(key)
                    key += 1  # Increment key for the next iteration

                
                lines = key_a + key_b
                arrData = arr_ramp_belum_proses + arr_ramp_sudah_proses


        self.after(10, lambda: self.populate_treeview(arrData, lines))

    def populate_treeview(self, arrData, lines):

        custom_font = tkFont.Font(family="Helvetica", size=11)
        key = 0
        
        for i, data in enumerate(arrData, start=1):
            line_ke = lines[key]
            item = self.tree.insert("", "end", values=data, tags=i)
            self.tree.tag_bind(i, "<ButtonRelease-1>", lambda event, row_item=item, line=line_ke: self.on_row_click(row_item,line))

            if "Selesai" in data:
                self.tree.tag_configure(i, background="#94c281", font=custom_font)  # Set background color to green
            else:
                self.tree.tag_configure(i, background="#FFFFFF", font=custom_font)  # Change row color

            key += 1

    def on_row_click(self, row_item, line_txt):
        # print('nais')
        row_values = self.tree.item(row_item, "values")  # Get values of the row
        print("Row Values:", row_values)  # Print row values

        # detail_frame = tk.Frame(self)
        # detail_frame.grid(row=3, column=0, columnspan=3, sticky="nsew")  # Adjust row and column values as needed

        # # Create labels to display the row details
        # for col_idx, col_value in enumerate(row_values):
        #     label_text = f"{self.tree.heading(col_idx + 1)['text']}: {col_value}"
        #     label = tk.Label(detail_frame, text=label_text, font=("Helvetica", 12))  # Customize font as needed
        #     label.grid(row=col_idx, column=0, sticky="w")

        # # Button to execute a script or perform other actions
        # execute_button = tk.Button(detail_frame, text="Execute Script", font=("Helvetica", 12), command=lambda: self.run_script(row_item, line_txt))
        # execute_button.grid(row=0, column=0, pady=10, sticky="e")
        
        if "Selesai" not in row_values:  # Check if "Selesai" is not in the row values
            self.update_row(row_item, line_txt)
        else:
            print("Row is already Selesai. Button is disabled.")
        
    def update_row(self, row_item, line_txt):
        row_id = int(self.tree.item(row_item, "tags")[0])  # Get row ID from tags
        
        if row_id not in self.clicked_buttons and not self.running_script:
            
            row_values = self.tree.item(row_item, "values")  # Get values of the row
            plat_est = row_values[0]

            self.tree.item(row_item, values=(plat_est,'', "Sedang Berjalan"))
            self.tree.tag_configure(row_id, background="#cccdce")  # Change row color
            self.clicked_buttons.add(row_id)

            self.running_script = True  # Set flag to indicate script is running
            self.button.config(state=tk.DISABLED)  # Disable the button
            
            if os.path.exists(log_dir):
                    with open(log_dir, 'r') as z:
                        content = z.readlines()   
                        targetLine = content[line_txt]

                        bisnis_unit = targetLine.split(';')[3]
                        divisi = targetLine.split(';')[4]
                        
                        wr = open(log_dir, "w")
                        content[line_txt]  = targetLine.replace("Mulai", "Selesai;Sedang Berjalan")
                        wr.writelines(content)
                        wr.close()

            thread = threading.Thread(target=self.run_script, args=(row_item, row_id, row_values, line_txt, bisnis_unit, divisi))
            thread.start()

    def run_script(self, row_item, row_id, row_values, line_txt, bisnis_unit, divisi):
        
        plat_est = row_values[0]
        
        try:

            shell_command = f'sh /home/sdz/grading/inference/github/yolov8ffb/script_inference_sampling.sh "{bisnis_unit}" "{divisi}"'

            script_output = os.popen(shell_command).read()
            self.running_script = False
            self.button.config(state=tk.NORMAL)

        except Exception as e:
            print("Error:", str(e))
        finally:


            
            # try:
            #     subprocess.run(['python', '/home/grading/yolov8/send_pdf_inference.py'], check=True)
            # except subprocess.CalledProcessError as e:
            #     print("Error running other_script.py:", str(e))
            
            if os.path.exists(log_dir):
                    with open(log_dir, 'r') as z:
                        content = z.readlines()   
                        targetLine = content[line_txt]
                        
                        # print(targetLine)
                        wr = open(log_dir, "w")
                        content[line_txt]  = targetLine.replace("Mulai", "Selesai")
                        wr.writelines(content)
                        wr.close()

            self.tree.tag_configure(row_id, background="#94c281")
            self.running_script = False  # Reset the flag
            self.button.config(state=tk.NORMAL)  # Enable the button back

            if os.path.exists(log_dir):
                    with open(log_dir, 'r') as z:
                        content = z.readlines()   
                        targetLine = content[line_txt]
                        
                        parts = targetLine.strip().split(';')

                        status_ramp = parts[7]
                        waktu_mulai = parts[15]
                        waktu_selesai = parts[16]
                        rp = int(parts[8])
                        ur = int(parts[9])
                        ovr = int(parts[10])
                        eb = int(parts[11])
                        ab = int(parts[12])
                        ks = int(parts[13])
                        tp = int(parts[14])
                        total_deteksi = rp + ur + ovr + eb + ab + ks
                        
            self.tree.item(row_item, values=(plat_est, '',status_ramp, waktu_mulai, waktu_selesai, total_deteksi, rp, ur, ovr, eb, ab, tp))

        


    def switch_frame(self):
        self.master.switch_frame(Frame2)



class Frame2(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.logo_image = tk.PhotoImage(file="/home/sdz/grading/inference/github/yolov8ffb/default-img/Logo-CBI(4).png")  # Replace "logo.png" with your image file path
        self.logo_image = self.logo_image.subsample(2, 2)  # Adjust the subsample values to resize the image
        logo_label = tk.Label(self, image=self.logo_image)
        logo_label.grid(row=0, column=0, padx=40, pady=10, sticky="nw")

        self.logo_image2 = tk.PhotoImage(file="/home/sdz/grading/inference/github/yolov8ffb/default-img/LOGO-SRS(1).png")
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

        # no_tiket_entry = tk.Entry(user_info_frame)
        # no_plat_entry = tk.Entry(user_info_frame)
        # driver_entry = tk.Entry(user_info_frame)
        # unit_entry = tk.Entry(user_info_frame)
        # divisi_entry = tk.Entry(user_info_frame)
        # blok_entry = tk.Entry(user_info_frame)
        # status_entry = ttk.Combobox(user_info_frame, values=["Inti", "Eksternal"],  font=entry_font)

        entry_fields = [no_tiket_entry, no_plat_entry, driver_entry, unit_entry, divisi_entry, blok_entry, status_entry]

        # no_tiket_entry.grid(row=2, column=0)
        # no_plat_entry.grid(row=2, column=1)
        # driver_entry.grid(row=2, column=2)
        # # unit_entry.grid(row=2, column=3)
        # divisi_entry.grid(row=4, column=0)
        # blok_entry.grid(row=4, column=1)
        # status_entry.grid(row=4, column=2)
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