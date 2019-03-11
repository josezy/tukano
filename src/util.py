import os
import json
import settings

def append_json_file(filename, new_data):
    file_path = "{}/{}".format(settings.DATA_DIR, filename)

    data_collected = load_json_file(file_path)

    # append data to 'data_collected' dict
    data_collected[len(data_collected)] = new_data

    save_json_file(file_path, data_collected)

def save_json_file(file_path, json_data):
    with open(file_path, 'w') as fp:
        json.dump(json_data, fp)

def load_json_file(file_path):
    if not os.path.isfile(file_path):
        with open(file_path, 'w+') as fp:
            json.dump({}, fp)
        return {}

    with open(file_path, 'r') as fp:
        data = json.load(fp)
    return data
