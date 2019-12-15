Tukano Project
===

Software running on a Raspberry connected to a Pixhawk for multiple aerial purposes.

### Setup

To install packages and setup enviroment run (or follow by steps) the `bin/tukano-setup` file

###### Summary / Notes
* install dependencies (pymavlink, redis, websocket-client, etc)
* if developing, run SITL
* be sure redis-server is running
* generate dialect library `mavgen.py --output=.venv/lib/python3.7/site-packages/pymavlink/dialects/v10/mav_tukano.py dialects/mav_tukano.xml`

---

Use `tukano reload|stop` for reload/stop `supervisor` processes

Use `tukano setup` to create sym links for `supervisor` conf
