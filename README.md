Tukano Project
===

Software running on a Raspberry connected to a Pixhawk for multiple aerial purposes.

## Super quick setup for RPi
0. Clone the repo (duh)
1. Execute `./bin/tukano-setup`

### Setup

To install packages and setup enviroment run (or follow by steps) the `bin/tukano-setup` file. Or follow summary commands

###### Summary / Notes
* install requirements `pip install -r dev-requirements.txt`
* if developing, run simulator (SITL Ardupilot): `sim_vehicle.py -v ArduCopter` or `dronekit-sitl copter --home=6.145663,-75.388640,2110,0`
* make sure redis-server is running
* Copy dialects `cp dialects/* .venv/lib/python3.7/site-packages/message_definitions/v1.0/` (make sure dir exists)
* Run tukano service: `python src/tukano_service.py`
* Inspect log: `mavlogdump.py --type PL logs/00000021.BIN`

### UV4L janus notes
#### Start/Stop janus stream
```
curl -s 'http://raspberrypi_ip:8080/janus?action=Start' > /dev/null
curl -s 'http://raspberrypi_ip:8080/janus?action=Stop' > /dev/null
```

#### URLs to access uv4l server video stream
```
http://raspberrypi_ip:8080/stream/video.mjpeg
http://raspberrypi_ip:8080/stream/video.h264
http://raspberrypi_ip:8080/stream/video.jpeg
```
