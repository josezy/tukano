
import cv2
from cv2 import aruco
forensic_message_tags = {
    "vehicle_stats":{},
    "yaw_align":{},
    "marker_stats":{},
    "control_stats":{}
}
def draw_info(frame,forensic_video,forensic_message, show=False):
    main_tag_text = "no tag"
    vehicle_stats_text = "mode: "+forensic_message["vehicle_stats"]["vehicle_mode"]
    control_stats = "vx: "+str(forensic_message["control_stats"]["vx"])[0:5]+" vy: "+str(forensic_message["control_stats"]["vy"])[0:5]+" vz: "+str(forensic_message["control_stats"]["vz"])[0:5]
    if forensic_message["marker_stats"]["some_tag_detected"]:
        main_tag_text = "following tag #"+str(forensic_message["marker_stats"]["priorized_tag"])
        frame = aruco.drawDetectedMarkers(frame, forensic_message["marker_stats"]["corners"], forensic_message["marker_stats"]["ids"], (0,255,0))
        
    font = cv2.FONT_HERSHEY_SIMPLEX    
    thickness = 1    
    color = (255, 0, 0)
    
    fontScale = 0.4
    cv2.putText(frame, main_tag_text, (10, 10), font, 
                   fontScale, color, thickness, cv2.LINE_AA)
                   
    cv2.putText(frame, vehicle_stats_text, (10, 30), font, 
                   fontScale, color, thickness, cv2.LINE_AA)
                   
    cv2.putText(frame, control_stats, (10, 50), font, 
                   fontScale, color, thickness, cv2.LINE_AA)
    
    forensic_video.write(frame)

    if show:
        cv2.imshow("frame", frame)
        cv2.waitKey(10)

if __name__ == "__main__":
	print("wwwwwwwaaaaaaaaaa")