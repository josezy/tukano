import os
import json
import settings

def append_json_file(filename, new_data, data_key):
    file_path = f"{settings.LOGS_DIR}/{filename}"
    data_collected = load_json_file(file_path, data_key)

    data_collected[data_key].append( new_data )
    save_json_file(file_path, data_collected)


def save_json_file(file_path, json_data):
    with open(file_path, 'w+') as file:
        json.dump(json_data, file)


def load_json_file(file_path, data_key):
    if not os.path.isfile(file_path):
        with open(file_path, 'w+') as fp:
            data = {}
            data[data_key] = []
            json.dump(data, fp)
        return data

    with open(file_path, 'r+') as fp:
        try:
            data = json.load(fp)
        except Exception:
            fp.truncate(0)
            data = {}
            data[data_key] = []
            json.dump(data, fp)           
    return data