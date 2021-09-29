import cv2
import picamera
from picamera.array import PiRGBArray
from PIL import Image
import numpy as np

from dronekit import connect

# Helper Libraries Imports
from pid_utils.main_proccess import  procces_frame
# Python Imports
import time


fourcc = cv2.VideoWriter_fourcc(*'XVID')
forensic_video = cv2.VideoWriter('output.avi', fourcc, 10.0, (640,  480))
forensic_message = {
    "vehicle_stats":{},
    "yaw_align":{},
    "marker_stats":{},
    "control_stats":{}
}
forensic_message["start_land"] = False
forensic_message["proccesing_hz"] = 10.0
forensic_message["proccesing_timer"] = time.time()


connection_string = 'udp:127.0.0.1:14551'

print("Connecting to vehicle on: %s" % connection_string)
vehicle = connect(connection_string, wait_ready=True, baud=57600)
# Download the vehicle waypoints (commands). Wait until download is complete.
cmds = vehicle.commands
cmds.download()
cmds.wait_ready()

forensic_message["priorized_tag"] = 0
forensic_message["priorized_tag_counter"] = {}


# --------------- PICAMERA INIT SECTION -------------#
# initialize the camera and grab a reference to the raw camera capture
print("[INFO] initializing Picamera...")
camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 10
rawCapture = PiRGBArray(camera, size=camera.resolution)


for image in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = image.array
    procces_frame(frame,forensic_video, forensic_message, vehicle)
    
    rawCapture.truncate(0)
