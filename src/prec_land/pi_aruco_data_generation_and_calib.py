import cv2
from cv2 import aruco
import numpy as np
from aruco_utils import detect_good_board_data, calib_camera, recreate_folder_data
import time


from picamera.array import PiRGBArray
from picamera import PiCamera

#--------------- PICAMERA INIT SECTION -------------#
# initialize the camera and grab a reference to the raw camera capture
print("[INFO] initializing Picamera...")
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 5
rawCapture = PiRGBArray(camera, size=(640, 480))
# allow the camera to warmup
time.sleep(0.1)

#--------------- ARUCO TAG  INIT SECTION -------------#
aruco_dict = aruco.getPredefinedDictionary( aruco.DICT_6X6_1000 )
arucoParams = aruco.DetectorParameters_create()
    
#Provide length of the marker's side
markerLength = 3.6  # Here, measurement unit is centimetre.

# Provide separation between markers
markerSeparation = 0.5   # Here, measurement unit is centimetre.
horizontal_tag_ammount= 4
vertical_tag_ammount= 5

#--------------- DATA SECTION ----------------#
path_images="aruco_images/"
path_config="./"
max_data_ammount = 40
data_ammount = 0    
recreate_folder_data(path_images)

for img in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = img.array   
    data_ammount=detect_good_board_data(
        image,
        arucoParams,
        aruco_dict,
        horizontal_tag_ammount,
        vertical_tag_ammount,
        data_ammount,
        path_images,
    )  
        
    if data_ammount>=max_data_ammount:
        break

    rawCapture.truncate(0)

calib_camera(
    arucoParams,
    aruco_dict,
    horizontal_tag_ammount,
    vertical_tag_ammount, 
    markerLength, 
    markerSeparation, 
    path_config,
    file_name="calibration"
)