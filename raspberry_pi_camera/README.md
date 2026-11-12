# AgriRover USB Webcam Service — Raspberry Pi 5 Guide

This microservice provides high-performance, low-latency USB webcam video streaming (MJPEG) and single-frame snapshot capture on **Raspberry Pi 5** running **Raspberry Pi OS 64-bit (Debian Bookworm)**.

---

## 1. System Requirements & Hardware Prerequisites

- **Board**: Raspberry Pi 5 (4GB or 8GB recommended)
- **OS**: Raspberry Pi OS 64-bit (Debian Bookworm) with desktop or lite
- **Camera**: Standard USB 2.0 / USB 3.0 UVC Web Camera (e.g., Logitech C270, C920, or generic USB webcam) plugged directly into any USB 3.0 (blue) or USB 2.0 port of the Pi 5.
- **Power**: Official 27W USB-C Raspberry Pi 5 Power Supply to guarantee stable 5V / 5A power under camera load.

---

## 2. Step-by-Step Installation on Raspberry Pi OS 64-bit

### Step 1: Update System Packages
```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Python, V4L2 Utilities, and OpenCV System Dependencies
```bash
sudo apt install -y python3 python3-pip python3-venv v4l-utils libgl1 libglib2.0-0 libjpeg-dev zlib1g-dev
```

### Step 3: Grant User Camera Permissions
Ensure your user (`pi` or your configured username) belongs to the `video` group:
```bash
sudo usermod -a -G video $USER
```
*(Log out and log back in or reboot for group changes to take effect).*

### Step 4: Verify USB Webcam Detection
Check if the Linux kernel recognizes your USB camera:
```bash
# 1. Check USB devices
lsusb

# 2. Check video device nodes
ls -l /dev/video*

# 3. Query Video4Linux2 capabilities and device indices
v4l2-ctl --list-devices
```
Example output:
```text
USB 2.0 Camera: HD 720P Webcam (usb-0000:01:00.0-1.1):
	/dev/video0
	/dev/video1
	/dev/media0
```
*(Note: USB webcams typically provide multiple `/dev/video*` nodes; the capture node is usually `/dev/video0`).*

Query supported formats and resolutions:
```bash
v4l2-ctl -d /dev/video0 --list-formats-ext
```

---

## 3. Python Environment & Service Setup

### Step 1: Clone or Copy the Repository
Navigate to the camera service directory on your Raspberry Pi:
```bash
cd ~/AgriRover/raspberry_pi_camera
```

### Step 2: Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Hardware Self-Test Before Running Server
Run the hardware diagnostic script to verify camera access and frame capture:
```bash
python test_camera.py --index 0 --width 640 --height 480
```
If successful, this will report negotiated resolution and save `test_frame.jpg`.

---

## 4. Configuration & Environment Variables

Copy the example configuration:
```bash
cp .env.example .env
```

Edit `.env` according to your network setup:
```ini
# Network binding
CAMERA_HOST=0.0.0.0
CAMERA_PORT=5001

# Camera Hardware
CAMERA_INDEX=0
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
CAMERA_FPS=15
CAMERA_JPEG_QUALITY=80

# Allowed Frontend Origins (allow your Next.js frontend IP or domain)
ALLOWED_ORIGINS=http://localhost:3000,http://192.168.1.50:3000
```

---

## 5. Running the Camera Service

### Manual Start:
```bash
source venv/bin/activate
python app.py
```

The service will start on `http://0.0.0.0:5001`.

---

## 6. Verifying API Endpoints

Test each endpoint from the Pi terminal or another computer on the same network:

### 1. Health Check
```bash
curl -i http://localhost:5001/health
```
Response:
```json
{
  "status": "healthy",
  "service": "AgriRover Raspberry Pi 5 USB Webcam Service",
  "version": "1.0.0",
  "camera_initialized": true,
  "camera_running": true,
  "device_index": 0,
  "error": null
}
```

### 2. Camera Status
```bash
curl -i http://localhost:5001/camera/status
```
Response:
```json
{
  "running": true,
  "initialized": true,
  "device_index": 0,
  "actual_resolution": "640x480",
  "actual_fps": 15.0,
  "backend": "V4L2",
  "active_clients": 0,
  "last_frame_age_seconds": 0.042
}
```

### 3. Stop Camera
```bash
curl -i -X POST http://localhost:5001/camera/stop
```

### 4. Start Camera
```bash
curl -i -X POST http://localhost:5001/camera/start
```

### 5. Capture Snapshot (JPEG)
```bash
curl -o snapshot.jpg http://localhost:5001/snapshot
file snapshot.jpg
```

### 6. Live MJPEG Stream
Open in any browser:
```text
http://<RASPBERRY_PI_IP>:5001/video
```

---

## 7. Auto-Start on Boot via Systemd

To keep the camera service running automatically on boot and restart upon unexpected failures:

### Step 1: Create Systemd Unit File
```bash
sudo nano /etc/systemd/system/agrirover-camera.service
```

Paste the following configuration (replace `pi` with your actual username and path):
```ini
[Unit]
Description=AgriRover Raspberry Pi 5 USB Webcam Microservice
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/AgriRover/raspberry_pi_camera
ExecStart=/home/pi/AgriRover/raspberry_pi_camera/venv/bin/python app.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

### Step 2: Enable and Start the Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable agrirover-camera
sudo systemctl start agrirover-camera
```

### Step 3: Check Status & Logs
```bash
sudo systemctl status agrirover-camera
journalctl -u agrirover-camera -f
```

---

## 8. Raspberry Pi Troubleshooting & Edge Cases

| Issue | Root Cause | Solution |
|---|---|---|
| `Could not open camera at index 0` | Device assigned to `/dev/video1` or `/dev/video2` | Check with `v4l2-ctl --list-devices` and update `CAMERA_INDEX` in `.env`. |
| `Permission denied` opening `/dev/video*` | Missing user video permissions | Run `sudo usermod -a -G video $USER` and reboot. |
| `Device or resource busy` | Another process (e.g., OpenCV, Motion, Chromium) is holding the webcam | Find locking process: `fuser -v /dev/video0` and terminate it. |
| Stream freezes or drops frames | Underpowered USB port or insufficient current | Use the official 27W power adapter and avoid high-power USB hubs. |
| Mixed content blocked in browser | Frontend loaded over `https://` accessing `http://` Pi stream | Set up an SSL reverse proxy (Nginx or Caddy) or run frontend on local network HTTP. |
