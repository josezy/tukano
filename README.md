Tukano Project
===

Software running on a Raspberry connected to a Pixhawk for multiple aerial purposes.

### Setup

To install packages and setup enviroment run (or follow by steps) the `bin/tukano-setup` file

###### Summary / Notes
* install requirements (pymavlink, redis, websocket-client, etc)
* if developing, run SITL
* be sure redis-server is running
* copy dialects `cp dialects/* .venv/lib/python3.7/site-packages/message_definitions/v1.0/` (make sure dir exists)
* run `python src/tukano_service.py`

## Useful commands

* Run simulator (SITL Ardupilot) `sim_vehicle.py -v ArduCopter` 
* Run tukano service `python src/tukano_service.py`
* Open logs `mavlogdump.py --type PL logs/00000021.BIN`

