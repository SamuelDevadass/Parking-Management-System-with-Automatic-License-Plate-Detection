import tkinter as tk
from tkinter import ttk
import threading
import queue
from dotenv import load_dotenv
import os
from typing import Final
import psycopg

# Assuming your class is in a file named detector_module.py
# from detector_module import LicensePlateDetection 

class ParkingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        load_dotenv()
        self.CONNECTION_STRING: Final = f"dbname={os.getenv("DB_NAME")} user={os.getenv("DB_USER")} password={os.getenv("DB_PW")} host={os.getenv("DB_HOST")}"
        self.title("Parking Management System")
        self.geometry("550x500")
        
        # Shared data
        self.shared_data = {
            "license_plate": tk.StringVar(value="Waiting for detection..."),
            "status": tk.StringVar(value="Idle"),
            "centre_id": None,
            "wing":tk.StringVar(),
            "floor":None,
            "spot_number":None,
            "type":None
        
        }
        
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        self.frames = {}
        for F in (Select_Wing_Page,Empty_Spots_Page, Page1, Page2, Page3):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_page("Select_Wing_Page")

    def show_page(self, page_name):
        self.frames[page_name].tkraise()

class Select_Wing_Page(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
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
        
        tk.Label(self, text=self.controller.shared_data["wing"].get(), font=('Arial', 26)).grid(row=0, column=0, pady=10)
        tk.Label(self, text="Check Availability", font=('Arial', 20)).grid(row=1, column=0, pady=10)

        # Empty Spots Count
        two_wheelers, four_wheelers = self.get_free_spots_count()

        if two_wheelers == -1 or four_wheelers == -1:
            tk.Label(self, text="NO FREE SPOTS AVAILABLE", font=('Arial', 26)).grid(row=1, column=0, pady=10)
        else:

            tk.Label(self, text=f"Free Spots Two-Wheeler = {two_wheelers}", font=('Arial',15)).grid(row=2, column = 0)
            tk.Label(self, text=f"Free Spots Four-Wheeler = {four_wheelers}", font=('Arial',15)).grid(row=3, column = 0)

            tk.Button(self, text="Continue", font=('Arial', 15), command=lambda: controller.show_page("Page1")).grid(row=4, column=0, pady=5)
        
        # 3. Add these two lines to center the grid columns!
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

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
        tk.Button(self, text="Start Detection", font=('Arial', 15), command=self.start_detection).grid(row=2, column=0, pady=10)
        tk.Button(self, text="Stop Detection", font=('Arial', 15), command=self.stop_detection).grid(row=2, column=1, pady=10)
        tk.Button(self, text="Continue", font=('Arial', 15), command=lambda: controller.show_page("Page2")).grid(row=3, column=0, columnspan=2, pady=5)
        
        # 3. Add these two lines to center the grid columns!
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.detection_thread = None
        self.stop_event = threading.Event()
    
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


class Page2(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Mark Entry / Exit", font=('Arial', 26)).grid(row=0,column=0,columnspan=2,pady=10)
        
        # License Plate Field (Autofilled)
        tk.Label(self, text="License Plate:", font=('Arial',15),).grid(row=1,column=0,pady=10)
        tk.Entry(self, textvariable=controller.shared_data["license_plate"], font = ('Arial',10)).grid(row=1,column=1,pady=10)
        
        # 5 dummy fields
        tk.Entry(self, text = "Enter", font=('Arial',15), width=30).grid(row=2,column=0,columnspan=2,pady=2)
            
        # Action Buttons
        tk.Button(self, text="Mark Entry", font=('Arial',15), command=lambda: print("DB Entry Added")).grid(row=7,column=0,pady=5)
        tk.Button(self, text="Mark Exit", font=('Arial',15), command=lambda: print("DB Exit Updated")).grid(row=7,column=1,pady=5)
        tk.Button(self, text="Generate Bill", font=('Arial',15), command=lambda: controller.show_page("Page3")).grid(row=8,column=0,columnspan=2,pady=5)
        
        # New Return Button
        tk.Button(self, text="Return", font=('Arial',15), command=lambda: controller.show_page("Empty_Spots_Page")).grid(row=9,column=0,columnspan=2,pady=10)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

class Page3(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Step 3: Billing", font=('Arial',20)).pack(pady=20)
        # Add SQL result display here
        tk.Button(self, text="Print Bill", font=('Arial',20), command=lambda: print("Printing...")).pack()
        tk.Button(self, text="Return Home", font=('Arial',20), command=lambda: controller.show_page("Empty_Spots_Page")).pack(pady=10)

if __name__ == "__main__":
    app = ParkingApp()
    app.mainloop()