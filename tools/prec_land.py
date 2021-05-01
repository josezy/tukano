import time
import math

from pymavlink import mavutil

hertz = 30  # betwwen 10 and 50 Hz

drone = mavutil.mavlink_connection("udp:localhost:14551")
ht = drone.wait_heartbeat()
print(ht.to_json())

# drone.param_set_send("PLND_ENABLED", 1)
# drone.param_set_send("PLND_TYPE", 1)
# drone.param_set_send("RNGFND1_TYPE", 1)
# drone.param_set_send("RNGFND1_MIN_CM", 0)
# drone.param_set_send("RNGFND1_MAX_CM", 4000)
# drone.param_set_send("RNGFND1_SCALING", 12.12)
# drone.param_set_send("RNGFND1_PIN", 0)
# drone.param_set_send("SIM_SONAR_SCALE", 12)

horizontal_fov = math.radians(54)
vertical_fov = math.radians(41)
horizontal_res = 640
vertical_res = 480

x = 100
y = -100
angle_x = (x - horizontal_res / 2) * horizontal_fov / horizontal_res
angle_y = (y - vertical_res / 2) * vertical_fov / vertical_res
print("Sending", x, y, angle_x, angle_y)

initialLocation = drone.location()
while True:
    globalPosInt = drone.recv_match(type='GLOBAL_POSITION_INT', blocking=True)

    drone.mav.landing_target_send(
        globalPosInt.time_boot_ms * 1000,  # time in us since system boot
        0,
        0,  # mavutil.mavlink.MAV_FRAME_BODY_NED
        angle_x,
        angle_y,
        drone.location().alt - initialLocation.alt,  # distance drone-target
        # 0, 0  # Size of target in radians
        horizontal_fov, vertical_fov
    )
    # print("sent", angle_x, angle_y, horizontal_fov, vertical_fov)
    time.sleep(1 / hertz)
    print(time.time())


# velocity_x = 5
# velocity_y = 0
# velocity_z = 0
# drone.mav.set_position_target_local_ned_send(
#     0,  # time_boot_ms (not used)
#     0, 0,  # target system, target component
#     mavutil.mavlink.MAV_FRAME_LOCAL_NED,  # frame
#     0b0000111111000111,  # type_mask (only speeds enabled)
#     0, 0, 0,  # x, y, z positions (not used)
#     velocity_x, velocity_y, -velocity_z,  # x, y, z velocity in m/s
#     # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
#     0, 0, 0,
#     0, 0  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
# )

# Configuration params in QGroundControl for simulation WITH this Script
# PLND_ENABLED = Enabled
# PLND_TYPE = CompanionComputer
# PLND_EST_TYPE = KalmanFilter
# RNGFND1_MAX_CM = 4000CM
# RNGFND1_MIN_CM = 0 CM
# RNGFND1_SCALING = 12.120 m/V
# RNGFND1_TYPE = Analog
# SIM_PLD_ENABLE = 0
# After doing this you must reboot the simulator

# Configuration params in QGroundControl for simulation WITHOUT this Script (The previus one plus ..)
# PLND_TYPE = SITL
# SIM_SONAR_SCALE = 12
# SIM_PLD_ENABLE = 1
# SIM_PLD_LAT = -35.364 #This parameter must be diferent from the initial location and the change must be notice in only three decimals
# SIM_PLD_LON 149.162 #Same note that latitude
# SIM_PLD_HEIGHT = 0
# SIM_PLD_ALT_LMT = 15
# SIM_PLD_DIST_LMT = 10
# After doing this you must reboot the simulator
