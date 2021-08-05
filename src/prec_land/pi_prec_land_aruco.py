# import the necessary packages
import cv2
import time
import numpy as np
from pymavlink import mavutil
from cv2 import aruco
import yaml
import math

# from picamera.array import PiRGBArray
# from picamera import PiCamera

from aruco_utils import update_landing, rgb2gray

DISPLAY_RESULTS = False
CONNECT_MAVLINK = False

#--------------- MAVLINK INIT SECTION -------------#
print("[INFO] connecting Mavlink...")
if CONNECT_MAVLINK:
    drone = mavutil.mavlink_connection("udp:localhost:14551")
    hertz = 1  # betwwen 10 and 50 Hz
    ht = drone.wait_heartbeat()
    print(ht.to_json())
    initialLocation = drone.location()
else:
    fps = 30
    hertz = fps
#--------------- ARUCO TAG  INIT SECTION -------------#

# For validating results, show aruco board to camera.
aruco_dict = aruco.getPredefinedDictionary( aruco.DICT_6X6_1000 )

#Provide length of the marker's side
markerLength = 3.6  # Here, measurement unit is centimetre.

# Provide separation between markers
markerSeparation = 0.5   # Here, measurement unit is centimetre.

horizontal_tag_ammount= 4
vertical_tag_ammount= 5
# create arUco board
board = aruco.GridBoard_create(horizontal_tag_ammount, vertical_tag_ammount, markerLength, markerSeparation, aruco_dict)

arucoParams = aruco.DetectorParameters_create()

with open('calibration.yaml') as f:
    print("LOADED")
    loadeddict = yaml.load(f)

mtx = loadeddict.get('camera_matrix')
dist = loadeddict.get('dist_coeff')
mtx = np.array(mtx)
dist = np.array(dist)

#--------------- PICAMERA INIT SECTION -------------#
# initialize the camera and grab a reference to the raw camera capture
print("[INFO] initializing Picamera...")
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 5
rawCapture = PiRGBArray(camera, size=(640, 480))
# allow the camera to warmup
time.sleep(0.1)


# capture frames from the camera
time_0 = time.time()
for image in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    img = image.array   
    img_aruco = img.copy()
    if time.time() >= time_0 + 1.0/hertz:      
  
        time_0 = time.time()
        before = time.time()
        im_gray = rgb2gray(img).astype(np.uint8)
        h,  w = im_gray.shape[:2]
        corners, ids, rejectedImgPoints = aruco.detectMarkers(im_gray, aruco_dict, parameters=arucoParams)
        if corners == None:
            print ("pass")
        else:

            ret, rvec, tvec = aruco.estimatePoseBoard( corners, ids, board, mtx, dist, None, None)        
            
            if ret != 0:
                
                #-- Calculate angles --#      
                angle_x = math.atan(tvec[0]/tvec[2])
                angle_y = math.atan(tvec[1]/tvec[2])
                dist_to_marker = math.sqrt(tvec[0]**2+tvec[1]**2+tvec[2]**2 )
                #print(angle_x,angle_y,dist_to_marker)
                #-- Print the tag position in camera frame
                if DISPLAY_RESULTS:
                    font = cv2.FONT_HERSHEY_PLAIN        
                    img_aruco = aruco.drawDetectedMarkers(img, corners, ids, (0,255,0))
                    img_aruco = aruco.drawAxis(img_aruco, mtx, dist, rvec, tvec, 10)    # axis length 100 can be changed according to your requirement
                    str_position = "MARKER Position x=%4.0f  y=%4.0f  z=%4.0f"%(tvec[0], tvec[1], tvec[2])
                    cv2.putText(img_aruco, str_position, (0, 100), font, 1, (0, 255, 0), 2, cv2.LINE_AA)  
                    str_attitude = "Angles angle_x=%4.0f  angle_y=%4.0f"%(math.degrees(angle_x),math.degrees(angle_y))
                    cv2.putText(img_aruco, str_attitude, (0, 250), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

                if CONNECT_MAVLINK:
                    update_landing(drone,initialLocation,angle_x,angle_y,tvec,dist_to_marker,hertz)
                print(f"takes {time.time()-before}")
        if DISPLAY_RESULTS:        
            cv2.imshow("Aruco", img_aruco)
            cv2.waitKey(10)
    else:
        pass

    rawCapture.truncate(0)
    # cv2.imshow("World co-ordinate frame axes", img)
