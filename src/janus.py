import time
import random
import string
import aiohttp
import asyncio
import argparse

from aiortc import RTCPeerConnection, RTCSessionDescription

from util.custom_stream_track import VideoStreamTrack

pcs = set()


def transaction_id():
    return "".join(random.choice(string.ascii_letters) for x in range(12))


class JanusPlugin:
    def __init__(self, session, url):
        self._queue = asyncio.Queue()
        self._session = session
        self._url = url

    async def send(self, payload):
        message = {
            "janus": "message",
            "transaction": transaction_id(),
            "token": self._session._token
        }
        message.update(payload)
        async with self._session._http.post(self._url, json=message) as response:
            data = await response.json()
            assert data["janus"] == "ack"

        response = await self._queue.get()
        assert response["transaction"] == message["transaction"]
        return response


class JanusSession:
    def __init__(self, url, token):
        self._http = None
        self._poll_task = None
        self._plugins = {}
        self._root_url = url
        self._session_url = None
        self._token = token

    async def attach(self, plugin_name: str) -> JanusPlugin:
        message = {
            "janus": "attach",
            "plugin": plugin_name,
            "transaction": transaction_id(),
            "token": self._token
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
        message = {
            "janus": "create",
            "transaction": transaction_id(),
            "token": self._token
        }
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
            message = {
                "janus": "destroy",
                "transaction": transaction_id(),
                "token": self._token
            }
            async with self._http.post(self._session_url, json=message) as response:
                data = await response.json()
                assert data["janus"] == "success"
            self._session_url = None

        if self._http:
            await self._http.close()
            self._http = None

    async def _poll(self):
        while True:
            params = {
                "maxev": 1,
                "rid": int(time.time() * 1000),
                "token": self._token
            }
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

    # configure media
    media = {"audio": False, "video": True}
    pc.addTrack(VideoStreamTrack())

    # send offer
    await pc.setLocalDescription(await pc.createOffer())
    request = {"request": "configure"}
    request.update(media)
    response = await plugin.send(
        {
            "body": request,
            "jsep": {
                "sdp": pc.localDescription.sdp,
                "trickle": False,
                "type": pc.localDescription.type,
            },
        }
    )

    # apply answer
    await pc.setRemoteDescription(
        RTCSessionDescription(
            sdp=response["jsep"]["sdp"], type=response["jsep"]["type"]
        )
    )


async def run(room, session):
    await session.create()

    # join video room
    plugin = await session.attach("janus.plugin.videoroom")
    await plugin.send(
        {
            "body": {
                "display": "aiortc",
                "ptype": "publisher",
                "request": "join",
                "room": room,
            }
        }
    )

    await publish(plugin=plugin)
    print("Exchanging media")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Janus")
    parser.add_argument(
        "url",
        type=str,
        default="http://localhost:8088/janus",
        help="Janus root URL, e.g. http://localhost:8088/janus",
    )
    parser.add_argument(
        "--room",
        type=int,
        default=1234,
        help="The video room ID to join (default: 1234).",
    ),
    parser.add_argument(
        "--token",
        type=str,
        default="janusrocks",
        help="The token to use for authentication (default: janusrocks).",
    )
    args = parser.parse_args()

    # create signaling and peer connection
    session = JanusSession(args.url, token=args.token)

    loop = asyncio.get_event_loop()
    try:
        loop.create_task(run(room=args.room, session=session))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(session.destroy())

        # close peer connections
        coros = [pc.close() for pc in pcs]
        loop.run_until_complete(asyncio.gather(*coros))
