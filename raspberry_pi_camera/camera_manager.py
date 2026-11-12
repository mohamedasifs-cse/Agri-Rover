"""
Thread-safe OpenCV Camera Manager for Raspberry Pi 5 USB Webcam.
Manages a single physical VideoCapture instance, serving multiple HTTP clients
safely via MJPEG streaming and snapshot capture without camera contention.
"""

import os
import sys
import time
import logging
import threading
from typing import Optional, Tuple, Dict, Any
import cv2
import numpy as np

logger = logging.getLogger("AgriRoverCamera")
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
)


class CameraManager:
    """
    Singleton-capable thread-safe camera manager for physical USB webcams.
    """

    def __init__(
        self,
        device_index: int = 0,
        width: int = 640,
        height: int = 480,
        fps: int = 15,
        jpeg_quality: int = 80,
    ):
        self.device_index = int(os.getenv("CAMERA_INDEX", device_index))
        self.requested_width = int(os.getenv("CAMERA_WIDTH", width))
        self.requested_height = int(os.getenv("CAMERA_HEIGHT", height))
        self.requested_fps = int(os.getenv("CAMERA_FPS", fps))
        self.jpeg_quality = int(os.getenv("CAMERA_JPEG_QUALITY", jpeg_quality))

        # Runtime state
        self._cap: Optional[cv2.VideoCapture] = None
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._thread: Optional[threading.Thread] = None
        self._is_running = False
        self._stop_requested = False

        # Current frame buffers
        self._latest_raw_frame: Optional[np.ndarray] = None
        self._latest_jpeg: Optional[bytes] = None
        self._last_frame_timestamp: float = 0.0
        self._frame_count: int = 0
        self._active_clients: int = 0
        self._error_message: Optional[str] = None

        # Camera actual capabilities
        self.actual_width: int = 0
        self.actual_height: int = 0
        self.actual_fps: float = 0.0
        self.backend_name: str = "AUTO"

    def _select_backend(self) -> int:
        """Select appropriate OpenCV capture backend based on OS."""
        if sys.platform.startswith("linux"):
            # Raspberry Pi OS (V4L2 is standard for USB webcams)
            self.backend_name = "V4L2"
            return cv2.CAP_V4L2
        elif sys.platform == "win32":
            self.backend_name = "DSHOW"
            return cv2.CAP_DSHOW
        else:
            self.backend_name = "ANY"
            return cv2.CAP_ANY

    def start(self) -> Tuple[bool, str]:
        """
        Initialize and start the camera thread.
        Thread-safe: will return True if already running.
        """
        with self._lock:
            if self._is_running and self._cap is not None and self._cap.isOpened():
                return True, "Camera is already running"

            self._error_message = None
            backend = self._select_backend()
            logger.info(
                f"Opening USB webcam at index {self.device_index} with backend {self.backend_name}..."
            )

            try:
                cap = cv2.VideoCapture(self.device_index, backend)
            except Exception as e:
                self._error_message = f"Exception opening camera device: {e}"
                logger.error(self._error_message)
                return False, self._error_message

            if not cap.isOpened():
                # Fallback to cv2.CAP_ANY if specific backend fails
                logger.warning(
                    f"Failed with {self.backend_name}, falling back to cv2.CAP_ANY..."
                )
                try:
                    cap = cv2.VideoCapture(self.device_index, cv2.CAP_ANY)
                    self.backend_name = "ANY"
                except Exception as e:
                    self._error_message = f"Fallback opening failed: {e}"
                    logger.error(self._error_message)
                    return False, self._error_message

            if not cap.isOpened():
                self._error_message = (
                    f"Could not open USB camera at index {self.device_index}. "
                    "Ensure device is connected, check permissions (e.g. video group), "
                    "or verify index with 'v4l2-ctl --list-devices'."
                )
                logger.error(self._error_message)
                return False, self._error_message

            # Configure resolution and FPS
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.requested_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.requested_height)
            cap.set(cv2.CAP_PROP_FPS, self.requested_fps)

            # Query actual negotiated settings
            self.actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.actual_fps = float(cap.get(cv2.CAP_PROP_FPS))

            logger.info(
                f"Camera opened successfully. Configured: {self.actual_width}x{self.actual_height} @ {self.actual_fps:.1f} FPS"
            )

            # Test-read first frame
            ret, frame = cap.read()
            if not ret or frame is None:
                cap.release()
                self._error_message = "Camera device opened but failed to read initial frame."
                logger.error(self._error_message)
                return False, self._error_message

            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality]
            _, jpeg_buf = cv2.imencode(".jpg", frame, encode_param)

            self._cap = cap
            self._latest_raw_frame = frame
            self._latest_jpeg = jpeg_buf.tobytes()
            self._last_frame_timestamp = time.time()
            self._is_running = True
            self._stop_requested = False

            # Start worker thread
            self._thread = threading.Thread(
                target=self._capture_worker,
                name="AgriRoverCamWorker",
                daemon=True
            )
            self._thread.start()
            return True, "Camera started successfully"

    def _capture_worker(self):
        """Dedicated background thread reading frames at steady target FPS."""
        logger.info("Camera capture worker thread started.")
        target_interval = 1.0 / max(1.0, self.requested_fps)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality]
        consecutive_read_failures = 0
        max_consecutive_failures = 15

        while not self._stop_requested:
            start_time = time.time()

            with self._lock:
                cap = self._cap

            if cap is None or not cap.isOpened():
                logger.warning("Camera handle is no longer valid. Exiting capture worker.")
                break

            ret, frame = cap.read()
            if ret and frame is not None:
                consecutive_read_failures = 0
                success, jpeg_buf = cv2.imencode(".jpg", frame, encode_param)

                if success:
                    with self._condition:
                        self._latest_raw_frame = frame
                        self._latest_jpeg = jpeg_buf.tobytes()
                        self._last_frame_timestamp = time.time()
                        self._frame_count += 1
                        self._condition.notify_all()
            else:
                consecutive_read_failures += 1
                logger.warning(
                    f"Frame read failed (attempt {consecutive_read_failures}/{max_consecutive_failures})"
                )
                if consecutive_read_failures >= max_consecutive_failures:
                    logger.error("Too many consecutive read failures. Marking camera as disconnected.")
                    with self._lock:
                        self._error_message = (
                            "Camera read disconnected or device dropped. "
                            "Please check the USB connection."
                        )
                    break
                time.sleep(0.05)
                continue

            elapsed = time.time() - start_time
            sleep_time = target_interval - elapsed
            if sleep_time > 0.001:
                time.sleep(sleep_time)

        # Cleanup if worker exits
        with self._lock:
            self._is_running = False
            if self._cap is not None:
                try:
                    self._cap.release()
                except Exception as e:
                    logger.warning(f"Error releasing camera: {e}")
                self._cap = None
        logger.info("Camera capture worker thread stopped.")

    def stop(self) -> Tuple[bool, str]:
        """Stop frame capture and release camera resources safely."""
        with self._lock:
            if not self._is_running and self._cap is None:
                return True, "Camera is already stopped"

            self._stop_requested = True

        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=2.0)

        with self._lock:
            if self._cap is not None:
                try:
                    self._cap.release()
                except Exception as e:
                    logger.warning(f"Error releasing capture on stop: {e}")
                self._cap = None

            self._is_running = False
            self._latest_raw_frame = None
            self._latest_jpeg = None
            logger.info("Camera stopped and resources released.")
            return True, "Camera stopped successfully"

    def get_status(self) -> Dict[str, Any]:
        """Return comprehensive status dictionary."""
        with self._lock:
            return {
                "running": self._is_running,
                "initialized": self._cap is not None and self._cap.isOpened(),
                "device_index": self.device_index,
                "requested_resolution": f"{self.requested_width}x{self.requested_height}",
                "actual_resolution": f"{self.actual_width}x{self.actual_height}",
                "requested_fps": self.requested_fps,
                "actual_fps": self.actual_fps,
                "backend": self.backend_name,
                "frame_count": self._frame_count,
                "active_clients": self._active_clients,
                "last_frame_timestamp": self._last_frame_timestamp,
                "last_frame_age_seconds": (
                    round(time.time() - self._last_frame_timestamp, 3)
                    if self._last_frame_timestamp > 0
                    else None
                ),
                "error_message": self._error_message,
            }

    def get_snapshot(self) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Thread-safe snapshot capture.
        Returns (jpeg_bytes, None) or (None, error_str).
        """
        with self._lock:
            if not self._is_running or self._latest_jpeg is None:
                if self._error_message:
                    return None, self._error_message
                return None, "Camera is not currently capturing frames"
            return self._latest_jpeg, None

    def generate_mjpeg(self):
        """
        Generator for MJPEG multipart video stream.
        Safely increments client count and yields frames as they arrive.
        """
        with self._lock:
            self._active_clients += 1
        logger.info(f"Client connected to MJPEG stream. Active clients: {self._active_clients}")

        try:
            last_sent_timestamp = 0.0
            while True:
                with self._condition:
                    # Wait for next frame or timeout
                    has_frame = self._condition.wait(timeout=1.0)
                    if not self._is_running:
                        break
                    if not has_frame or self._latest_jpeg is None:
                        continue
                    if self._last_frame_timestamp == last_sent_timestamp:
                        continue

                    jpeg_bytes = self._latest_jpeg
                    last_sent_timestamp = self._last_frame_timestamp

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    b"Content-Length: " + str(len(jpeg_bytes)).encode("ascii") + b"\r\n\r\n"
                    + jpeg_bytes
                    + b"\r\n"
                )
        except (GeneratorExit, ConnectionResetError, BrokenPipeError):
            logger.info("Client disconnected from MJPEG stream.")
        finally:
            with self._lock:
                self._active_clients = max(0, self._active_clients - 1)
            logger.info(f"Client cleanup done. Remaining active clients: {self._active_clients}")


# Shared singleton instance
camera_manager = CameraManager()
