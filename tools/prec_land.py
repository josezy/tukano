import time
import math

from pymavlink import mavutil

hertz = 40

drone = mavutil.mavlink_connection("udp:localhost:14550")
ht = drone.wait_heartbeat()
print(ht.to_json())

horizontal_fov = math.radians(54)
vertical_fov = math.radians(41)
horizontal_res = 640
vertical_res = 480

x = 600
y = 400
angle_x = (x - horizontal_res / 2) * horizontal_fov / horizontal_res
angle_y = (y - vertical_res / 2) * vertical_fov / vertical_res
print("Sending", x, y, angle_x, angle_y)
while True:
    drone.mav.landing_target_send(
        0,
        0,
        0,  # mavutil.mavlink.MAV_FRAME_BODY_NED
        angle_x,
        angle_y,
        2,  # Distance
        # 0, 0  # Size of target in radians
        horizontal_fov, vertical_fov
    )
    # print("sent", angle_x, angle_y, horizontal_fov, vertical_fov)
    time.sleep(1 / hertz)


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
