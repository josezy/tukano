# import os
# import json
# import settings

from datetime import datetime

from celery_tasks import am2302_measure

def collect_data(drone):

    # this is a syncronous job that blocks normal flow
    am2302_data = am2302_measure()

    new_data = {
        'dt': str(datetime.now()),
        'pos': {
            'lat': drone.location.global_relative_frame.lat,
            'lon': drone.location.global_relative_frame.lon,
            'alt': drone.location.global_relative_frame.alt,
        },
        'am2302': am2302_data,
    }
    print(new_data)
    return new_data

    # append_json_file(filename, new_data)

# def append_json_file(filename, new_data):
#     file_path = "{}/{}".format(settings.DATA_DIR, filename)

#     data_collected = load_json_file(file_path)

#     # append data to 'data_collected' dict
#     data_collected[len(data_collected)] = new_data

#     save_json_file(file_path, data_collected)

# def save_json_file(file_path, json_data):
#     with open(file_path, 'w') as fp:
#         json.dump(json_data, fp)

# def load_json_file(file_path):
#     if not os.path.isfile(file_path):
#         with open(file_path, 'w+') as fp:
#             json.dump({}, fp)
#         return {}

#     with open(file_path, 'r') as fp:
#         data = json.load(fp)
#     return data
