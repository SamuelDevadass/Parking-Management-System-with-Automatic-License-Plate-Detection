import cv2
from tkinter import *
from PIL import Image, ImageTk, ImageFilter, ImageDraw, ImageEnhance
from datetime import datetime
import os
import numpy as np
from rapidocr_onnxruntime import RapidOCR
import easyocr

"""I. GLOBAL INITIALIZATIONS"""
rapid_engine = RapidOCR()
easy_reader = easyocr.Reader(['en'], gpu=False)

"""II. IMAGE CAPTURE PIPELINE"""
# Get Camera
camera = cv2.VideoCapture(0)
if not camera:
    print("CAMERA not found\nExiting ... ")
    exit()
print("CAMERA available at : ",camera)

# Get Current Time for logging
now = datetime.now()
print("Current Time: ", now)

# New repository for current cycle
folder_path = now.strftime("%Y-%m-%d_%H-%M-%S") # os.mkdir() returns None hence create path as string and then create folder
os.mkdir(folder_path)

# Capture Video 5 frames
for i in range(5):
    ret, frame = camera.read()
    if not ret:
        print("UNABLE TO ACCESS CAMERA")
        break
    cv2.imshow( f'frame{i}.jpg'.format(i),frame)
    print("CAPTURING FRAME ",i)
    cv2.waitKey(1000)
    current_path = os.path.join(folder_path, f"frame{i}.jpg")
    cv2.imwrite(current_path, frame)

# Display captured image
root=Tk()
root.title("LATEST CAPTURED IMAGE")
#local path for PI
image = Image.open(os.path.join(folder_path, f"frame{4}.jpg"))
tk_image = ImageTk.PhotoImage(image)
label = Label(root,image=tk_image)
label.pack()
# Add timer for 3 seconds
root.after(3000,root.destroy)
root.mainloop() # wont close until user closes window, root.after sets a timer 
camera.release()
current_path = os.path.join(folder_path, "Captured_Image.jpg")
image.save(current_path)

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

"""IV. OCR PIPELINE"""
text = ""
try:
    results, _ = rapid_engine(cropped_ocr_input)
    if not results:
        raise ValueError("No text in cropped zone")
    text = " ".join([line[1] for line in results])
    print(f"RAPIDOCR SUCCESS: {text}")
    
except Exception:
    print("RapidOCR high-speed pass failed. Trying Deep Learning EasyOCR on cropped zone...")
    results = easy_reader.readtext(cropped_ocr_input)
    text = " ".join([detection[1] for detection in results])
    if text:
        print(f"EASYOCR FALLBACK SUCCESS: {text}")
    else:
        print("NO LICENSE PLATE TEXT DETECTED IN CROPPED ZONE.")

"""V. CLEAN-UP"""
if not os.path.exists(folder_path):
    print("FOLDER DOES NOT EXIST . . .")
    exit()
else:
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if filename != "Captured_Image.jpg":
            os.remove(filepath)