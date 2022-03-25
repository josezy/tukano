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
    A dummy video track.
    """

    kind = "video"

    _start: float
    _timestamp: int

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
        subclass :class:`VideoStreamTrack` to provide a useful implementation.
        """
        pts, time_base = await self.next_timestamp()

        print('antes')
        frame = VideoFrame.from_ndarray(self._frame, format='bgr16')
        print('despues')
        frame.pts = pts
        frame.time_base = time_base

        return frame

    async def setFrame(self, frame):
        print('setting frame')
        self._frame = frame
