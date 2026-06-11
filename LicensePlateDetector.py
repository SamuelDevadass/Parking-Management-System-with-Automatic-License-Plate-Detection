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

    def video_capture_with_yolo(self):
        """CAPTURE LIVE FEED"""
        print("Live video stream active. Press 'q' inside the window to exit.")
        cropped_car_capture = None
        while True:
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

                    if class_id == 2 and conf > 0.65:
                        car_x1, car_y1, car_x2, car_y2 = map(int,box)
                        cropped_car_capture = frame[car_y1:car_y2, car_x1:car_x2]

            cv2.imshow("YOLO Live Detection Feed", frame)

            # Check if the user pressed the 'q' key to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                current_path = os.path.join(self.folder_path, "Captured_Image.jpg") 
                cv2.imwrite(current_path, frame)
                self.display_image(image_name = "Captured_Image.jpg", title = "LIVE CAPTURED IMAGE")
                if cropped_car_capture is not None:
                    current_path = os.path.join(self.folder_path, "Car_Crop_Capture.jpg")
                    cv2.imwrite(current_path, cropped_car_capture)
                    self.display_image(image_name = "Car_Crop_Capture.jpg", title = "CROPPED CAR CAPTURE")

                break

    def display_image(self, image_name:str, title:str):
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
         
    def perform_ocr(self, image_name:str):
        """OCR PIPELINE"""
        image = Image.open(os.path.join(self.folder_path, f"{image_name}"))
        # PERFORM OCR ON THE CROPPED IMAGE
        detected = False
        text = ""
        try:
            results, _ = self.rapid_engine(image)
            if not results:
                raise ValueError("No text in cropped zone")
            text = " ".join([line[1] for line in results])
            print(f"RAPIDOCR SUCCESS: {text}")
            detected = True
            
        except Exception:
            print("RapidOCR high-speed pass failed. Trying Deep Learning EasyOCR on cropped zone...")
            results = self.easy_reader.readtext(image)
            text = " ".join([detection[1] for detection in results])
            if text:
                print(f"EASYOCR FALLBACK SUCCESS: {text}")
                detected = True
            else:
                print("NO LICENSE PLATE TEXT DETECTED IN CROPPED ZONE.")
                detected = False
        
    

"""III. IMAGE PREPROCESSING PIPELINE"""
cropped_ocr_input = None
binary_output = None  # Standardized variable name for the final binary matrix
w_pil, h_pil = image.size

"""III.A. PILLOW FIRST RUN"""
enhancer = ImageEnhance.Contrast(image)
enhanced_image = enhancer.enhance(1.3)
sharpness_enhancer = ImageEnhance.Sharpness(enhanced_image)
sharpened_image = sharpness_enhancer.enhance(1.8)
sharpened_image = sharpened_image.filter(ImageFilter.GaussianBlur(radius=0.1))
gray = sharpened_image.convert('L')
gray = gray.filter(ImageFilter.GaussianBlur(radius=0.1))

threshold = 65
binary_edges_pil = gray.point(lambda p: p > threshold and 255)
contours = []

for x in range(w_pil):
    for y in range(h_pil):
        if binary_edges_pil.getpixel((x, y)) == 255:
            contours.append((x, y))

contour_image = Image.new("RGB", binary_edges_pil.size, (255, 255, 255))
for contour_point in contours:
    contour_image.putpixel(contour_point, (0, 0, 0))

drawn_image = contour_image.copy()

confidence_score = 1.0 if len(contours) > 100 else 0.0

if confidence_score > 0.5:
    print(f"Confidence Score: {confidence_score} - Pillow Thresholding Succeeded")
    draw = ImageDraw.Draw(drawn_image)
    for contour in contours:
        draw.point(contour, fill='green')
        
    x_coords = [p[0] for p in contours]
    y_coords = [p[1] for p in contours]
    padding = 5
    y1 = max(0, min(y_coords) - padding)
    y2 = min(h_pil, max(y_coords) + padding)
    x1 = max(0, min(x_coords) - padding)
    x2 = min(w_pil, max(x_coords) + padding)
    
    binary_output = np.array(binary_edges_pil)
    cropped_ocr_input = binary_output[y1:y2, x1:x2]

else:
    """III.B. OPENCV FALLBACK"""
    print(f"Confidence Score: {confidence_score} - No solid pixel data. Falling back to OpenCV Execution...")
    open_cv_image = np.array(image)
    open_cv_image = open_cv_image[:, :, ::-1].copy()

    gray_cv = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray_cv, (3, 3), 0.1)
    sharpened_cv = cv2.addWeighted(gray_cv, 1.8, blurred, -0.8, 0)

    final_blur = cv2.GaussianBlur(sharpened_cv, (3, 3), 0.1)
    _, binary_output = cv2.threshold(final_blur, 65, 255, cv2.THRESH_BINARY)
    current_path = os.path.join(folder_path, "Binary_Image.jpg")
    cv2.imwrite(current_path, binary_output)

    cv_contours, _ = cv2.findContours(binary_output, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    height, width = binary_output.shape[:2]
    contour_image_cv = np.ones((height, width, 3), dtype=np.uint8) * 255
    cv2.drawContours(contour_image_cv, cv_contours, -1, (0, 255, 0), 1)
    
    drawn_image = Image.fromarray(cv2.cvtColor(contour_image_cv, cv2.COLOR_BGR2RGB))
    if cv_contours:
        plate_contour = None
        for contour in cv_contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            if 2.0 <= aspect_ratio <= 5.5:
                plate_contour = contour
                break

        if plate_contour is None:
            plate_contour = max(cv_contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(plate_contour)
        padding = 5
        y1, y2 = max(0, y - padding), min(height, y + h + padding)
        x1, x2 = max(0, x - padding), min(width, x + w + padding)
        cropped_ocr_input = binary_output[y1:y2, x1:x2]
    else:
        cropped_ocr_input = binary_output

# Global safety catch
if binary_output is None:
    binary_output = np.array(binary_edges_pil)
if cropped_ocr_input is None:
    cropped_ocr_input = binary_output

self.display_image(image_name = "Cropped_Plate.jpg", title = "CONTOURS")
cv2.imwrite(os.path.join(folder_path, "Cropped_Plate.jpg"), cropped_ocr_input)
root = Tk()
root.title("CONTOURS")
tk_image = ImageTk.PhotoImage(drawn_image)
label = Label(root, image=tk_image)
label.pack()
root.after(3000, root.destroy)
root.mainloop()
current_path = os.path.join(folder_path, "Contours.jpg")
drawn_image.save(current_path)



