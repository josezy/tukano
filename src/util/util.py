import os
import json
import settings


def append_json_file(filename, new_data):
    file_path = f"{settings.LOGS_DIR}/{filename}"
    data_collected = load_json_file(file_path)

    data_collected += [new_data]
    save_json_file(file_path, data_collected)


def save_json_file(file_path, json_data):
    with open(file_path, 'w+') as file:
        json.dump(json_data, file)


def load_json_file(file_path):
    if not os.path.isfile(file_path):
        with open(file_path, 'w+') as file:
            data = []
            json.dump(data, file)
        return data

    with open(file_path, 'r+') as file:
        try:
            data = json.load(file)
        except Exception:
            file.truncate(0)
            data = []
            json.dump(data, file)
    return data
