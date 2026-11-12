"""
AgriRover USB Webcam Microservice for Raspberry Pi 5
=====================================================
Lightweight Flask microservice providing:
- MJPEG video streaming for Next.js browser preview
- Single-frame snapshot capture for AI disease inference
- Camera lifecycle endpoints (start, stop, status, health)
- Thread-safe camera sharing to prevent multiple VideoCapture conflicts
"""

import os
import atexit
import signal
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from camera_manager import camera_manager, logger

# Load environment variables
load_dotenv()

app = Flask("AgriRoverWebcamService")

# Allowed origins for CORS (default to local Next.js instances)
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

CORS(
    app,
    resources={r"/*": {"origins": allowed_origins if allowed_origins != ["*"] else "*"}},
    supports_credentials=True,
)


@app.route("/health", methods=["GET"])
def health():
    """
    Service health check endpoint.
    Reports service uptime, camera availability, and initialization status.
    """
    status = camera_manager.get_status()
    return jsonify({
        "status": "healthy" if not status.get("error_message") else "degraded",
        "service": "AgriRover Raspberry Pi 5 USB Webcam Service",
        "version": "1.0.0",
        "camera_initialized": status["initialized"],
        "camera_running": status["running"],
        "device_index": status["device_index"],
        "error": status["error_message"],
    }), 200 if not status.get("error_message") else 503


@app.route("/camera/status", methods=["GET"])
def camera_status():
    """Detailed camera connection and streaming status."""
    return jsonify(camera_manager.get_status()), 200


@app.route("/camera/start", methods=["POST"])
def camera_start():
    """
    Initialize and start the USB webcam.
    Safe to call if camera is already running.
    """
    success, message = camera_manager.start()
    status = camera_manager.get_status()
    if success:
        return jsonify({
            "success": True,
            "message": message,
            "status": status,
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": message,
            "status": status,
        }), 500


@app.route("/camera/stop", methods=["POST"])
def camera_stop():
    """
    Safely stop capture worker and release physical webcam hardware.
    """
    success, message = camera_manager.stop()
    status = camera_manager.get_status()
    return jsonify({
        "success": success,
        "message": message,
        "status": status,
    }), 200


@app.route("/video", methods=["GET"])
def video_stream():
    """
    MJPEG multipart video stream for browser <img> or canvas element.
    Automatically starts the camera if not already active.
    """
    status = camera_manager.get_status()
    if not status["running"]:
        success, msg = camera_manager.start()
        if not success:
            return jsonify({
                "error": "Failed to auto-start camera for video stream",
                "details": msg,
            }), 503

    return Response(
        camera_manager.generate_mjpeg(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@app.route("/snapshot", methods=["GET", "POST"])
@app.route("/camera/snapshot", methods=["GET", "POST"])
def snapshot():
    """
    Capture and return the latest JPEG frame directly from the shared camera manager.
    Used by Next.js to forward high-fidelity frame to FastAPI inference service.
    """
    status = camera_manager.get_status()
    if not status["running"]:
        success, msg = camera_manager.start()
        if not success:
            return jsonify({
                "error": "Failed to auto-start camera for snapshot",
                "details": msg,
            }), 503

    jpeg_bytes, error = camera_manager.get_snapshot()
    if error or jpeg_bytes is None:
        return jsonify({
            "error": "Snapshot capture failed",
            "details": error or "No frame buffer available",
        }), 500

    return Response(
        jpeg_bytes,
        mimetype="image/jpeg",
        headers={
            "Content-Type": "image/jpeg",
            "Content-Disposition": 'inline; filename="rover_snapshot.jpg"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )


def cleanup():
    """Release camera resources on process exit."""
    logger.info("Service shutting down - releasing camera resources...")
    camera_manager.stop()


atexit.register(cleanup)


def signal_handler(signum, frame):
    cleanup()
    os._exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    host = os.getenv("CAMERA_HOST", "0.0.0.0")
    port = int(os.getenv("CAMERA_PORT", "5001"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() in ("true", "1")

    logger.info(f"Starting AgriRover Webcam Service on http://{host}:{port}")
    # threaded=True allows concurrent streaming and snapshot/status requests
    app.run(host=host, port=port, debug=debug, threaded=True)
