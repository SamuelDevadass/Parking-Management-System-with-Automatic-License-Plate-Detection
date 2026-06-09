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
"""III.A. OPENCV"""
open_cv_image = np.array(image)
open_cv_image = open_cv_image[:,:,::-1].copy() # RGB to BGR for opencv standards

gray_cv = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY) # Greyscale
blurred = cv2.GaussianBlur(gray_cv, (3,3), 0.1) # Gaussian Blur
sharpened_cv = cv2.addWeighted(gray_cv, 1.8, blurred, -0.8, 0) # Sharpen

# Noise reduction and thresholding
final_blur = cv2.GaussianBlur(sharpened_cv, (3, 3), 0.1) # apply blur again
_, binary_edges_cv = cv2.threshold(final_blur, 65, 255, cv2.THRESH_BINARY) # save as binary black & white image
current_path = os.path.join(folder_path, "Binary_Image.jpg")
cv2.imwrite(current_path, binary_edges_cv)


# Contour detection
cv_contours, _ = cv2.findContours(binary_edges_cv, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

# Confidence Score
confidence_score = 1.0 if len(cv_contours) > 0 else 0.0
if confidence_score > 0.5:
    print(f"Confidence Score: {confidence_score} - Using Fast OpenCV Execution")
    height, width = binary_edges_cv.shape[:2]
    contour_image_cv = np.ones((height, width, 3), dtype=np.uint8) * 255 # New image with contours
    cv2.drawContours(contour_image_cv, cv_contours, -1, (0, 255, 0), 1) # draws all geometric outlines in green with a width of 1
    drawn_image = Image.fromarray(cv2.cvtColor(contour_image_cv, cv2.COLOR_BGR2RGB)) # convert to Pillow image

else:
    print(f"Confidence Score: {confidence_score} - below Threshold 0.5, falling back to Pillow Execution\nRetrying - - - - -")
    """III.B. PILLOW"""
    enhancer = ImageEnhance.Contrast(image) # Enhance Image
    enhanced_image = enhancer.enhance(1.3)
    sharpness_enhancer = ImageEnhance.Sharpness(enhanced_image) # Increase Sharpness
    sharpened_image = sharpness_enhancer.enhance(1.8)
    sharpened_image=sharpened_image.filter(ImageFilter.GaussianBlur(radius=0.1))
    gray=sharpened_image.convert('L') # Convert to ,greyscale
    gray=gray.filter(ImageFilter.GaussianBlur(radius=0.1)) # Noise reduction


    # Contour detection
    threshold = 65
    binary_edges = gray.point(lambda p: p > threshold and 255)
    contours = []
    width, height = binary_edges.size
    for x in range(width):
        for y in range(height):
            if binary_edges.getpixel((x, y)) == 255:
                contours.append((x, y))

    contour_image = Image.new("RGB", binary_edges.size, (255, 255, 255))
    for contour_point in contours:
        contour_image.putpixel(contour_point, (0,0,0))

    drawn_image = contour_image.copy()
    #DRAW CONTOURS
    draw = ImageDraw.Draw(drawn_image)
    for contour in contours:
        draw.line(contour, fill='green', width=1)
    

root=Tk()
root.title("CONTOURS")
tk_image=ImageTk.PhotoImage(drawn_image)
label=Label(root,image=tk_image)
label.pack()
root.after(3000,root.destroy)
root.mainloop()
camera.release()
current_path = os.path.join(folder_path, "Contours.jpg")
drawn_image.save(current_path)

"""IV. OCR PIPELINE"""
"""IV.A. RAPIDOCR"""
results, _ = rapid_engine(binary_edges_cv)
if results and results[0][2] > 0.85: # threshold
    text = " ".join([line[1] for line in results])
    print(f"DETECTED LICENSE PLATE REGISTRATION NUMBER: {text}")
else:
    print("Confidence Score below Threshold, falling back to EasyOCR Deep Learning Networks\nRetrying - - - - -")
    results = easy_reader.readtext(np.array(drawn_image)) # easyocr expects numpy array not image object
    text = " ".join([line[1] for line in results])
    print(f"DETECTED LICENSE PLATE REGISTRATION NUMBER: {text}")
