#!/usr/bin/env python3

import time
import rospy
import random
import string
import asyncio
import aiohttp
import ros_numpy

from sensor_msgs.msg import Image

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRecorder

from custom_stream_track_ros import VideoStreamTrack

pcs = set()
JANUS_URL = 'http://192.168.195.225:8088/janus'
JANUS_ROOM = 1234

vst = VideoStreamTrack()


def transaction_id():
    return "".join(random.choice(string.ascii_letters) for x in range(12))


class JanusPlugin:
    def __init__(self, session, url):
        self._queue = asyncio.Queue()
        self._session = session
        self._url = url

    async def send(self, payload):
        message = {"janus": "message", "transaction": transaction_id()}
        message.update(payload)
        async with self._session._http.post(self._url, json=message) as response:
            data = await response.json()
            assert data["janus"] == "ack"

        response = await self._queue.get()
        assert response["transaction"] == message["transaction"]
        return response


class JanusSession:
    def __init__(self, url):
        self._http = None
        self._poll_task = None
        self._plugins = {}
        self._root_url = url
        self._session_url = None

    async def attach(self, plugin_name: str) -> JanusPlugin:
        message = {
            "janus": "attach",
            "plugin": plugin_name,
            "transaction": transaction_id(),
        }
        async with self._http.post(self._session_url, json=message) as response:
            data = await response.json()
            assert data["janus"] == "success"
            plugin_id = data["data"]["id"]
            plugin = JanusPlugin(self, self._session_url + "/" + str(plugin_id))
            self._plugins[plugin_id] = plugin
            return plugin

    async def create(self):
        self._http = aiohttp.ClientSession()
        message = {"janus": "create", "transaction": transaction_id()}
        async with self._http.post(self._root_url, json=message) as response:
            data = await response.json()
            assert data["janus"] == "success", data
            session_id = data["data"]["id"]
            self._session_url = self._root_url + "/" + str(session_id)

        self._poll_task = asyncio.ensure_future(self._poll())

    async def destroy(self):
        if self._poll_task:
            self._poll_task.cancel()
            self._poll_task = None

        if self._session_url:
            message = {"janus": "destroy", "transaction": transaction_id()}
            async with self._http.post(self._session_url, json=message) as response:
                data = await response.json()
                assert data["janus"] == "success"
            self._session_url = None

        if self._http:
            await self._http.close()
            self._http = None

    async def _poll(self):
        while True:
            params = {"maxev": 1, "rid": int(time.time() * 1000)}
            async with self._http.get(self._session_url, params=params) as response:
                data = await response.json()
                if data["janus"] == "event":
                    plugin = self._plugins.get(data["sender"], None)
                    if plugin:
                        await plugin._queue.put(data)
                    else:
                        print(data)


async def publish(plugin):
    """
    Send video to the room.
    """
    pc = RTCPeerConnection()
    pcs.add(pc)
    pc.addTrack(vst)

    # send offer
    await pc.setLocalDescription(await pc.createOffer())
    response = await plugin.send(
        {
            "body": {
                "request": "configure",
                "audio": False,
                "video": True,
            },
            "jsep": {
                "sdp": pc.localDescription.sdp,
                "trickle": False,
                "type": pc.localDescription.type,
            },
        }
    )
    await pc.setRemoteDescription(
        RTCSessionDescription(
            sdp=response["jsep"]["sdp"], type=response["jsep"]["type"]
        )
    )

async def callback(data):
    # bridge = CvBridge()
    # cv_image = bridge.imgmsg_to_cv2(data, 'bgr16')

    np_img = ros_numpy.numpify(data)
    await vst.setFrame(np_img)
    # (rows, cols, channels) = cv_image.shape

    # rospy.loginfo(
    #     'H: %d, W: %d, rows: %d, cols: %d, channels: %d',
    #     data.height, data.width, rows, cols, channels
    # )


async def run(session):
    await session.create()

    plugin = await session.attach('janus.plugin.videoroom')
    await plugin.send(
        {
            "body": {
                "display": "aiortc",
                "ptype": "publisher",
                "request": "join",
                "room": JANUS_ROOM,
            }
        }
    )
    await publish(plugin=plugin)

    print("Exchanging media")

    rospy.init_node('vtstreamer', anonymous=True)
    rospy.Subscriber('/usb_cam/image_raw', Image, callback)
    rospy.spin()


if __name__ == '__main__':
    session = JanusSession(JANUS_URL)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run(session))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(session.destroy())

        # close peer connections
        coros = [pc.close() for pc in pcs]
        loop.run_until_complete(asyncio.gather(*coros))
