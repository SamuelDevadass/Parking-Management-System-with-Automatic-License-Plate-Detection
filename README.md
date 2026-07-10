# APPLICATION

## Parking Management System with License Plate Detection

STAND ALONE PROTOTYPE APPLICATION WITH FULLY FUNCTIONAL DATABASE AND AUTOMATIC PLATE DETECTION

### DATABASE

Implemented using PostGreSQL and Psycopg

Designed to support organizations with multiple centres, wings, floors and spots
    
    Eg: Organization Seasons Mall
            Centre: Seasons Mall Parking Centre
                Wing:   Seasons Mall Parking Centre Wing 1
                Floors: B1,B2,B3
                Spots: Multiple spots for Two Wheelers and Four Wheelers Available per floor
Supports comprehensive logging for robust performance

### USER INTERFACE

Implemented using TKinter

Designed to support multiple pages dedicated to specific user activities
    
    Eg: Choose Wing
        Automatic License Number Plate Detection
        Input User Details
        Mark Entry/Exit
        Generate Bill 
Supports Interactive design for enhanced efficiency

### AUTOMATIC LICENSE PLATE DETECTION

Integrated YOLO_Monolith for Automatic License Number Detection

Implemented using YOLO, OpenCV, EasyOCR and Pillow

Includes automatic fallbacks with custom image enhancement pipeline against confidence score checks


-----------------------------------------------------------------------------------------------------

### QUICK DEV PATCHES

#### Tools and Technologies

PostgreSQL, Psycopg, Tkinter, YOLO, EasyOCR, OpenCV, Pillow, RapidOCR

#### CONFIGURATIONS

    i. Folder Structure
    
    root/
    -   .env
    -   .gitignore
    -   README.md
    -   requirements.txt
    -   requirements.bak
    +---.vscode/
    -       settings.json
    +---app_frontend/
        -   app.py
        -   __init__.py
    +---backend/
        -   LicensePlateDetector.py
        -   yolo26n.pt
        -   __init__.py
    +---db/
    -       .sql
    +---venv

    ii. Environment Variables
    
    Configure following DB variables to develop Psycopg connection string
        
        DB_NAME = 
        DB_USER = 
        DB_PW = 
        DB_HOST = 

    iii. Environment Setup
    
    -> Clone the repository/branch using command: 
    
    -> Create venv using command python -m create venv venv
    
    -> Activate the venv
    
    -> Install requirements using command pip install -r requirements.txt
    
       (Incase required, install other requirements from requirements.bak file)
    
    -> Implement the DB using postgresql with the SQL from ./db/.sql
    
       Refer to diagrams in ./db and issues for detailed Schema and ER diagram
    
    -> Run the application using the command python -m app_frontend.app

#### PRO TIPS

    i. Ensure the .gitignore contains the lines:

        frame*.jpg
        202*/
        202*/*.jpg
      
      This ensures the folders created during YOLO capture cycles are not tracked by Git

    ii. venv startup:
    
        -> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Remote
    
        -> ./venv/scripts/Activate

    iii. Pipreqs library 
    
         To add only those libraries actually imported in the files
    
         Command: pipreqs . --force

# CITATION

If you use this project, please credit https://github.com/SamuelDevadass/License-Plate-Detector

Citation: [Parking Management & License Number Detection / Application], Samuel (2026). Available at: [https://github.com/SamuelDevadass/License-Plate-Detector/tree/Application]

