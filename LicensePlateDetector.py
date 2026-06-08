import cv2
from tkinter import *
from PIL import Image, ImageTk, ImageFilter, ImageDraw, ImageEnhance
import ocrspace
from datetime import datetime
import os

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
folder_path = now.strftime("%Y-%m-%d_%H-%M-%S")
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

exit()

root=Tk()
root.title("CAPTURED IMAGE")
#local path for PI
image=Image.open("./frame4.jpg")
tk_image=ImageTk.PhotoImage(image)
label=Label(root,image=tk_image)
label.pack()
root.mainloop()
camera.close()

#IMAGE PREPROCESSING
image=Image.open("/home/pi/Desktop/frame4.jpg")


#ENHANCE IMAGE
enhancer = ImageEnhance.Contrast(image)
enhanced_image = enhancer.enhance(1.3)
#INCREASE SHARPNESS
sharpness_enhancer = ImageEnhance.Sharpness(enhanced_image)
sharpened_image = sharpness_enhancer.enhance(1.8)
sharpened_image=sharpened_image.filter(ImageFilter.GaussianBlur(radius=0.1))
#CONVERT TO GREYSCALE
gray=sharpened_image.convert('L')
#NOISE REDUCTION
gray=gray.filter(ImageFilter.GaussianBlur(radius=0.1))

#CONTOUR DETECTION
threshold = 65
binary_edges = gray.point(lambda p: p > threshold and 255)

#FIND CONTOURS AND ADD TO LIST
contours = []
width, height = binary_edges.size
for x in range(width):
    for y in range(height):
        if binary_edges.getpixel((x, y)) == 255:
            contours.append((x, y))

#CREATE NEW IMAGE WITH CONTOURS
contour_image = Image.new("RGB", binary_edges.size, (255, 255, 255))
for contour_point in contours:
    contour_image.putpixel(contour_point, (0,0,0))

#CREATE A COPY
drawn_image = contour_image.copy()
#DRAW CONTOURS
draw = ImageDraw.Draw(drawn_image)
for contour in contours:
    draw.line(contour, fill='green', width=1)
    
#DISPLAY NEW IMAGE
root=Tk()
root.title("CONTOURS")
tk_image=ImageTk.PhotoImage(drawn_image)
label=Label(root,image=tk_image)
label.pack()
root.mainloop()
#SAVE THE IMAGE
drawn_image.save("contour.png")

#TEXT RECOGNITION
client=ocrspace.API()
result=client.ocr_file("/home/pi/Desktop/contour.png")
print("DETECTED LICENSE NUMBER: ",result)
