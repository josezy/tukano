import cv2
import picamera
from picamera.array import PiRGBArray
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


forensic_video = cv2.VideoWriter('output.avi', -1, 20.0, (640,480))
forensic_message = {
    "vehicle_stats":{},
    "yaw_align":{},
    "marker_stats":{},
    "control_stats":{}
}
proccesing_hz = 10.0
proccesing_timer = time.time()


parent_conn_im, child_conn_im = multiprocessing.Pipe()
imageQueue = Queue.Queue()
vehicleQueue = Queue.Queue()

# connection_string = "udp:127.0.0.1:14551"
connection_string = "/dev/ttyACM0"

print("Connecting to vehicle on: %s" % connection_string)
vehicle = connect(connection_string, wait_ready=True, baud=57600)
print("[INFO] Conected!!")
# Download the vehicle waypoints (commands). Wait until download is complete.
cmds = vehicle.commands
cmds.download()
cmds.wait_ready()

priorized_tag = 0
priorized_tag_counter = {}


def measure_distance(lat1, lon1, lat2, lon2):
    R = 6378.137
    dLat = lat2 * math.pi / 180 - lat1 * math.pi / 180
    dLon = lon2 * math.pi / 180 - lon1 * math.pi / 180
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(
        lat1 * math.pi / 180
    ) * math.cos(lat2 * math.pi / 180) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    return d * 1000


start_land = False

# --------------- PICAMERA INIT SECTION -------------#
# initialize the camera and grab a reference to the raw camera capture
print("[INFO] initializing Picamera...")
camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 10
rawCapture = PiRGBArray(camera, size=camera.resolution)


for image in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = image.array
    if time.time() > proccesing_timer + 1 / proccesing_hz:
        forensic_message["vehicle_stats"]["vehicle_mode"] = vehicle.mode.name
        forensic_message["vehicle_stats"]["vehicle_arm"] = vehicle.armed
        proccesing_timer = time.time()
        if vehicle.armed:
            before_time = time.time()
            location = vehicle.location.global_relative_frame
            attitude = vehicle.attitude
            
            
            forensic_message["vehicle_stats"]["altitude"]=location.alt
            forensic_message["vehicle_stats"]["yaw"]=math.degrees(attitude.yaw)
            try:
                distance_to_home = measure_distance(
                    vehicle.home_location.lat,
                    vehicle.home_location.lon,
                    location.lat,
                    location.lon,
                )

                forensic_message["vehicle_stats"]["distance_to_home"]=distance_to_home
                
                if (
                    not start_land
                    and distance_to_home < 1
                    and location.alt < 10
                    and vehicle.mode == VehicleMode("RTL")
                ):
                    start_land = True
                    

                if start_land:
                    imageQueue.put(frame)
                    vehicleQueue.put((location, attitude))

                    img = multiprocessing.Process(
                        name="img",
                        target=search_image_aruco.analyze_frame,
                        args=(
                            child_conn_im,
                            frame,
                            location,
                            attitude,
                            priorized_tag,
                            priorized_tag_counter,
                            forensic_message
                        ),
                    )
                    img.daemon = True
                    img.start()

                    results = parent_conn_im.recv()

                    priorized_tag_counter = results[3]
                    priorized_tag = results[4]
                    forensic_message = results[6]
                    forensic_message["marker_stats"]["priorized_tag"]=priorized_tag
                    forensic_message["marker_stats"]["priorized_tag_counter"]=priorized_tag_counter

                    if results[5] != None:
                        orientation = 1
                        if results[5] < 0:
                            orientation = -1
                        condition_yaw(
                            vehicle,
                            abs(results[5]),
                            relative=True,
                            orientation=orientation,
                        )                   
                        forensic_message["yaw_align"]["orientation"]=orientation
                        forensic_message["yaw_align"]["value"]=results[5]

                    img = imageQueue.get()

                    location, attitude = vehicleQueue.get()
                    
                    control.land(vehicle, results[1], attitude, location)
                    time.sleep(0.1)

                forensic_message["vehicle_stats"]["home_set"]=True
            except AttributeError:
                forensic_message["vehicle_stats"]["home_set"]=False
                print("no home location set")

            proccesing_hz = 1 / ((time.time() - before_time) * 1.5)
            print("Takes", time.time() - before_time, "Seconds")
        else:            
            start_land = False
        forensic_message["start_land"] = start_land
    else:
        print("not proc")

    rawCapture.truncate(0)
