import cv2
from cv2 import aruco
import numpy as np
from aruco_utils import detect_good_board_data, calib_camera, recreate_folder_data
import time

cap = cv2.VideoCapture(0)
#--------------- ARUCO TAG  INIT SECTION -------------#
aruco_dict = aruco.getPredefinedDictionary( aruco.DICT_6X6_1000 )
arucoParams = aruco.DetectorParameters_create()
    
#Provide length of the marker's side
markerLength = 3.6  # Here, measurement unit is centimetre.

# Provide separation between markers
markerSeparation = 0.34   # Here, measurement unit is centimetre.
horizontal_tag_ammount= 4
vertical_tag_ammount= 5

#--------------- DATA SECTION ----------------#
path_images="aruco_images/"
path_config="./"
max_data_ammount = 40
data_ammount = 0    
recreate_folder_data(path_images)

while cap.isOpened():
    ret, image = cap.read()
    data_ammount=detect_good_board_data(
        image,
        arucoParams,
        aruco_dict,
        horizontal_tag_ammount,
        vertical_tag_ammount,
        data_ammount,
        path_images,
        show_detections=True
    )  
        
    if data_ammount>=max_data_ammount:
        break
    cv2.imshow("image",image)
    cv2.waitKey(10)
calib_camera(
    arucoParams,
    aruco_dict,
    horizontal_tag_ammount,
    vertical_tag_ammount, 
    markerLength, 
    markerSeparation, 
    path_images,
    file_name="calibration_pc"
)