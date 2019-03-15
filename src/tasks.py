from datetime import datetime

from sensor_tasks import am2302_measure

def collect_data(drone):

    # this is a syncronous job that blocks normal flow
    # TODO: run sensor mesasures async, then get the last sensed value here
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

