import time
import settings

if settings.PROD:
    import io
    import numpy as np
    from picamera import PiCamera
else:
    import cv2


class Camera(object):
    """PiCamera class abstraction with custom methods"""

    cam = None

    _pic_dir = settings.PICS_DIR
    _vid_dir = settings.VIDEOS_DIR

    _state = None

    def __init__(self, rotation=0):
        if settings.PROD:
            self.cam = PiCamera()
            self.cam.resolution = (640, 480)
            self.cam.rotation = rotation
        else:
            self.cam = cv2.VideoCapture(0)

    def __del__(self):
        if settings.PROD:
            self.cam.close()
        else:
            self.cam.release()

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
        pic_path = f"{self._pic_dir}/{filename or self._ts_name()}.jpg"

        if settings.PROD:
            if gps_data:
                self.cam.exif_tags.update(self._gps_exif(**gps_data))

            self.cam.capture(pic_path, use_video_port=True)
        else:
            _, frame = self.cam.read()
            cv2.imwrite(pic_path, frame)

        return pic_path.split('/')[-1]

    def grab_frame(self):
        if settings.PROD:
            stream = io.BytesIO()
            self.cam.capture(
                stream,
                format="jpeg",
                quality=settings.STREAM_VIDEO_JPEG_QUALITY
            )
            frame = np.fromstring(stream.getvalue(), dtype=np.uint8)
        else:
            frame = self.cam.read()[1]

        return frame

    def start_recording(self, filename=None):
        self.vid_path = f"{self._vid_dir}/{filename or self._ts_name()}.h264"
        if settings.PROD:
            self.cam.start_recording(self.vid_path)
        self._state = 'RECORDING'
        return self.vid_path.split('/')[-1]

    def stop_recording(self):
        if settings.PROD:
            self.cam.stop_recording()
        self._state = None
        return self.vid_path.split('/')[-1]

    @property
    def is_recording(self):
        return self._state == 'RECORDING'
