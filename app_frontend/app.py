import tkinter as tk
from tkinter import ttk
import threading
import queue
from dotenv import load_dotenv
import os
from typing import Final
import psycopg
import datetime

# Assuming your class is in a file named detector_module.py
# from detector_module import LicensePlateDetection 

class ParkingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        load_dotenv()
        self.update()
        self.CONNECTION_STRING: Final = f"dbname={os.getenv("DB_NAME")} user={os.getenv("DB_USER")} password={os.getenv("DB_PW")} host={os.getenv("DB_HOST")}"
        self.title("Parking Management System")
        self.geometry("700x600")
        
        # Shared data
        self.shared_data = {
            "license_plate": tk.StringVar(value="..."),
            "status": tk.StringVar(value="Idle"),
            "centre_id": None,
            "wing":tk.StringVar(),
            "floor":None,
            "spot_number":None,
            "size":tk.StringVar(),
            "owner_id":tk.StringVar()}
        
        self.container = tk.Frame(self)
        self.update()
        self.container.pack(fill="both", expand=True)
        
        self.frames = {}
        for F in (Select_Wing_Page,Empty_Spots_Page, Page1, Page2, Page3):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_page("Select_Wing_Page")

    def show_page(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

class Select_Wing_Page(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.update_idletasks()
        tk.Label(self, text="Parking Management System", font=('Arial', 26)).grid(row=0, column=0, columnspan=2, pady=20)
        tk.Label(self, text="Select Your Wing", font=('Arial', 20)).grid(row=1, column=0, columnspan=2, pady=10)
        
        wings_list = self.get_wings_list()
        
        if not wings_list:
            tk.Label(self, text="NO WINGS FOUND", font=('Arial', 26), fg="red").grid(row=1, column=0, columnspan=2, pady=10)
            return 

        tk.Label(self, text="Select Wing:", font=('Arial', 15)).grid(row=2, column=0, pady=10)
        
        # 1. Create the Combobox
        self.wing_dropdown = ttk.Combobox(self,textvariable=self.controller.shared_data["wing"], 
                                            values=wings_list, width=50, font=('Arial', 10),state="readonly")
        self.wing_dropdown.grid(row=2, column=1, pady=10)
        
        # 2. BIND the event. This tells the program: "Run this function whenever a new item is picked"
        self.wing_dropdown.bind("<<ComboboxSelected>>", self.on_wing_selected)

        tk.Button(self, text="Continue", font=('Arial', 15), command=lambda: controller.show_page("Empty_Spots_Page")).grid(row=3, column=0, columnspan=2, pady=5)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def get_wings_list(self):
        with psycopg.connect(self.controller.CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT wing FROM has_wing_floor")
                return [row[0] for row in cur.fetchall()] # returns string result

    def on_wing_selected(self, event):
        # This function runs only after the user selects a wing
        selected_wing = self.controller.shared_data["wing"].get()
        print(f"DEBUG: User selected {selected_wing}")
        self.get_centre(selected_wing)
                 
    def get_centre(self, selected_wing):
        with psycopg.connect(self.controller.CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                # Use the passed argument 'selected_wing' directly
                cur.execute("SELECT centre_id FROM has_wing_floor WHERE wing = %s", (selected_wing,))
                result = cur.fetchone()
                if result:
                    self.controller.shared_data["centre_id"] = result[0]
                    print(f"DEBUG: Centre ID updated to {result[0]}")

class Empty_Spots_Page(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.wing_label = tk.Label(self, text="", font=('Arial', 26))
        self.wing_label.grid(row=0, column=0, pady=10)

        self.availability_label = tk.Label(self, text="", font=('Arial', 20))
        self.availability_label.grid(row=1, column=0, pady=10)

        self.two_wheeler_label = tk.Label(self, text="", font=('Arial', 15))
        self.two_wheeler_label.grid(row=2, column=0)

        self.four_wheeler_label = tk.Label(self, text="", font=('Arial', 15))
        self.four_wheeler_label.grid(row=3, column=0)

        tk.Button(self, text="Continue", font=('Arial', 15),
                  command=lambda: controller.show_page("Page1")).grid(row=4, column=0, pady=5)
        
        tk.Button(self, text="Select Wing", font=('Arial', 15),
                  command=lambda: controller.show_page("Select_Wing_Page")).grid(row=5, column=0, pady=5)

        self.grid_columnconfigure(0, weight=1)

    def on_show(self):
        self.refresh_data()

    def refresh_data(self):
        self.wing_label.config(text=f"{self.controller.shared_data['wing'].get()}")
        two, four = self.get_free_spots_count()
        if two == -1 and four == -1:
            self.availability_label.config(text="NO FREE SPOTS AVAILABLE", fg="red")
            self.two_wheeler_label.config(text="")
            self.four_wheeler_label.config(text="")
        else:
            self.availability_label.config(text="Check Availability", fg="black")
            self.two_wheeler_label.config(text=f"Free Spots Two-Wheeler = {two}")
            self.four_wheeler_label.config(text=f"Free Spots Four-Wheeler = {four}")

    def get_free_spots_count(self):
        two_wheeler_free_spots = four_wheeler_free_spots = 0
        with psycopg.connect(f"{self.controller.CONNECTION_STRING}") as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT COUNT(*) FROM has_parking_spot WHERE wing = %s 
                                AND size = 'Two Wheeler' AND  availability = True""",(self.controller.shared_data['wing'].get(),))
                two_wheeler_free_spots = cur.fetchone()[0]

                cur.execute("""SELECT COUNT(*) FROM has_parking_spot WHERE wing = %s 
                                AND size = 'Four Wheeler' AND  availability = True""",(self.controller.shared_data['wing'].get(),))
                four_wheeler_free_spots = cur.fetchone()[0]

                if two_wheeler_free_spots >0 and four_wheeler_free_spots >0:
                    return two_wheeler_free_spots, four_wheeler_free_spots
                else:
                    return -1,-1


class Page1(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 1. Header with columnspan so it stays centered at the top
        tk.Label(self, text="Automatic License Plate Detection", font=('Arial', 26)).grid(row=0, column=0, columnspan=2,pady=10)
        
        # 2. Buttons
        tk.Button(self, text="Start Detection", font=('Arial', 15), command=self.start_detection).grid(row=1, column=0, pady=10)
        tk.Button(self, text="Stop Detection", font=('Arial', 15), command=self.stop_detection).grid(row=1, column=1, pady=10)

        tk.Label(self, text="License Plate:", font=('Arial', 15)).grid(row=2, column=0, pady=10)
        tk.Entry(self, textvariable=controller.shared_data["license_plate"], font=('Arial', 10)).grid(row=2, column=1, pady=10)

        tk.Label(self, text="Vehicle Type:", font=('Arial', 15)).grid(row=3, column=0, pady=10)
        self.size_dropdown = ttk.Combobox(
            self, textvariable=self.controller.shared_data["size"],
            values=["Two Wheeler", "Four Wheeler"], font=('Arial', 10), state="readonly"
        )
        self.size_dropdown.grid(row=3, column=1, pady=10)
        self.size_dropdown.bind("<<ComboboxSelected>>", self.on_size_selected)

        self.model =  tk.StringVar(value="")
        self.colour = tk.StringVar(value="")
        self.phone_number = tk.StringVar(value="")
        self.name = tk.StringVar(value="")
        self.clear_fields()
        tk.Label(self, text="Model:", font=('Arial', 15)).grid(row=4, column=0, pady=10)
        tk.Entry(self, textvariable=self.model, font=('Arial', 10)).grid(row=4, column=1, pady=10)

        tk.Label(self, text="Colour:", font=('Arial', 15)).grid(row=5, column=0, pady=10)
        tk.Entry(self, textvariable=self.colour, font=('Arial', 10)).grid(row=5, column=1, pady=10)

        tk.Label(self, text="Owner_Id:", font=('Arial', 15)).grid(row=6, column=0, pady=10)
        tk.Entry(self, textvariable=controller.shared_data["owner_id"], font=('Arial', 10)).grid(row=6, column=1, pady=10)

        tk.Label(self, text="Phone Number:", font=('Arial', 15)).grid(row=7, column=0, pady=10)
        tk.Entry(self, textvariable=self.phone_number, font=('Arial', 10)).grid(row=7, column=1, pady=10)

        tk.Label(self, text="Name:", font=('Arial', 15)).grid(row=8, column=0, pady=10)
        tk.Entry(self, textvariable=self.name, font=('Arial', 10)).grid(row=8, column=1, pady=10)

        tk.Button(self, text="Fetch Details", font=('Arial', 15), 
                  command= self.fetch_details).grid(row=9, column=0,  pady=5)
        
        tk.Button(self, text="Save Details", font=('Arial', 15), 
                  command=lambda: self.update_vehicle_details(self.model, self.colour, self.phone_number, self.name)).grid(row=9, column=1, pady=5)

        tk.Button(self, text="Continue", font=('Arial', 15), command=lambda: controller.show_page("Page2")).grid(row=10, column=0, columnspan=2, pady=5)
        
        # 3. Add these two lines to center the grid columns!
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.detection_thread = None
        self.stop_event = threading.Event()
    
    def on_show(self):
        self.clear_fields()
    
    def clear_fields(self):
        self.model.set("")
        self.colour.set("")
        self.phone_number.set("")
        self.name.set("")
        self.controller.shared_data["license_plate"].set("")
        self.controller.shared_data["owner_id"].set("")
        self.controller.shared_data["size"].set("")
    
    def fetch_details(self):
        with psycopg.connect(self.controller.CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT owner_id,model,colour,type
                                FROM owns_vehicle WHERE license_number = %s""",
                                (self.controller.shared_data["license_plate"].get(),),)
                result = cur.fetchone()
                if result:
                    self.controller.shared_data["owner_id"].set(result[0])
                    self.model.set(result[1])
                    self.colour.set(result[2])
                    self.controller.shared_data["size"].set(result[3])
                    
                cur.execute("""SELECT phone FROM owner_phone
                                WHERE owner_id = %s""",
                                (self.controller.shared_data["owner_id"].get(),),)
                
                phone_result = cur.fetchone()
                if phone_result:
                    self.phone_number.set(phone_result[0])

                cur.execute("SELECT name FROM owner WHERE owner_id = %s",
                            (self.controller.shared_data["owner_id"].get(),),)
                
                name_result = cur.fetchone()
                if phone_result:
                    self.name.set(name_result[0])


    def start_detection(self):
        self.stop_event.clear()
        self.detection_thread = threading.Thread(target=self.run_yolo)
        self.detection_thread.start()

    def run_yolo(self):
        # Initialize your class here
        # detector = LicensePlateDetection()
        # Use a loop that checks self.stop_event.is_set()
        print("Detection loop running...")
        # Update shared_data using: self.controller.shared_data["license_plate"].set("ABC-1234")

    def stop_detection(self):
        self.stop_event.set()
        print("Stopping detection...")

    def on_size_selected(self, event=None):
        self.controller.shared_data["floor"] = None
        self.controller.shared_data["spot_number"] = None

    def update_vehicle_details(self, tk_model, tk_colour, tk_phone_number, tk_name):
        model = tk_model.get()
        colour = tk_colour.get()
        phone_number = tk_phone_number.get()
        name = tk_name.get()
        if self.controller.shared_data["owner_id"].get() == "":
            self.controller.shared_data["owner_id"].set(self.controller.shared_data["license_plate"].get()) 
        with psycopg.connect(self.controller.CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO owner (owner_id, name) 
                                VALUES (%s,%s)
                                ON CONFLICT (owner_id)
                                DO NOTHING""",
                                (self.controller.shared_data["owner_id"].get(),name))
                
                cur.execute("""INSERT INTO owner_phone (owner_id, phone) 
                                VALUES (%s,%s)
                                ON CONFLICT (owner_id,phone)
                                DO NOTHING""",
                                (self.controller.shared_data["owner_id"].get(),phone_number))
                
                cur.execute("""INSERT INTO 
                                owns_vehicle (owner_id, license_number,model,colour,type)
                                VALUES (%s,%s,%s,%s,%s) 
                                ON CONFLICT (license_number)
                                DO NOTHING""",
                                (self.controller.shared_data["owner_id"].get(),
                                 self.controller.shared_data["license_plate"].get(),
                                 model, colour, self.controller.shared_data["size"].get()))
                
                conn.commit()

class Page2(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller  

        tk.Label(self, text="Mark Entry / Exit", font=('Arial', 26)).grid(row=0, column=0, columnspan=2, pady=10)

        
        self.load_spots()

        tk.Label(self, text="Available Spots:", font=('Arial', 15)).grid(row=3, column=0, pady=10)
        self.spot_var = tk.StringVar()
        self.spot_dropdown = ttk.Combobox(
            self, textvariable=self.spot_var, values=[], width=40,
            font=('Arial', 10), state="readonly"
        )
        self.spot_dropdown.grid(row=3, column=1, pady=10)
        self.spot_dropdown.bind("<<ComboboxSelected>>", self.on_spot_selected)

        # Action Buttons
        tk.Button(self, text="Mark Entry", font=('Arial', 15), command=self.mark_entry).grid(row=4, column=0, pady=5)
        tk.Button(self, text="Mark Exit", font=('Arial', 15), command=self.calculate_duration).grid(row=4, column=1, pady=5)
        tk.Button(self, text="Generate Bill", font=('Arial', 15), command=lambda: controller.show_page("Page3")).grid(row=5, column=0, columnspan=2, pady=5)
        tk.Button(self, text="Return", font=('Arial', 15), command=lambda: controller.show_page("Empty_Spots_Page")).grid(row=6, column=0, columnspan=2, pady=10)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # cache of (floor, spot_number, size) tuples for the current spot_dropdown values
        self._spot_lookup = {}

    def on_show(self):
        self.spot_var.set("")
        self.spot_dropdown["values"] = []
        self.controller.shared_data["floor"] = None
        self.controller.shared_data["spot_number"] = None
        if self.controller.shared_data["size"].get():
            self.load_spots()


    def load_spots(self):
        size = self.controller.shared_data["size"].get()
        if not size:
            return
        rows = self.get_available_spots(size)
        display_values = [f"Floor {floor} - Spot {spot} ({sz})" for floor, spot, sz in rows]
        self._spot_lookup = dict(zip(display_values, rows))
        self.spot_dropdown["values"] = display_values
        self.spot_var.set("")

    def on_spot_selected(self, event=None):
        selected = self.spot_var.get()
        floor, spot_number, size = self._spot_lookup[selected]
        self.controller.shared_data["floor"] = floor
        self.controller.shared_data["spot_number"] = spot_number
        print(f"DEBUG: Selected spot {floor}/{spot_number} ({size})")

    def get_available_spots(self, size):
        with psycopg.connect(self.controller.CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT floor, spot_number, size
                       FROM has_parking_spot
                       WHERE centre_id = %s AND wing = %s AND size = %s AND availability = True
                       ORDER BY floor, spot_number""",
                    (
                        self.controller.shared_data["centre_id"],
                        self.controller.shared_data["wing"].get(),
                        size,
                    ),
                )
                return cur.fetchall()
            
    def mark_entry(self):
        with psycopg.connect(self.controller.CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO 
                                parking_log (entry_time, license_number, centre_id, wing, floor, spot_number)
                                VALUES (%s,%s,%s,%s,%s,%s)""",
                                (datetime.datetime.now(),
                                self.controller.shared_data["license_plate"].get(),
                                self.controller.shared_data["centre_id"],
                                self.controller.shared_data["wing"].get(),
                                self.controller.shared_data["floor"],
                                self.controller.shared_data["spot_number"]))

                cur.execute("""UPDATE has_parking_spot
                                SET availability = False
                                WHERE centre_id = %s AND wing = %s AND floor = %s AND spot_number = %s""",
                                (self.controller.shared_data["centre_id"],
                                self.controller.shared_data["wing"].get(),
                                self.controller.shared_data["floor"],
                                self.controller.shared_data["spot_number"]))
            conn.commit()
        print("DB Entry Added")

    def calculate_duration(self):
        exit_time = datetime.datetime.now()
        with psycopg.connect(self.controller.CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT entry_time, centre_id, wing, floor, spot_number
                                FROM parking_log 
                                WHERE license_number = %s
                                AND exit_time IS NULL 
                                ORDER BY entry_time DESC LIMIT 1""",
                            (self.controller.shared_data["license_plate"].get(),))
                result = cur.fetchone()
                if result:
                    entry_time, centre_id, wing, floor, spot_number = result
                    if entry_time.tzinfo is None:
                        entry_time = entry_time.replace(tzinfo=None)
                    duration = exit_time - entry_time
                    self.calculate_bill_amount(duration, entry_time, exit_time, centre_id, wing, floor, spot_number)
                else:
                    print("No active parking session found for this plate")
                    return -1

    def calculate_bill_amount(self, duration, entry_time, exit_time, centre_id, wing, floor, spot_number):
        self.mark_exit(duration, 100, entry_time, exit_time, centre_id, wing, floor, spot_number)

    def mark_exit(self, duration, amount, entry_time, exit_time, centre_id, wing, floor, spot_number):
        with psycopg.connect(self.controller.CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute("""UPDATE parking_log 
                                SET exit_time = %s, duration = %s, amount = %s
                                WHERE entry_time = %s AND exit_time IS NULL""",
                                (exit_time, duration, amount, entry_time))

                cur.execute("""UPDATE has_parking_spot
                                SET availability = True
                                WHERE centre_id = %s AND wing = %s AND floor = %s AND spot_number = %s""",
                                (centre_id, wing, floor, spot_number))
            conn.commit()
        print("DB Exit Updated")
class Page3(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Billing", font=('Arial', 26)).grid(row=0, column=0, columnspan=2, pady=20)

        self.name_var = tk.StringVar()
        self.entry_time_var = tk.StringVar()
        self.exit_time_var = tk.StringVar()
        self.duration_var = tk.StringVar()
        self.amount_var = tk.StringVar()

        tk.Label(self, text="License Number:", font=('Arial', 15)).grid(row=1, column=0, pady=10, sticky="e")
        tk.Label(self, textvariable=controller.shared_data["license_plate"], font=('Arial', 15, 'bold')).grid(row=1, column=1, pady=10, sticky="w")

        tk.Label(self, text="Owner Name:", font=('Arial', 15)).grid(row=2, column=0, pady=10, sticky="e")
        tk.Label(self, textvariable=self.name_var, font=('Arial', 15, 'bold')).grid(row=2, column=1, pady=10, sticky="w")

        tk.Label(self, text="Entry Time:", font=('Arial', 15)).grid(row=3, column=0, pady=10, sticky="e")
        tk.Label(self, textvariable=self.entry_time_var, font=('Arial', 15, 'bold')).grid(row=3, column=1, pady=10, sticky="w")

        tk.Label(self, text="Exit Time:", font=('Arial', 15)).grid(row=4, column=0, pady=10, sticky="e")
        tk.Label(self, textvariable=self.exit_time_var, font=('Arial', 15, 'bold')).grid(row=4, column=1, pady=10, sticky="w")

        tk.Label(self, text="Duration:", font=('Arial', 15)).grid(row=5, column=0, pady=10, sticky="e")
        tk.Label(self, textvariable=self.duration_var, font=('Arial', 15, 'bold')).grid(row=5, column=1, pady=10, sticky="w")

        tk.Label(self, text="Amount:", font=('Arial', 15)).grid(row=6, column=0, pady=10, sticky="e")
        tk.Label(self, textvariable=self.amount_var, font=('Arial', 15, 'bold')).grid(row=6, column=1, pady=10, sticky="w")

        tk.Button(self, text="Print Bill", font=('Arial', 20), command=lambda: print("Printing...")).grid(row=7, column=0, columnspan=2, pady=10)
        tk.Button(self, text="Return Home", font=('Arial', 20), command=lambda: controller.show_page("Empty_Spots_Page")).grid(row=8, column=0, columnspan=2, pady=10)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def on_show(self):
        self.fetch_bill()

    def fetch_bill(self):
        plate = self.controller.shared_data["license_plate"].get()
        with psycopg.connect(self.controller.CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT entry_time, exit_time, duration, amount
                               FROM parking_log
                               WHERE license_number = %s AND exit_time IS NOT NULL
                               ORDER BY exit_time DESC LIMIT 1""",
                            (plate,))
                result = cur.fetchone()
                if not result:
                    self.entry_time_var.set("--")
                    self.exit_time_var.set("--")
                    self.duration_var.set("--")
                    self.amount_var.set("No completed session found")
                    self.name_var.set("--")
                    return

                entry_time, exit_time, duration, amount = result
                self.entry_time_var.set(entry_time.strftime("%Y-%m-%d %H:%M:%S"))
                self.exit_time_var.set(exit_time.strftime("%Y-%m-%d %H:%M:%S"))
                self.duration_var.set(str(duration))
                self.amount_var.set(f"₹{amount}")

                cur.execute("""SELECT o.name FROM owner o
                               JOIN owns_vehicle v ON v.owner_id = o.owner_id
                               WHERE v.license_number = %s""",
                            (plate,))
                name_result = cur.fetchone()
                self.name_var.set(name_result[0] if name_result else "--")

if __name__ == "__main__":
    app = ParkingApp()
    app.mainloop()