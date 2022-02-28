import io
import os
import json
import settings


def append_json_file(filename, new_data):
    file_path = f"{settings.LOGS_DIR}/{filename}"
    data_collected = load_json_file(file_path)

    data_collected += [new_data]
    save_json_file(file_path, data_collected)


def save_json_file(file_path, json_data):
    with open(file_path, 'w') as fp:
        json.dump(json_data, fp)


def load_json_file(file_path):
    if not os.path.isfile(file_path):
        with open(file_path, 'w+') as fp:
            json.dump([], fp)
        return []

    with open(file_path, 'r+') as fp:
        try:
            data = json.load(fp)
        except Exception:
            fp.truncate(0)
            json.dump([], fp)
            data = []
    return data

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False
