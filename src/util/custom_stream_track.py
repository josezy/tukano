import cv2
import time
import asyncio
import fractions

from av import VideoFrame
from av.frame import Frame
from typing import Tuple
from aiortc import MediaStreamTrack

VIDEO_CLOCK_RATE = 90000
VIDEO_PTIME = 1 / 30  # 30fps
VIDEO_TIME_BASE = fractions.Fraction(1, VIDEO_CLOCK_RATE)

class MediaStreamError(Exception):
    pass

class VideoStreamTrack(MediaStreamTrack):
    """
    A dummy video track which reads green frames.
    """

    kind = "video"

    _start: float
    _timestamp: int

    def __init__(self):
        super().__init__()
        self._cap = cv2.VideoCapture(0, cv2.CAP_V4L)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while not self._cap.isOpened():
            pass

    async def next_timestamp(self) -> Tuple[int, fractions.Fraction]:
        if self.readyState != "live":
            raise MediaStreamError

        if hasattr(self, "_timestamp"):
            self._timestamp += int(VIDEO_PTIME * VIDEO_CLOCK_RATE)
            wait = self._start + (self._timestamp / VIDEO_CLOCK_RATE) - time.time()
            await asyncio.sleep(wait)
        else:
            self._start = time.time()
            self._timestamp = 0
        return self._timestamp, VIDEO_TIME_BASE

    async def recv(self) -> Frame:
        """
        Receive the next :class:`~av.video.frame.VideoFrame`.
        The base implementation just reads a 640x480 green frame at 30fps,
        subclass :class:`VideoStreamTrack` to provide a useful implementation.
        """
        pts, time_base = await self.next_timestamp()

        ret, _frame = self._cap.read()
        frame = VideoFrame.from_ndarray(_frame, format='bgr24')
        frame.pts = pts
        frame.time_base = time_base

        return frame
