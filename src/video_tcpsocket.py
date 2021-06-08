import io
import socket
import struct
import time
import picamera

# Connect a client socket to my_server:8000 (change my_server to the
# hostname of your server)

camera = picamera.PiCamera()
camera.resolution = (320, 240)
camera.framerate = 30
# Start a preview and let the camera warm up for 2 seconds
camera.start_preview()
time.sleep(2)
while True:
    try:
        client_socket = socket.socket()
        client_socket.connect(('207.246.118.54', 8080))

        # Make a file-like object out of the connection
        connection = client_socket.makefile('wb')
        try:

            # Note the start time and construct a stream to hold image data
            # temporarily (we could write it directly to connection but in this
            # case we want to find out the size of each capture first to keep
            # our protocol simple)
            start = time.time()
            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                # before=time.time()
                # Write the length of the capture to the stream and flush to
                # ensure it actually gets sent

                try:
                    connection.write(struct.pack('<L', stream.tell()))
                    connection.flush()
                    # Rewind the stream and send the image data over the wire
                    stream.seek(0)
                    connection.write(stream.read())
                    # Reset the stream for the next capture
                    stream.seek(0)
                    stream.truncate()
                    # print(f"takes {time.time() - before}")

                except ConnectionResetError:
                    print("WHAA?")
            # Write a length of zero to the stream to signal we're done
            connection.write(struct.pack('<L', 0))
        except BrokenPipeError:
            print("WHAA?")
        # finally:
        #     connection.close()
        #     client_socket.close()
        #     print("DISCONNECTING FROM SOCKET")
    except ConnectionRefusedError:
        print("NO CONNECTION!, RECONECTING IN 5 Seconds")
        time.sleep(5)