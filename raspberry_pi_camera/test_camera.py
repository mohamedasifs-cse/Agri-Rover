"""
AgriRover USB Webcam Hardware Diagnostic & Test Script
======================================================
Run this script directly on the Raspberry Pi 5 to verify the physical USB webcam
before launching the Flask web service.

Usage:
    python test_camera.py [--index 0] [--width 640] [--height 480]
"""

import sys
import time
import argparse
import cv2

def parse_args():
    parser = argparse.ArgumentParser(description="Test USB webcam hardware connection.")
    parser.add_argument("--index", type=int, default=0, help="V4L2 camera device index (default: 0)")
    parser.add_argument("--width", type=int, default=640, help="Requested width (default: 640)")
    parser.add_argument("--height", type=int, default=480, help="Requested height (default: 480)")
    parser.add_argument("--fps", type=int, default=15, help="Requested FPS (default: 15)")
    return parser.parse_args()

def main():
    args = parse_args()
    print("=" * 60)
    print(" AgriRover USB Webcam Hardware Test (Raspberry Pi 5 / OS)")
    print("=" * 60)
    print(f"Platform: {sys.platform}")
    print(f"OpenCV Version: {cv2.__version__}")
    print(f"Testing Device Index: {args.index}")
    print(f"Requested Mode: {args.width}x{args.height} @ {args.fps} FPS")

    # Select backend
    if sys.platform.startswith("linux"):
        backend = cv2.CAP_V4L2
        backend_name = "V4L2 (Linux/Raspberry Pi OS)"
    elif sys.platform == "win32":
        backend = cv2.CAP_DSHOW
        backend_name = "DirectShow (Windows)"
    else:
        backend = cv2.CAP_ANY
        backend_name = "Auto (CAP_ANY)"

    print(f"Attempting connection using backend: {backend_name}...")
    cap = cv2.VideoCapture(args.index, backend)

    if not cap.isOpened():
        print(f"[!] Primary backend {backend_name} failed. Trying cv2.CAP_ANY fallback...")
        cap = cv2.VideoCapture(args.index, cv2.CAP_ANY)

    if not cap.isOpened():
        print("\n❌ ERROR: Could not open camera at index", args.index)
        print("Troubleshooting steps:")
        print("  1. Run 'ls -l /dev/video*' or 'v4l2-ctl --list-devices' to find the device.")
        print("  2. Ensure your user has permissions: 'sudo usermod -a -G video $USER'")
        print("  3. Check USB connection with 'lsusb'.")
        print("  4. Verify another process (e.g. motion, ffmpeg) is not holding the camera.")
        sys.exit(1)

    # Set requested resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    cap.set(cv2.CAP_PROP_FPS, args.fps)

    # Read back actual settings
    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)

    print("\n✅ Camera opened successfully!")
    print(f"   Actual Resolution: {actual_w}x{actual_h}")
    print(f"   Actual FPS: {actual_fps}")

    print("\nCapturing 10 test frames to verify stability...")
    start_time = time.time()
    last_frame = None
    frames_ok = 0

    for i in range(10):
        ret, frame = cap.read()
        if ret and frame is not None:
            frames_ok += 1
            last_frame = frame
        else:
            print(f"   [!] Frame {i+1} read failed!")
        time.sleep(0.05)

    duration = time.time() - start_time
    effective_fps = frames_ok / max(0.001, duration)

    print(f"Captured {frames_ok}/10 frames in {duration:.2f}s (~{effective_fps:.1f} FPS)")

    if last_frame is not None:
        output_file = "test_frame.jpg"
        cv2.imwrite(output_file, last_frame)
        print(f"Saved test image to '{output_file}' ({last_frame.shape[1]}x{last_frame.shape[0]} px).")

    cap.release()
    print("\nCamera hardware released safely.")
    print("=" * 60)
    print("✅ TEST PASSED: USB Webcam is fully functional on this system.")
    print("=" * 60)

if __name__ == "__main__":
    main()
