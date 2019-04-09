import time
import settings


def am2302_measure():
    import Adafruit_DHT
    humidity, temperature = Adafruit_DHT.read_retry(
        Adafruit_DHT.AM2302,
        settings.AM2302_PINS['out']
    )
    # from random import random
    # humidity, temperature = 90 + 3 * random(), 17 + 3 * random()
    data = {
        'ts': time.time(),
        'humidity': float("{:.2f}".format(humidity)),
        'temperature': float("{:.2f}".format(temperature)),
    }
    return data


def collect_data(position):
    from datetime import datetime

    # this is a syncronous job that blocks normal flow
    # TODO: run sensor mesasures async, then get the last sensed value here
    am2302_data = am2302_measure()

    new_data = {
        'dt': str(datetime.now()),
        'pos': {
            'lat': float(position.lat) / 10**7,
            'lon': float(position.lon) / 10**7,
            'alt': float(position.alt) / 10**3,
        },
        'am2302': am2302_data,
    }
    return new_data





class camera(object):
    """PiCamera class abstraction with custom methods"""

    cam = None

    _pic_dir = settings.PICS_DIR
    _vid_dir = settings.VIDEOS_DIR

    def __init__(self):
        from picamera import PiCamera
        self.cam = PiCamera()
        self.cam.rotation = 180

    def __del__(self):
        self.cam.close()
        self.cam = None

    def _ts_name(self):
        return time.strftime("%Y%m%d_%H%M%S")

    def _decdeg_to_dms(self, dd):
        mins, secs = divmod(dd * 3600, 60)
        deg, mins = divmod(mins, 60)
        return deg, mins, secs

    def _gps_exif(self, lat, lon, alt):
        lat_d, lat_m, lat_s = self._decdeg_to_dms(abs(lat))
        fractional_lat_str = "{:.0f}/1,{:.0f}/1,{:.0f}/100".format(
            lat_d, lat_m, lat_s * 100
        )
        lat_ref = 'N' if lat > 0 else 'S'

        lon_d, lon_m, lon_s = self._decdeg_to_dms(abs(lon))
        fractional_lon_str = "{:.0f}/1,{:.0f}/1,{:.0f}/100".format(
            lon_d, lon_m, lon_s * 100
        )
        lon_ref = 'E' if lon > 0 else 'W'

        fractional_alt_str = "{:.0f}/100".format(abs(alt) * 100)
        alt_ref = '0' if alt > 0 else '1'

        return {
            'GPS.GPSLatitude': fractional_lat_str,
            'GPS.GPSLatitudeRef': lat_ref,
            'GPS.GPSLongitude': fractional_lon_str,
            'GPS.GPSLongitudeRef': lon_ref,
            'GPS.GPSAltitude': fractional_alt_str,
            'GPS.GPSAltitudeRef': alt_ref,
        }

    def take_pic(self, filename=None, gps_data=None):
        pic_path = "{}/{}.jpg".format(
            self._pic_dir,
            filename or self._ts_name()
        )

        if gps_data:
            self.cam.exif_tags.update(self._gps_exif(**gps_data))

        self.cam.capture(pic_path, use_video_port=True)

        return pic_path.split('/')[-1]

    def start_recording(self, filename=None):
        self.vid_path = "{}/{}.h264".format(
            self._vid_dir,
            filename or self._ts_name()
        )
        self.cam.start_recording(self.vid_path)
        
    def stop_recording(self):
        self.cam.stop_recording()
        return self.vid_path.split('/')[-1]

