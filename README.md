# SkyWatch

**EGT211 IoT Applications — Project #4 (IoT-Based Weather Station)**

SkyWatch is a compact IoT weather station that collects **local, real-time** weather data using a Raspberry Pi, performs **on-device image + sensor processing**, and publishes readings to cloud dashboards (Google Sheets, Looker Studio, Blynk).

## Team
- Samuel Kosasih
- Marcus Teo
- Alexander Chan

---

## Contents
- [Overview](#overview)
- [What SkyWatch Does](#what-skywatch-does)
- [System Architecture](#system-architecture)
- [Data Captured](#data-captured)
- [Hardware](#hardware)
- [Software](#software)
- [Repository Contents](#repository-contents)
- [Setup](#setup)
  - [1) Raspberry Pi](#1-raspberry-pi)
  - [2) Google Drive (Service Account)](#2-google-drive-service-account)
  - [3) Google Sheets (Apps Script Endpoint)](#3-google-sheets-apps-script-endpoint)
  - [4) Run on Raspberry Pi](#4-run-on-raspberry-pi)
  - [5) Web Dashboard](#5-web-dashboard)
  - [6) Arduino (Optional)](#6-arduino-optional)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)
- [Future Work](#future-work)
- [License](#license)

---

## Overview
Most public weather services aggregate data from large-scale meteorological stations, which can be too broad for a specific neighborhood. SkyWatch aims to provide **personalized, live conditions** with a small, low-cost, open-source station that can be deployed at home.

---

## What SkyWatch Does
- Collects temperature + humidity (DHT-series sensor) and precipitation signal (raindrop/moisture sensor).
- Captures periodic sky images using a Raspberry Pi camera.
- Extracts cloud-related features on-device (no external compute needed).
- Uploads to a cloud “database” (Google Sheets via HTTPS).
- Visualizes data via:
  - Google Sheets (embedded)
  - Looker Studio (embedded)
  - Blynk dashboard link
  - A simple web dashboard page (`index.html`)

Sampling is designed around a **5-minute cycle**.

---

## System Architecture
```mermaid
flowchart LR
  A[Sensors + Pi Camera] --> B[Raspberry Pi]
  B --> C[Image feature extraction<br/>(edges, LBP, HSV, cloud %)]
  B --> D[HTTPS request<br/>to Apps Script]
  D --> E[Google Sheets<br/>(data store)]
  B --> F[Google Drive<br/>(sky images)]
  E --> G[Looker Studio dashboard]
  E --> H[Blynk dashboard]
  E --> I[Web dashboard (embed)]
```

---

## Data Captured

### Sensor data
- `TEMP`: Temperature (°C)
- `HUM`: Humidity (%)
- `RAIN`: Analog rain/moisture reading (raw value)

### Image-derived features (from sky photo)
SkyWatch computes lightweight features to quantify cloud conditions:
- `EDGE`: Edge count (Canny)
- `LBPMEAN`, `LBPSTDDEV`, `LBPSTDENT`: Local Binary Pattern stats (mean, stddev, entropy)
- `HUE`, `SAT`, `VAL`: HSV channel means
- `CLOUD`: Cloud percentage estimate (simple brightness threshold)
- `ID`: Image filename/timestamp

> Note: These features are logged for visualization and as groundwork for more reliable prediction models.

---

## Hardware
The exact parts may vary by availability, but the implementation is built around:

**Core**
- Raspberry Pi (tested with Raspberry Pi 4)
- Raspberry Pi Camera (Picamera2)

**Sensors**
- DHT-series temperature/humidity sensor  
  - Slides reference DHT11; the provided Raspberry Pi script uses **DHT22** (both are supported conceptually).
- Raindrop / moisture sensor (analog input)

**Indicators**
- Grove 4-digit display (countdown timer until next sample)
- LED indicator (collection/countdown status)

**Optional**
- Arduino WiFi board using `WiFiS3` + button trigger for “instant” collection (see slides).  
  A minimal HTTPS-request sketch is included in this repo.

---

## Software

### Raspberry Pi
- Python 3
- `picamera2`
- `opencv-python` / `cv2`
- `numpy`, `Pillow`
- `requests`
- `google-api-python-client` + `google-auth` (Google Drive service account upload)
- `adafruit-circuitpython-dht`, `RPi.GPIO`
- `grovepi` (Grove sensors + 4-digit display)

### Cloud & Dashboards
- Google Apps Script (HTTP endpoint)
- Google Sheets (data store)
- Looker Studio (dashboard)
- Blynk (dashboard)
- Simple web dashboard (HTML/CSS/JS)

---

## Repository Contents
This README was generated from the uploaded project materials. The key files are:

- `iota_raspicode.py` — Raspberry Pi main script (sensors + camera + upload)
- `iota_arduinocode.ino` — Arduino HTTPS request sketch (optional)
- `EGT211 Samuel Marcus Alex IoT Slides and App/Slides Samuel Marcus Alex AI2302 T2.pdf` — project slides
- `EGT211 Samuel Marcus Alex IoT Slides and App/Application Samuel Marcus Alex/` — web dashboard site:
  - `index.html`, `style.css`, `script.js`
  - `App.png`, `blynk-logo.png`, `google-logo.png`

Recommended repo layout when you publish to GitHub:
```
skywatch/
  raspberry-pi/
    iota_raspicode.py
  arduino/
    iota_arduinocode.ino
    arduino_secrets.h        # do not commit
  dashboard/
    index.html
    style.css
    script.js
    App.png
    blynk-logo.png
    google-logo.png
  slides/
    skywatch-slides.pdf
  README.md
  .gitignore
```

---

## Setup

### 1) Raspberry Pi
**Prerequisites**
- Raspberry Pi OS
- Camera enabled (Picamera2)
- Internet access

**Install system packages (example)**
```bash
sudo apt update
sudo apt install -y python3-pip python3-opencv
```

**Install Python packages**
```bash
python3 -m pip install --upgrade pip
python3 -m pip install   requests numpy pillow   google-api-python-client google-auth google-auth-httplib2   adafruit-circuitpython-dht RPi.GPIO
```

Picamera2 is typically installed via Raspberry Pi OS packages:
```bash
sudo apt install -y python3-picamera2
```

If you are using GrovePi, ensure the `grovepi` library is installed per your hardware vendor instructions.

---

### 2) Google Drive (Service Account)
SkyWatch uploads sky photos to a Google Drive folder using a service account.

1. Create a Google Cloud project
2. Enable **Google Drive API**
3. Create a **Service Account**
4. Download the JSON key file and place it next to the Pi script as:
   - `service_account.json` (do **not** commit this file)
5. Create a Drive folder and copy its Folder ID
6. Share that folder with the service account email (Editor access)

Update in `iota_raspicode.py`:
```py
SERVICE_ACCOUNT_FILE = "service_account.json"
PARENT_FOLDER_ID = "FOLDERIDGOESHERE"
```

---

### 3) Google Sheets (Apps Script Endpoint)
The Raspberry Pi sends readings to Google Sheets using an Apps Script HTTP endpoint.

Update in `iota_raspicode.py`:
```py
APP_SCRIPT_URL = "APIKEYGOESHERE"
```

The script sends the following query parameters:
`TEMP`, `HUM`, `EDGE`, `LBPMEAN`, `LBPSTDDEV`, `LBPSTDENT`, `HUE`, `SAT`, `VAL`, `CLOUD`, `RAIN`, `ID`

Your Apps Script should parse these and append a row to your Google Sheet.

---

### 4) Run on Raspberry Pi
From the folder containing `iota_raspicode.py`:

```bash
python3 iota_raspicode.py
```

The loop will:
1. Capture an image
2. Resize to 256×256
3. Extract features
4. Upload image to Google Drive
5. Send a row to Google Sheets
6. Start a 5-minute countdown (4-digit display + LED)

Stop with `Ctrl + C`.

---

### 5) Web Dashboard
The provided dashboard is a static website (HTML/CSS/JS).

To run locally:
```bash
cd dashboard
python3 -m http.server 8000
```

Open:
- `http://localhost:8000`

If you want to publish via GitHub Pages, place the dashboard files in your Pages directory (commonly `/docs` or repo root) and enable Pages in GitHub settings.

**Important:** The current `index.html` contains embedded links to:
- a published Google Sheet
- a Looker Studio report
- a Blynk dashboard URL

When you fork/reuse this project, replace these embeds with your own links.

---

### 6) Arduino (Optional)
`iota_arduinocode.ino` connects to WiFi using `WiFiS3` and makes an HTTPS request to `script.google.com`.

You must create `arduino_secrets.h`:
```cpp
#define SECRET_SSID "YOUR_WIFI_NAME"
#define SECRET_PASS "YOUR_WIFI_PASSWORD"
```

Then replace the placeholder path in:
```cpp
client.println("GET <APIKEYGOESHERE> HTTP/1.1");
```

---

## Troubleshooting

**DHT sensor read failures**
- DHT sensors can be noisy; ensure solid wiring and correct pull-up resistor.
- Add retries and spacing between reads if needed.

**Camera errors**
- Confirm camera is enabled and `python3-picamera2` is installed.
- Test a minimal capture script first.

**Drive upload fails**
- Ensure the Drive folder is shared with the service account email.
- Verify `PARENT_FOLDER_ID` and `service_account.json` are correct.

**Google Sheets not updating**
- Confirm Apps Script is deployed as a Web App and accessible.
- Confirm parameter names match what the script sends.

---

## Security Notes
Do not commit secrets to GitHub:
- `service_account.json`
- `arduino_secrets.h`
- Any private Apps Script URLs if you treat them as sensitive

Add them to `.gitignore`.

---

## Future Work
- Improve cloud masking (e.g., K-means segmentation + sky-only mask) as shown in slides.
- Build a stronger rain prediction model from the collected dataset.
- Add a barometer (mentioned in the project brief) for pressure-based trend detection.
- Convert the Raspberry Pi script into a `systemd` service for always-on deployment.

---

## License
This project was built for an academic module (EGT211).  
Before making the repository public, choose an explicit license (e.g., MIT / Apache-2.0).
