#!/usr/bin/env python3
"""
Camera streaming service using libcamera + GStreamer for Janus WebRTC Gateway
Replaces UV4L for modern Raspberry Pi camera streaming
"""

import os
import sys
import time
import signal
import logging
import subprocess
from settings import PROD

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="[%(levelname)s] %(asctime)s: %(message)s"
)
logger = logging.getLogger(__name__)


class CameraStreamer:
    def __init__(self):
        self.process = None
        self.running = False

        # Janus gateway configuration (from UV4L config)
        self.janus_url = "http://207.246.118.54:8088"  # rata server
        self.janus_room = "1234"
        self.janus_token = "123456789"

        # Camera settings
        self.width = 640
        self.height = 480
        self.framerate = 30
        self.bitrate = 1200000  # 1.2Mbps

        # Signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)

    def _build_gstreamer_pipeline(self):
        """Build GStreamer pipeline for UDP RTP streaming to Janus"""
        # Use v4l2src for camera access on RPi
        pipeline = [
            "gst-launch-1.0", "-v",
            "v4l2src", "device=/dev/video0",
            f"! video/x-raw,width={self.width},height={self.height},framerate={self.framerate}/1",
            "! videoconvert",
            "! v4l2h264enc", f"bitrate={self.bitrate}",
            "! h264parse",
            "! rtph264pay", "config-interval=1", "pt=96",
            "! udpsink", "host=207.246.118.54", "port=5004"
        ]

        return pipeline

    def start(self):
        """Start camera streaming"""
        if self.running:
            logger.warning("Camera stream already running")
            return

        try:
            pipeline = self._build_gstreamer_pipeline()
            logger.info(f"Starting camera stream with pipeline: {' '.join(pipeline)}")

            self.process = subprocess.Popen(
                pipeline,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )

            self.running = True
            logger.info("Camera stream started successfully")

        except Exception as e:
            logger.error(f"Failed to start camera stream: {e}")
            self.running = False

    def stop(self):
        """Stop camera streaming"""
        if not self.running or not self.process:
            return

        try:
            logger.info("Stopping camera stream...")
            self.process.terminate()

            # Wait for graceful shutdown
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Process didn't terminate gracefully, killing...")
                self.process.kill()
                self.process.wait()

            self.running = False
            logger.info("Camera stream stopped")

        except Exception as e:
            logger.error(f"Error stopping camera stream: {e}")

    def is_running(self):
        """Check if camera stream is running"""
        if not self.process:
            return False

        return self.process.poll() is None

    def run(self):
        """Main run loop with restart capability"""
        logger.info("Starting camera streaming service...")

        while True:
            try:
                if not self.is_running():
                    logger.info("Starting camera stream...")
                    self.start()

                # Monitor process
                time.sleep(5)

                if self.process and self.process.poll() is not None:
                    # Process died, restart it
                    logger.warning("Camera stream process died, restarting...")
                    self.running = False
                    time.sleep(2)  # Brief delay before restart

            except KeyboardInterrupt:
                logger.info("Received interrupt, shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(5)

        self.stop()


if __name__ == "__main__":
    streamer = CameraStreamer()
    streamer.run()
