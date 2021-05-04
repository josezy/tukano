Tukano Project
===

Software running on a Raspberry connected to a Pixhawk for multiple aerial purposes.

### Setup

To install packages and setup enviroment run (or follow by steps) the `bin/tukano-setup` file. Or follow summary commands

###### Summary / Notes
* install requirements `pip install -r dev-requirements.txt`
* if developing, run simulator (SITL Ardupilot): `sim_vehicle.py -v ArduCopter` or `dronekit-sitl copter --home=6.145663,-75.388640,2110,0`
* make sure redis-server is running
* Copy dialects `cp dialects/* .venv/lib/python3.7/site-packages/message_definitions/v1.0/` (make sure dir exists)
* Run tukano service: `python src/tukano_service.py`
* Inspect log: `mavlogdump.py --type PL logs/00000021.BIN`

