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

columns = ('no', 'notiket', 'nopol', 'driver', 'b_unit','divisi', 'field', 'bunches', 'ownership', 'pushtime', 'action')

current_date = datetime.datetime.now()

# Format the date as yyyy-mm-dd
formatted_date = current_date.strftime('%Y-%m-%d')

log_data = Path(os.getcwd() + '/data')
data_bunit = Path(str(log_data) + '/bunit_mapping.txt')
data_div = Path(str(log_data) + '/div_mapping.txt')
data_block = Path(str(log_data) + '/blok_mapping.txt')

log_inference = Path(os.getcwd() + '/hasil')

log_inference.mkdir(parents=True, exist_ok=True)  # make dir
log_dir = Path(os.getcwd() + '/hasil/' + formatted_date  + '/'+ formatted_date+'_log.TXT')

if not log_dir.exists():
    log_folder = os.path.dirname(log_dir)
    os.makedirs(log_folder, exist_ok=True)
    log_dir.touch()

def remove_non_numeric(input_str):
    return re.sub(r'[^0-9.]', '', input_str)
class Frame1(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
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
        self.tree.column("no", width=25)         
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
        top_frame.grid_columnconfigure(2, weight=50)
        top_frame.grid_columnconfigure(3, weight=28)


        self.title_label = tk.Label(top_frame, text="TABEL LIST TRUK FFB GRADING PER TRUK SCM", font=("Helvetica", 16, "bold"))
        self.title_label.grid(row=0, column=2)
        self.logo_image = tk.PhotoImage(file=Path(os.getcwd() + '/default-img/Logo-CBI(4).png'))  # Replace "logo.png" with your image file path
        self.logo_image = self.logo_image.subsample(2, 2)  # Adjust the subsample values to resize the image
        logo_label = tk.Label(top_frame, image=self.logo_image)
        logo_label.grid(row=0, column=0)

        self.logo_image2 = tk.PhotoImage(file=Path(os.getcwd() + '/default-img/LOGO-SRS(1).png'))
        self.logo_image2 = self.logo_image2.subsample(2, 2)
        logo_label2 = tk.Label(top_frame, image=self.logo_image2)
        logo_label2.grid(row=0, column=1)  # Change column to 0 and sticky to "ne"

         # Create a styled button
        self.button = ttk.Button(top_frame, text="REFRESH", style="Accent.TButton", command=self.refresh_data)
        self.button.grid(row=0, column=3)

        self.refresh_data()

        self.tree.grid(row=1, column=0, columnspan=4, sticky="nsew")  # Use columnspan to span all columns

        self.footer_frame = tk.Frame(self)
        self.footer_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=40)  # Use columnspan to span all columns

        footer_label = tk.Label(self.footer_frame, text="Copyright @ Digital Architect SRS 2023", font=("Helvetica", 14, "bold"))
        footer_label.pack()

        self.last_update_model = tk.Frame(self)
        self.last_update_model.grid(row=2, column=0, columnspan=3, sticky="nw", pady=10)  # Use columnspan to span all columns

        last_model = tk.Label(self.last_update_model, text="Tanggal Update Model AI : 08 Agustus 2023",font=("Helvetica", 12, "italic"))
        last_model.pack()
                
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.running_script = False  # Flag to track if script is running


    def populate_treeview(self, arrData):
        #clearprint(arrData)
        custom_font = tkFont.Font(family="Helvetica", size=11)
        
        for i, data in enumerate(arrData, start=1):
            item = self.tree.insert("", "end", values=data, tags=i)
            self.tree.set(item, "#11", "READY")

            self.tree.tag_bind(i, "<ButtonRelease-1>", lambda event, row_item=item: self.update_row(row_item, event))

            if "Selesai" in data:
                self.tree.tag_configure(i, background="#94c281", font=custom_font)  # Set background color to green
            else:
                self.tree.tag_configure(i, background="#FFFFFF", font=custom_font)  # Change row color      

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
                print(f"Error executing update query: {str(e)}")
                output_datetime_str = str(data['Ppro_push_time'])

            arr_data.append((
                str(index+1),
                data['WBTicketNo'],
                data['VehiclePoliceNO'],
                data['DriverName'],
                ppro_bunit_name,
                ppro_div_name,
                ppro_block_name,
                data['Bunches'],
                data['Ownership'],
                output_datetime_str
            ))

        sorted_data = sorted(arr_data, key=lambda x: x[9], reverse=True)
        
        return sorted_data

    def refresh_data(self):
        self.tree.delete(*self.tree.get_children())
        master_bunit = self.pull_master('MasterBunit_staging','Ppro_BUnitCode','Ppro_BUnitName',data_bunit)
        master_div = self.pull_master('MasterDivisi_Staging','Ppro_DivisionCode','Ppro_DivisionName',data_div)
        master_block = self.pull_master('MasterBlock_Staging','Ppro_FieldCode','Ppro_FieldName',data_block)
        record = self.pull_data_ppro() 
        arr_data = self.process_data(record, master_bunit, master_div, master_block)
        self.after(10, lambda: self.populate_treeview(arr_data))
    
    def update_row(self, row_item, event):
        row_id = int(self.tree.item(row_item, "tags")[0])  # Get row ID from tags

        column = self.tree.identify_column(event.x)  # Identify the column clicked

        # Extract the column name from the column identifier
        column = column.split("#")[-1]
        #print(self.clicked_buttons)
        for cb in self.clicked_buttons:
            
            self.tree.tag_configure(cb, background="#ffffff")  # Change row color
            self.clicked_buttons.remove(cb)
        
        #print("column:" + str(column) + "|columns:"+ str(len(columns)))
        if row_id not in self.clicked_buttons and not self.running_script:

            self.tree.tag_configure(row_id, background="#cccdce")  # Change row color
            self.clicked_buttons.append(row_id)

            if int(column) == len(columns):
            
                row_values = self.tree.item(row_item, "values")  # Get values of the row
                                
                self.running_script = True  # Set flag to indicate script is running
                self.button.config(state=tk.DISABLED)  # Disable the button

                thread = threading.Thread(target=self.run_script, args=(row_item, row_id, row_values))
                thread.start()


    def run_script(self, row_item, row_id, row_values):

        output_inference = None
        try:
            
            result = subprocess.run(['python', '9-track-master.py', '--pull_data', str(row_values)], 
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
            self.button.config(state=tk.NORMAL)  # Enable the button

class Frame3(tk.Frame):
    def __init__(self, master, output_inference, row_values):
        super().__init__(master)
      
        totalJjg = 0
        count_per_class = None

        if output_inference is not None:
            first_list_end = output_inference.find("]")
            if first_list_end != -1:
                count_per_class_str = output_inference[:first_list_end + 1]
                try:
                    count_per_class = eval(count_per_class_str)
                except Exception as e:
                    print(f"Error evaluating count_per_class: {e}")
            
            class_names = output_inference[first_list_end + 1:]

            if isinstance(count_per_class, list) and count_per_class:
                totalJjg = sum(count_per_class)
            else:
                # Handle the case when count_per_class is not a valid list
                totalJjg = 0  # or some other default value


        WBTicketNo = row_values[0] if row_values else ''
        VehiclePoliceNO = row_values[1]if row_values else ''
        DriverName = row_values[2]if row_values else ''
        BUnit = row_values[3]if row_values else ''
        Divisi = row_values[4]if row_values else ''
        Field = row_values[5]if row_values else ''
        Bunches = row_values[6]if row_values else ''
        Ownership = row_values[7]if row_values else ''
        push_time = row_values[8]if row_values else ''
        # pull_time = row_values[9]if row_values else ''

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

        param_label9 = tk.Label(self, text=push_time)
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

        if count_per_class and len(count_per_class) > 0:
            param_label10 = tk.Label(self, text=count_per_class[0])
        else:
            param_label10 = tk.Label(self, text="N/A")  # Provide a default value when count_per_class is empty or None
        param_label10.grid(row=10, column=3,  sticky="w", pady=5)

        label11 = tk.Label(self, text="Ripe : ")
        label11.grid(row=11, column=0, sticky="w",  pady=5)

        if count_per_class and len(count_per_class) > 1:
            param_label11 = tk.Label(self, text=count_per_class[1])
        else:
            param_label11 = tk.Label(self, text="N/A")  # Provide a default value when count_per_class is empty or has less than 2 elements
        param_label11.grid(row=11, column=1, sticky="w",  pady=5)

        label12 = tk.Label(self, text="Overripe : ")
        label12.grid(row=11, column=2, sticky="w",  pady=5)

        if count_per_class and len(count_per_class) > 2:
            param_label12 = tk.Label(self, text=count_per_class[2])
        else:
            param_label12 = tk.Label(self, text="N/A")  # Provide a default value when count_per_class is empty or has less than 3 elements
        param_label12.grid(row=11, column=3,  sticky="w", pady=5)

        label13 = tk.Label(self, text="Empty Bunch : ")
        label13.grid(row=12, column=0, sticky="w",  pady=5)

        if count_per_class and len(count_per_class) > 2:
            param_label13 = tk.Label(self, text=count_per_class[3])
        else:
            param_label13 = tk.Label(self, text="N/A")  # Provide a default value when count_per_class is empty or has less than 3 elements
        param_label13.grid(row=12, column=1,  sticky="w", pady=5)

        label14 = tk.Label(self, text="Abnormal : ")
        label14.grid(row=12, column=2, sticky="w",  pady=5)

        if count_per_class and len(count_per_class) > 2:
            param_label12 = tk.Label(self, text=count_per_class[4])
        else:
            param_label12 = tk.Label(self, text="N/A")  # Provide a default value when count_per_class is empty or has less than 3 elements
        param_label12.grid(row=12, column=3,  sticky="w", pady=5)

        label15 = tk.Label(self, text="Tangkai Panjang : ")
        label15.grid(row=13, column=0, sticky="w",  pady=5)

        if count_per_class and len(count_per_class) > 2:
            param_label12 = tk.Label(self, text=count_per_class[5])
        else:
            param_label12 = tk.Label(self, text="N/A")  # Provide a default value when count_per_class is empty or has less than 3 elements
        param_label12.grid(row=13, column=1,  sticky="w", pady=5)

        label16 = tk.Label(self, text="Kastrasi : ")
        label16.grid(row=13, column=2, sticky="w",  pady=5)

        if count_per_class and len(count_per_class) > 2:
            param_label12 = tk.Label(self, text=count_per_class[6])
        else:
            param_label12 = tk.Label(self, text="N/A")  # Provide a default value when count_per_class is empty or has less than 3 elements
        param_label12.grid(row=13, column=3,  sticky="w", pady=5)

        subtitle3 = tk.Label(self, text="Input Tambahan : ",  font=("Helvetica", 13, "italic"))
        subtitle3.grid(row=14, column=0,columnspan=4, sticky="w",  pady=5)

        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=15, column=0, columnspan=4, sticky="ew")

        label17 = tk.Label(self, text="Brondolan : ")
        label17.grid(row=16, column=0, sticky="w",  pady=5)

        self.brondolanEntry = tk.Entry(self)
        self.brondolanEntry.grid(row=16, column=1, sticky="w", pady=5)

        unit_label = tk.Label(self, text="kg")
        unit_label.grid(row=16, column=2, sticky="w", pady=5)

        label18 = tk.Label(self, text="Brondolan Busuk : ")
        label18.grid(row=17, column=0, sticky="w",  pady=5)

        self.brondoalBusukEntry = tk.Entry(self)
        self.brondoalBusukEntry.grid(row=17, column=1, sticky="w", pady=5)

        unit_label = tk.Label(self, text="kg")
        unit_label.grid(row=17, column=2, sticky="w", pady=5)

        label19 = tk.Label(self, text="Dirt/Kotoran : ")
        label19.grid(row=18, column=0, sticky="w",  pady=5)

        self.dirtEntry = tk.Entry(self)
        self.dirtEntry.grid(row=18, column=1,  sticky="w",pady=5)

        unit_label = tk.Label(self, text="kg")
        unit_label.grid(row=18, column=2, sticky="w", pady=5)

        submit_button = tk.Button(self, text="Submit", command=lambda: self.save_and_switch(count_per_class, row_values))
        submit_button.grid(row=19, column=0, columnspan=4, sticky="w", pady=50)


    def save_and_switch(self, count_per_class, row_values):

        brondol = self.brondolanEntry.get()
        brondolBusuk = self.brondoalBusukEntry.get()
        dirt = self.dirtEntry.get()

        brondol = remove_non_numeric(brondol)
        brondolBusuk = remove_non_numeric(brondolBusuk)
        dirt = remove_non_numeric(dirt)

        result = ';'.join(map(str, row_values)) + ';'
        result += ';'.join(map(str, count_per_class)) + ';'
        result += str(brondol or 0) + ';'
        result += str(brondolBusuk or 0) + ';'
        result += str(dirt or 0)

        log_file_path = log_dir  

        try:
            with open(log_file_path, 'a') as log_file:
                log_file.write(result + '\n')  # Append the result to the log file with a newline character
                print("Data saved successfully to", log_file_path)
        except Exception as e:
            print("Error saving data to", log_file_path, ":", str(e))

        messagebox.showinfo("Success", "Data Sukses Tersimpan !")  # Show success message

        # Switch back to Frame1
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
        self.output_inference = None  # Initialize output_inference in MainWindow
        self.row_values = None  # Initialize row_values in MainWindow
        
        self.geometry(f"{window_width}x{window_height}")
        
        self.frame1 = Frame1(self)
        self.frame3 = Frame3(self,  self.output_inference , self.row_values)  

        self.current_frame = self.frame1
        self.current_frame.pack(padx=50, pady=50)

    def switch_frame(self, new_frame_class, output_inference=None, row_values=None):
        self.current_frame.destroy()
        if new_frame_class == Frame3:
            # Pass output_inference and row_values to Frame3
            self.current_frame = Frame3(self, output_inference, row_values)
        else:
            self.current_frame = new_frame_class(self)
        self.current_frame.pack()

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