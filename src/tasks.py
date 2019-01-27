import json
import time

from datetime import datetime

from settings import DATA_DIR

def collect_data(drone):
    data_collected = {}
    for s in range(10):
        data_collected[s] = {
            'ts': str(datetime.now()),
            'lat': drone.location.global_relative_frame.lat,
            'lon': drone.location.global_relative_frame.lon,
            'alt': drone.location.global_relative_frame.alt,
        }
        print(data_collected[s])
        time.sleep(0.5)

    save_json_file("data.json", data_collected)


def save_json_file(filename, json_data):
    output_file = "{}/{}".format(DATA_DIR, filename)
    with open(output_file, 'w') as outfile:
        json.dump(json_data, outfile)