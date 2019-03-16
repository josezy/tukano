from datetime import datetime

from sensor_tasks import am2302_measure

def collect_data(gps_raw):

    # this is a syncronous job that blocks normal flow
    # TODO: run sensor mesasures async, then get the last sensed value here
    am2302_data = am2302_measure()

    new_data = {
        'dt': str(datetime.now()),
        'pos': {
            'lat': float(gps_raw.lat) / 10**7,
            'lon': float(gps_raw.lon) / 10**7,
            'alt': float(gps_raw.alt) / 10**3,
        },
        'am2302': am2302_data,
    }
    return new_data
