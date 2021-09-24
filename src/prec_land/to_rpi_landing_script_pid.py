

import cv2
from PIL import Image
import numpy as np

from dronekit import connect, VehicleMode

# Helper Libraries Imports
import pid_utils.search_image_aruco as search_image_aruco
import pid_utils.search_image as search_image
import pid_utils.control as control
import multiprocessing

from pid_utils.flight_assist import condition_yaw


# Python Imports
import time
import queue as Queue
import math

CONNECT_TO_MAVLINK = False
proccesing_hz = 10.0
proccesing_timer = time.time()


parent_conn_im, child_conn_im = multiprocessing.Pipe()
imageQueue = Queue.Queue()
vehicleQueue = Queue.Queue()

connection_string = 'udp:127.0.0.1:14551'

print("Connecting to vehicle on: %s" % connection_string)
vehicle = connect(connection_string, wait_ready=True, baud=57600)
# Download the vehicle waypoints (commands). Wait until download is complete.
cmds = vehicle.commands
cmds.download()
cmds.wait_ready()

priorized_tag = 0
priorized_tag_counter = { }

def measure_distance(lat1, lon1, lat2, lon2):
    R = 6378.137
    dLat = lat2 * math.pi / 180 - lat1 * math.pi / 180
    dLon = lon2 * math.pi / 180 - lon1 * math.pi / 180
    a = math.sin(dLat/2) * math.sin(dLat/2) +  math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) *    math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d * 1000; 

start_land = False

#--------------- PICAMERA INIT SECTION -------------#
# initialize the camera and grab a reference to the raw camera capture
print("[INFO] initializing Picamera...")
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 5
rawCapture = PiRGBArray(camera, size=camera.resolution )


for image in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = image.array   
    if time.time()>proccesing_timer+1/proccesing_hz:
        
        proccesing_timer=time.time()
        if vehicle.armed :
            before_time= time.time()
            location = vehicle.location.global_relative_frame
            attitude = vehicle.attitude
            try:
                distance_to_home=measure_distance(vehicle.home_location.lat, vehicle.home_location.lon,location.lat,location.lon)
            
                print(vehicle.mode,distance_to_home,location.alt,start_land)
                if not start_land and distance_to_home < 0.5 and location.alt<10 and vehicle.mode ==  VehicleMode('RTL'):
                    start_land = True

                if start_land:
                    imageQueue.put(frame)
                    vehicleQueue.put((location,attitude))

                    img = multiprocessing.Process(name="img",target=search_image_aruco.analyze_frame, args = (child_conn_im, frame, location, attitude,priorized_tag,priorized_tag_counter))
                    img.daemon = True
                    img.start()

                    results = parent_conn_im.recv()

                    priorized_tag_counter=results[3]
                    priorized_tag=results[4]  

                    if results[5] != None:
                        orientation = 1
                        if results[5]<0:
                            orientation = -1 
                        condition_yaw(vehicle,abs(results[5]), relative=True, orientation=orientation)
        
         
                    img = imageQueue.get()
                    
                    location, attitude = vehicleQueue.get()
                    control.land(vehicle, results[1], attitude, location)
                    time.sleep(0.1)
 
            except AttributeError:
                print("no home location set")
            proccesing_hz=1/((time.time()-before_time)*1.5)
            print("Takes", time.time()-before_time,"Seconds")
        else:
            start_land = False
    else:
        print("not proc")

    rawCapture.truncate(0)


