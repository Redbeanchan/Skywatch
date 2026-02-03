# SkyWatch

**Project #4 — IoT Weather Station**

SkyWatch is a compact **IoT weather station** built around a Raspberry Pi. It collects **live local weather readings**, captures sky images, extracts lightweight cloud features on-device, and publishes the data to cloud dashboards (Google Sheets / Looker Studio / Blynk) for easy viewing.

## Team
- Samuel Kosasih
- Marcus Teo
- Alexander Chan

---

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Data Schema](#data-schema)
- [Hardware](#hardware)
- [Software](#software)
- [Repo Layout](#repo-layout)
- [Setup](#setup)
  - [Raspberry Pi](#raspberry-pi)
  - [Google Drive Service Account](#google-drive-service-account)
  - [Google Sheets Apps Script Endpoint](#google-sheets-apps-script-endpoint)
  - [Run SkyWatch](#run-skywatch)
  - [Web Dashboard](#web-dashboard)
  - [Arduino Optional](#arduino-optional)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Overview
Most public weather apps rely on large-scale meteorological stations and focus heavily on forecasts. SkyWatch was designed to provide **personalized, real-time weather conditions** from your own deployment location, with transparent data collection and simple visualization.

---

## Key Features
- Live sensor readings (temperature, humidity, rain signal)
- Periodic sky image capture (Raspberry Pi Camera)
- On-device image processing for cloud-related signals (no external compute required)
- Automatic logging to Google Sheets (via Google Apps Script HTTP endpoint)
- Optional image uploads to Google Drive
- Web dashboard that embeds:
  - Published Google Sheet
  - Looker Studio report
  - Blynk dashboard link

---

## Architecture
(ASCII diagram for compatibility across Markdown renderers)

```
[Sensors + Pi Camera]
        |
        v
 [Raspberry Pi]
   |        |
   |        +--> Upload sky images --> [Google Drive Folder]
   |
   +--> Extract features (edges/LBP/HSV/cloud %)
   |
   +--> HTTPS request (Apps Script URL)
                 |
                 v
           [Google Sheets]
                 |
        +--------+--------+
        |                 |
        v                 v
 [Looker Studio]       [Web Dashboard]
 (embedded)            (embeds Sheets/Looker/Blynk)
```

---

## Data Schema
SkyWatch logs both sensor values and image-derived features. The Raspberry Pi script sends these as query parameters to Apps Script:

### Sensor values
- `TEMP` — temperature (°C)
- `HUM` — humidity (%)
- `RAIN` — rain sensor analog value (raw reading)

### Image-derived features (from the captured sky photo)
- `EDGE` — Canny edge count
- `LBPMEAN` — Local Binary Pattern mean
- `LBPSTDDEV` — Local Binary Pattern standard deviation
- `LBPSTDENT` — Local Binary Pattern entropy
- `HUE` — HSV hue mean
- `SAT` — HSV saturation mean
- `VAL` — HSV value mean
- `CLOUD` — estimated cloud percentage (simple brightness threshold heuristic)
- `ID` — image filename / timestamp key

---

## Hardware
Built around common parts. Your exact models can vary by availability.

**Core**
- Raspberry Pi (tested with Raspberry Pi 4)
- Raspberry Pi Camera (Picamera2)

**Sensors**
- DHT temperature/humidity sensor  
  - Slides reference DHT11; the Raspberry Pi script uses **DHT22 on GPIO22**.
- Rain / moisture sensor (Grove analog input)

**Indicators**
- Grove 4-digit display (countdown timer)
- Grove LED (status)

**Optional**
- Arduino WiFi board sketch included for HTTPS request testing / trigger workflow

---

## Software
### Raspberry Pi (Python)
- `picamera2`
- `opencv-python` (`cv2`)
- `numpy`, `Pillow`
- `requests`
- `google-api-python-client`, `google-auth` (Drive upload via service account)
- `adafruit-circuitpython-dht`, `RPi.GPIO`
- `grovepi` (Grove ports + 4-digit display)

### Dashboards
- Google Apps Script (HTTP endpoint)
- Google Sheets (data store)
- Looker Studio (visualization)
- Blynk (optional dashboard)
- Static web dashboard (`index.html`, `style.css`, `script.js`)

---

## Repo Layout
Recommended structure when publishing to GitHub:

```
skywatch/
  raspberry-pi/
    iota_raspicode.py
    service_account.json        # DO NOT COMMIT
  arduino/
    iota_arduinocode.ino
    arduino_secrets.h           # DO NOT COMMIT
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

### Raspberry Pi
1) Update packages
```bash
sudo apt update
sudo apt install -y python3-pip python3-opencv python3-picamera2
```

2) Install Python dependencies
```bash
python3 -m pip install --upgrade pip
python3 -m pip install   requests numpy pillow   google-api-python-client google-auth google-auth-httplib2   adafruit-circuitpython-dht RPi.GPIO
```

> If you are using GrovePi/Grove expansion hardware, install `grovepi` according to your board vendor instructions.

---

### Google Drive Service Account
SkyWatch uploads sky photos to a Google Drive folder using a service account.

1. Create a Google Cloud project  
2. Enable **Google Drive API**  
3. Create a **Service Account**  
4. Download the JSON key file and save as:
   - `raspberry-pi/service_account.json`  
5. Create a Drive folder and copy its folder ID  
6. Share that folder with the service account email (Editor access)

Update in `iota_raspicode.py`:
```py
SERVICE_ACCOUNT_FILE = "service_account.json"
PARENT_FOLDER_ID = "FOLDERIDGOESHERE"
```

---

### Google Sheets Apps Script Endpoint
The Raspberry Pi sends readings to Sheets through Apps Script.

Update in `iota_raspicode.py`:
```py
APP_SCRIPT_URL = "APIKEYGOESHERE"
```

The script constructs a URL like:
```
{APP_SCRIPT_URL}?TEMP=...&HUM=...&EDGE=...&...&ID=...
```

Your Apps Script should parse these parameters and append them as a new row.

---

### Run SkyWatch
From the Raspberry Pi folder:
```bash
cd raspberry-pi
python3 iota_raspicode.py
```

Each cycle:
1. Capture image
2. Resize to 256×256
3. Extract features
4. Upload image to Google Drive
5. Send a row to Google Sheets
6. Start a 5-minute countdown (4-digit display + LED)

Stop with `Ctrl + C`.

---

### Web Dashboard
A simple static website is included (HTML/CSS/JS). It embeds:
- a published Google Sheet
- a Looker Studio report
- a Blynk dashboard link

Run locally:
```bash
cd dashboard
python3 -m http.server 8000
```

Open:
- `http://localhost:8000`

When publishing, replace the embedded URLs in `dashboard/index.html` with your own.

---

### Arduino Optional
The Arduino sketch (`iota_arduinocode.ino`) demonstrates making an HTTPS request to `script.google.com` using `WiFiS3`.

Create `arduino_secrets.h`:
```cpp
#define SECRET_SSID "YOUR_WIFI_NAME"
#define SECRET_PASS "YOUR_WIFI_PASSWORD"
```

Then replace the Apps Script path line in the sketch:
```cpp
client.println("GET <APIKEYGOESHERE> HTTP/1.1");
```

---

## Troubleshooting
**DHT sensor read failures**
- DHT sensors can be noisy—check wiring and add retries if needed.

**Camera errors**
- Confirm camera is enabled and `python3-picamera2` is installed.
- Test a minimal capture script first.

**Drive upload fails**
- Confirm the Drive folder is shared with the service account email.
- Check `PARENT_FOLDER_ID` and that `service_account.json` exists.

**Sheets not updating**
- Confirm Apps Script is deployed as a Web App and is accessible.
- Ensure parameter names match what the Pi script sends.

---

## Security Notes
Do **not** commit secrets to GitHub:
- `raspberry-pi/service_account.json`
- `arduino/arduino_secrets.h`
- any private Apps Script URLs if you treat them as sensitive

Add them to `.gitignore`, for example:
```gitignore
# Secrets
**/service_account.json
**/arduino_secrets.h
.env
```

---

## Future Improvements
- Better cloud masking (segmentation) for more stable cloud-percentage estimation
- Add a barometer/pressure sensor for trend detection
- Train a lightweight model using the logged dataset for stronger rain prediction
- Run the Raspberry Pi script as a background service (`systemd`) for always-on deployment

---

## License
This project was built for an academic module. Add an explicit license (MIT / Apache-2.0) before making the repository public.
