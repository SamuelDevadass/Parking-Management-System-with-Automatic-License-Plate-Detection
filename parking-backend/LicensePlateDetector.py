from typing import Optional,Any
import cv2
from tkinter import *
from PIL import Image, ImageTk, ImageFilter, ImageDraw, ImageEnhance
from datetime import datetime
import os
import numpy as np
from rapidocr_onnxruntime import RapidOCR
import easyocr
from ultralytics import YOLO

class LicensePlateDetection:

    def __init__(self):
        """GLOBAL INITIALIZATIONS"""
        self.rapid_ocr_engine = RapidOCR()
        self.easy_ocr_reader = easyocr.Reader(['en'], gpu=False)
        self.yolo_model = YOLO("yolo26n.pt")
        self.folder_path = None
        self.camera = cv2.VideoCapture(0)



    def cleanup(self, detected_status:bool):
        """CLEANUP"""
        if not os.path.exists(self.folder_path):
            print("FOLDER DOES NOT EXIST . . .")
            exit()
        elif detected_status is False:
            print("NO LICENSE PLATE DETECTED . . .")
            exit()
        else:
            for filename in os.listdir(self.folder_path):
                filepath = os.path.join(self.folder_path, filename)
                if filename != "Captured_Image.jpg":
                    os.remove(filepath)

        self.camera.release()
        cv2.destroyAllWindows()

    def startup_check(self):
        """IMAGE CAPTURE PIPELINE"""
        # Get Camera
        if not self.camera:
            print("CAMERA not found\nExiting ... ")
            exit()
        print("CAMERA available at : ",self.camera)

        # Get Current Time for logging
        now = datetime.now()
        print("Current Time: ", now)

        # New repository for current cycle
        self.folder_path = now.strftime("%Y-%m-%d_%H-%M-%S") # os.mkdir() returns None hence create path as string and then create folder
        os.mkdir(self.folder_path)

    def video_capture_with_yolo(self, stop_event = None):
        """CAPTURE LIVE FEED"""
        print("Live video stream active. Press 'q' inside the window to exit.")
        cropped_car_capture = None
        while True:
            if stop_event is not None and stop_event.is_set():
                print("Stop requested from GUI.")
                break

            ret, frame = self.camera.read()
            if not ret:
                print("UNABLE TO ACCESS CAMERA")
                break
            
            results = self.yolo_model(frame, stream=True)

            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Get integer coordinates for drawing
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Extract confidence and class ID
                    conf = float(box.conf[0])
                    class_id = int(box.cls[0])
                    label = f"{result.names[class_id]} {conf:.2f}"

                    # Draw the bounding box and label directly onto the live frame
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    if conf > 0.65:
                        car_x1, car_y1, car_x2, car_y2 = x1, y1, x2, y2
                        cropped_car_capture = frame[car_y1:car_y2, car_x1:car_x2]

            cv2.imshow("YOLO Live Detection Feed", frame)

            # Check if the user pressed the 'q' key to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        current_path = os.path.join(self.folder_path, "Captured_Image.jpg") 
        cv2.imwrite(current_path, frame)
        name_list = ["Captured_Image.jpg"]
        self.display_image(image_name = "Captured_Image.jpg", title = "LIVE CAPTURED IMAGE")
        if cropped_car_capture is not None:
            current_path = os.path.join(self.folder_path, "Car_Crop_Capture.jpg")
            cv2.imwrite(current_path, cropped_car_capture)
            self.display_image(image_name = "Car_Crop_Capture.jpg", title = "CROPPED CAR CAPTURE")
            name_list.append("Car_Crop_Capture.jpg")
        
        cv2.destroyAllWindows()
        return name_list

    def display_image_tk(self, image_name:str, title:str):
        """Display captured image"""
        root=Tk()
        root.title(f"{title}")
        image = Image.open(os.path.join(self.folder_path, f"{image_name}"))
        tk_image = ImageTk.PhotoImage(image)
        label = Label(root,image=tk_image)
        label.pack()
        # Add timer for 3 seconds
        root.after(3000,root.destroy)
        root.mainloop() # wont close until user closes window, root.after sets a timer 
        # Display Car Cropped Capture

    def display_image(self, image_name: str, title: str):
        """Display captured image using OpenCV instead of a second Tk root."""
        image_path = os.path.join(self.folder_path, image_name)
        img = cv2.imread(image_path)
        if img is None:
            print(f"Could not load image for display: {image_path}")
            return
        cv2.imshow(title, img)
        cv2.waitKey(3000)          # shows for 3 seconds
        cv2.destroyWindow(title)
         
    def perform_ocr(self, image_name:str, image_array: Optional[Any] = None):
        """OCR PIPELINE"""
        if os.path.exists(os.path.join(self.folder_path,f"{image_name}")):
            image = Image.open(os.path.join(self.folder_path, f"{image_name}"))
        else:
                image = Image.fromarray(cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB))
        # PERFORM OCR ON THE CROPPED IMAGE
        detected = False
        text = ""
        try:
            results, _ = self.rapid_ocr_engine(image)
            if not results:
                raise ValueError("No text in cropped zone")
            text = " ".join([line[1] for line in results])
            print(f"RAPIDOCR SUCCESS: {text}")
            detected = True
            
        except Exception:
            print("RapidOCR high-speed pass failed. Trying Deep Learning EasyOCR on cropped zone...")
            results = self.easy_ocr_reader.readtext(image)
            text = " ".join([detection[1] for detection in results])
            if text:
                print(f"EASYOCR FALLBACK SUCCESS: {text}")
                detected = True
            else:
                print("NO LICENSE PLATE TEXT DETECTED IN CROPPED ZONE.")
                detected = False

        return text, detected
    
    def image_processing_pipeline(self, image_name: str):
        # A. Try Pillow
        conf, crop, visual = self.pillow_thresholding_pipeline(image_name)
        
        # B. Fallback if needed
        if conf <= 0.5:
            print("Pillow low confidence, falling back to OpenCV...")
            crop, visual = self.opencv_thresholding_pipeline(image_name)
            
        # C. Standardize Output (Save visual for display, return crop for OCR)
        visual.save(os.path.join(self.folder_path, "Contours.jpg"))
        self.display_image(image_name="Contours.jpg", title="CONTOURS")
        
        return "Contours.jpg", crop

    def pillow_thresholding_pipeline(self, image_name: str):
        # 1. Load and Preprocess
        image = Image.open(os.path.join(self.folder_path, image_name)).convert("RGB")
        gray = image.convert('L').filter(ImageFilter.GaussianBlur(0.1))
        
        # 2. Thresholding
        threshold = 65
        binary_edges = gray.point(lambda p: 255 if p > threshold else 0)
        
        # 3. Find Contours (Using built-in filter for cleaner edges)
        # Instead of painting every white pixel, we find the boundaries
        edge_map = binary_edges.filter(ImageFilter.FIND_EDGES)
        
        drawn_image = image.copy()
        draw = ImageDraw.Draw(drawn_image)
        
        # Get coordinates only for the edge pixels
        binary_np = np.array(edge_map)
        coords = np.argwhere(binary_np > 0)
        
        confidence_score = 1.0 if len(coords) > 100 else 0.0
        
        if confidence_score > 0.5:
            # Draw only the edges as lines/points
            for y, x in coords:
                draw.point((x, y), fill='green')
            
            # Crop logic remains the same
            y1, x1 = coords.min(axis=0)
            y2, x2 = coords.max(axis=0)
            padding = 5
            cropped_ocr_input = np.array(binary_edges)[max(0, y1-padding):y2+padding, 
                                                       max(0, x1-padding):x2+padding]
        else:
            cropped_ocr_input = np.array(binary_edges)

        return confidence_score, cropped_ocr_input, drawn_image

    def opencv_thresholding_pipeline(self, image_name: str):
        # 1. Process
        img = cv2.imread(os.path.join(self.folder_path, image_name))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 65, 255, cv2.THRESH_BINARY)
        
        # 2. Draw on original-style visual
        drawn_image_cv = img.copy()
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(drawn_image_cv, contours, -1, (0, 255, 0), 1)
        drawn_image = Image.fromarray(cv2.cvtColor(drawn_image_cv, cv2.COLOR_BGR2RGB))
        
        # 3. Logic to extract crop
        plate_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(plate_contour)
        padding = 5
        cropped_ocr_input = binary[max(0, y-padding):y+h+padding, 
                                   max(0, x-padding):x+w+padding]
        
        return cropped_ocr_input, drawn_image

class Detector:
    def __init__(self):
        self.License_Plate_Detector = LicensePlateDetection()

    def start(self, stop_event):
        print("STARTING APPLICATION . . .")
        self.License_Plate_Detector.startup_check()
        name_list = self.License_Plate_Detector.video_capture_with_yolo(stop_event)
        if len(name_list) > 1:
            image_name = name_list[1]
            text, detected = self.License_Plate_Detector.perform_ocr(image_name=image_name)
            if detected:
                print("YOLO OCR SUCCESS")
                return text, self.License_Plate_Detector.folder_path
            image_name = name_list[0]
            return text,self.License_Plate_Detector.folder_path
        else:
            image_name = name_list[0]

        final_name, final_result = self.License_Plate_Detector.image_processing_pipeline(image_name = image_name)
        text , detected = self.License_Plate_Detector.perform_ocr(image_name=final_name, image_array=final_result)
        #self.License_Plate_Detector.cleanup(detected_status=detected)
        return text,self.License_Plate_Detector.folder_path

if __name__ == "__main__":
    app = Detector()
    text, app.License_Plate_Detector.folder_path = app.start(stop_event=None)
