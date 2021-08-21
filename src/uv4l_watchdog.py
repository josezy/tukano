import time
import requests

SLEEPING_TIME = 1000
UV4L_URL = "http://localhost:8080/janus"
VIDEO_STARTED = False


while True:
  time.sleep(SLEEPING_TIME)

  if VIDEO_STARTED:
    resp = requests.get(UV4L_URL)
    if resp.status_code == 200:
      if "fieldset disabled" in str(resp.content):
        SLEEPING_TIME = 5000
      else:
        VIDEO_STARTED = False

  else:
    SLEEPING_TIME = 1000
    resp = requests.get(f"{UV4L_URL}?action=Start")
    if resp.status_code == 200:
      VIDEO_STARTED = "fieldset disabled" in str(resp.content)

