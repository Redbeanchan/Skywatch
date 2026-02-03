import RPi.GPIO as GPIO
import adafruit_dht
import board
from googleapiclient.discovery import build
from google.oauth2 import service_account
from picamera2 import Picamera2
import requests
import random
import time
import os
import cv2
import numpy as np
from datetime import datetime
from PIL import Image
import grovepi

RAIN_SENSOR_PORT = 0  # Rain sensor on analog port A0
# Connect the Grove 4 Digit Display to digital port D5
# CLK,DIO,VCC,GND
display = 4
grovepi.pinMode(display, "OUTPUT")

# Connect the Grove LED to digital port D3
led = 3
grovepi.pinMode(led, "OUTPUT")

# Google Drive API setup
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
PARENT_FOLDER_ID = "FOLDERIDGOESHERE"  # Replace with your folder ID

# Google Sheets App Script URL
APP_SCRIPT_URL = 'APIKEYGOESHERE'  # Replace with your Google Apps Script URL

# Function to authenticate Google Drive API
def authenticate():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds


edge_count = 0
lbp_mean = 0
lbp_stddev = 0
lbp_entropy = 0
hue_mean = 0
saturation_mean = 0
value_mean = 0
cloud_percentage = 0

# Initialize DHT sensor
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
dht_device = adafruit_dht.DHT22(board.D22)  # GPIO 22

# Function to reset GPIO pins
def reset_gpio():
    print("Resetting GPIO pins...")
    GPIO.cleanup()          # Reset all GPIO pins
    print("GPIO cleanup complete.")
    
def countdown_timer(minutes):
    """
    Countdown timer that starts from the given minutes and counts down to 00:00.
    :param minutes: Number of minutes to count down from.
    """
    total_seconds = minutes * 60

    grovepi.fourDigit_init(display)

    # Turn on the LED to indicate the countdown has started
    grovepi.digitalWrite(led, 1)

    while total_seconds >= 0:
        try:
            # Calculate minutes and seconds
            mins = total_seconds // 60
            secs = total_seconds % 60

            # Display the countdown in MMSS format
            time_value = mins * 100 + secs
            grovepi.fourDigit_number(display, time_value, 1)

            # Wait for 1 second
            time.sleep(1)

            # Decrement the total seconds
            total_seconds -= 1
        except KeyboardInterrupt:
            grovepi.fourDigit_off(display)
            grovepi.digitalWrite(led, 0)  # Turn off the LED
            break
        except IOError:
            print("Error while communicating with the display.")
            grovepi.fourDigit_off(display)
            grovepi.digitalWrite(led, 0)  # Turn off the LED
            break

    # Turn off the display and LED after countdown is complete
    grovepi.fourDigit_off(display)
    grovepi.digitalWrite(led, 0)
    time.sleep(1)
    grovepi.digitalWrite(led, 1)
    time.sleep(1)
    grovepi.digitalWrite(led, 0)
    time.sleep(1)
    grovepi.digitalWrite(led, 1)

# Function to read temperature and humidity
def read_temp_humidity():
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        if temperature is not None and humidity is not None:
            temperature = round(temperature, 2)
            humidity = round(humidity, 2)
            return temperature, humidity
        else:
            print("Failed to read from DHT sensor.")
            return None, None
    except RuntimeError as e:
        print(f"Error reading DHT sensor: {e}")
        return None, None

# Function to read rain sensor data
def read_rain():
    try:
        rain_value = grovepi.analogRead(RAIN_SENSOR_PORT)
        return rain_value
    except IOError as e:
        print(f"Error reading rain sensor: {e}")
        return None

# Function to capture an image using Picamera2
def capture_image(file_path):
    picam2 = Picamera2()
    config = picam2.create_still_configuration()
    picam2.configure(config)
    picam2.start()
    time.sleep(2)  # Allow the camera to adjust
    picam2.capture_file(file_path)
    picam2.stop()
    picam2.close()
    print(f"Image captured and saved as {file_path}")

# Function to resize the image to 256x256 and rename it
def resize_image(original_path):
    img = Image.open(original_path)
    img = img.resize((256, 256), Image.Resampling.LANCZOS)
    new_path = original_path.replace(".jpg", "_r1.jpg")
    img.save(new_path)
    os.remove(original_path)
    print(f"Image resized to 256x256 and saved as {new_path}")
    return new_path

# Function to calculate Local Binary Patterns (LBP)
def calculate_lbp(image):
    lbp = np.zeros_like(image, dtype=np.uint8)
    for i in range(1, image.shape[0] - 1):
        for j in range(1, image.shape[1] - 1):
            center = image[i, j]
            binary = ''.join(['1' if image[i + x, j + y] > center else '0' 
                              for x, y in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]])
            lbp[i, j] = int(binary, 2)
    return lbp

# Function to analyze image
def analyze_image(image_path):
    global edge_count, lbp_mean, lbp_stddev, lbp_entropy, hue_mean, saturation_mean, value_mean, cloud_percentage
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Image not found. Check the path!")
        return None

    resized_image = cv2.resize(image, None, fx=0.4, fy=0.4)
    gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray_image, 100, 200)
    edge_count = np.sum(edges > 0)
    lbp = calculate_lbp(gray_image)
    lbp_mean = np.mean(lbp)
    lbp_stddev = np.std(lbp)
    lbp_entropy = -np.sum((lbp / 255) * np.log2((lbp / 255) + 1e-10))
    hsv_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2HSV)
    hue_mean = np.mean(hsv_image[:, :, 0])
    saturation_mean = np.mean(hsv_image[:, :, 1])
    value_mean = np.mean(hsv_image[:, :, 2])
    cloud_percentage = np.sum(gray_image > 200) / gray_image.size * 100

    print("Image Analysis Results:")
    print(f"Edge Count: {edge_count}")
    print(f"LBP Mean: {lbp_mean}")
    print(f"LBP StdDev: {lbp_stddev}")
    print(f"LBP Entropy: {lbp_entropy}")
    print(f"Hue Mean: {hue_mean}")
    print(f"Saturation Mean: {saturation_mean}")
    print(f"Value Mean: {value_mean}")
    print(f"Cloud Percentage: {cloud_percentage}%")

    return {
        "Edge Count": edge_count,
        "LBP_Mean": lbp_mean,
        "LBP_StdDev": lbp_stddev,
        "LBP_Entropy": lbp_entropy,
        "Hue_Mean": hue_mean,
        "Saturation_Mean": saturation_mean,
        "Value_Mean": value_mean,
        "Cloud_Percentage": cloud_percentage
    }

# Function to upload the resized image to Google Drive
def upload_photo(file_path):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [PARENT_FOLDER_ID]
    }

    with open(file_path, 'rb') as file:
        service.files().create(
            body=file_metadata,
            media_body=file_path
        ).execute()

    print(f"Image '{os.path.basename(file_path)}' uploaded to Google Drive.")

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Local file '{file_path}' deleted.")

# Function to send sensor data to Google Sheets
def send_data_to_sheets(image_name,edge_count, lbp_mean, lbp_stddev, lbp_entropy, hue_mean, saturation_mean, value_mean, cloud_percentage):
    
    TEMP, HUMD = read_temp_humidity()
    rain = read_rain()



    # Step 4: Send data to Google Sheets via HTTPS request
    full_url = f"{APP_SCRIPT_URL}?TEMP={TEMP}&HUM={HUMD}&EDGE={edge_count}&LBPMEAN={lbp_mean}&LBPSTDDEV={lbp_stddev}&LBPSTDENT={lbp_entropy}&HUE={hue_mean}&SAT={saturation_mean}&VAL={value_mean}&CLOUD={cloud_percentage}&RAIN={rain}&ID={image_name}"
    response = requests.get(full_url)

    if response.status_code == 200:
        print(full_url)
        print(response)
        print("Data sent successfully to Google Sheets.")
    else:
        print(f"Failed to send data: {response.status_code} - {response.text}")
# Main function to run all processes
def main():
    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            image_path = f"{timestamp}.jpg"
            capture_image(image_path)
            resized_image_path = resize_image(image_path)
            analysis_results = analyze_image(resized_image_path)
            upload_photo(resized_image_path)

            if analysis_results:
                send_data_to_sheets(
                    os.path.basename(resized_image_path),
                    analysis_results["Edge Count"],
                    analysis_results["LBP_Mean"],
                    analysis_results["LBP_StdDev"],
                    analysis_results["LBP_Entropy"],
                    analysis_results["Hue_Mean"],
                    analysis_results["Saturation_Mean"],
                    analysis_results["Value_Mean"],
                    analysis_results["Cloud_Percentage"]
                )
            print("Waiting for 5 minutes...")
            countdown_timer(5)
    except KeyboardInterrupt:
        grovepi.fourDigit_off(display)
        grovepi.digitalWrite(led, 0)  # Turn off the LED
        print("Exiting program.")
    finally:
        dht_device.exit()
        reset_gpio()

# Run the script
if __name__ == "__main__":
    main()
