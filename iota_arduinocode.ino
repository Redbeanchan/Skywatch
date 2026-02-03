#include "WiFiS3.h"
#include "WiFiSSLClient.h"
#include "IPAddress.h"

#include "arduino_secrets.h"

///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;        // your network password (use for WPA, or use as key for WEP)

int status = WL_IDLE_STATUS;
char server[] = "script.google.com";    // name address for Google (using DNS)

WiFiSSLClient client;

void setup() {
  Serial.begin(115200);
  while (!Serial);

  Serial.println("[DEBUG] Initializing WiFi module...");
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("[ERROR] WiFi module failed!");
    while (true);
  }

  while (status != WL_CONNECTED) {
    Serial.print("[DEBUG] Connecting to SSID: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
    delay(10000);
  }

  printWifiStatus();

  Serial.println("\n[DEBUG] Starting connection to Google Apps Script...");

  if (client.connect(server, 443)) {
    Serial.println("[DEBUG] Connected to server");

    client.println("GET <APIKEYGOESHERE> HTTP/1.1");
    client.println("Host: script.google.com");
    client.println("User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)");
    client.println("Connection: close");
    client.println();
  } else {
    Serial.println("[ERROR] Connection failed");
    return;
  }

  delay(500);
  Serial.println("[DEBUG] Checking for redirection...");
  int httpCode = getHTTPResponseCode();
  Serial.print("[DEBUG] HTTP Response Code: ");
  Serial.println(httpCode);
  String redirectURL = getRedirectURL();

  if (redirectURL.length() > 0) {
    Serial.print("[DEBUG] Redirecting to: ");
    Serial.println(redirectURL);

    String newHost = redirectURL.substring(8); // Remove "https://"
    int slashIndex = newHost.indexOf('/');
    String newPath = newHost.substring(slashIndex);
    newHost = newHost.substring(0, slashIndex);

    Serial.print("[DEBUG] New Host: ");
    Serial.println(newHost);
    Serial.print("[DEBUG] New Path: ");
    Serial.println(newPath);

    client.stop(); // Ensure previous connection is closed before reconnecting
    delay(1000); // Allow some time for disconnection

    Serial.println("[DEBUG] Connecting to redirected server...");
    if (client.connect(newHost.c_str(), 443)) {
      Serial.println("[DEBUG] Connected to redirected server");

      client.print("GET ");
      client.print(newPath);
      client.println(" HTTP/1.1");
      client.print("Host: ");
      client.println(newHost);
      client.println("User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)");
      client.println("Connection: close");
      client.println();
      int httpCode = getHTTPResponseCode();
      Serial.print("[DEBUG] HTTP Response Code: ");
      Serial.println(httpCode);
    } else {
      Serial.println("[ERROR] Failed to connect to redirected server.");
    }
  } else {
    Serial.println("[ERROR] No redirect URL found.");
  }
}

int getHTTPResponseCode() {
  Serial.println("[DEBUG] Waiting for HTTP response...");
  while (client.available() == 0) {
    delay(100);
  }
  
  while (client.available()) {
    String line = client.readStringUntil('\n');
    Serial.println("[DEBUG] " + line);
    if (line.startsWith("HTTP/1.1 ")) {
      int code = line.substring(9, 12).toInt(); // Extract the HTTP code
      Serial.print("[DEBUG] Extracted HTTP Response Code: ");
      Serial.println(code);
      return code;
    }
  }
  Serial.println("[ERROR] No valid HTTP response code found.");
  return 0; // Return 0 if no valid response code is found
}

String getRedirectURL() {
  String location = "";
  Serial.println("[DEBUG] Reading HTTP headers...");
  while (client.available()) {
    String line = client.readStringUntil('\n');
    Serial.println("[DEBUG] " + line);

    if (line.startsWith("Location: ")) {
      location = line.substring(10);
      location.trim();
      Serial.print("[DEBUG] Moved Location URL: ");
      Serial.println(location);
    }

    if (line == "\r") {
      break;
    }
  }
  return location;
}

void loop() {
  Serial.println("[DEBUG] Reading response...");
  read_response();

  if (!client.connected()) {
    Serial.println("\n[DEBUG] Disconnecting from server.");
    client.stop();
    while (true);
  }
}

void read_response() {
  uint32_t received_data_num = 0;
  Serial.println("\n[DEBUG] Final Response:");
  while (client.available()) {
    char c = client.read();
    Serial.print(c);
    received_data_num++;
    if (received_data_num % 80 == 0) {
      Serial.println();
    }
  }
  Serial.println("\n[DEBUG] Response Complete.");
  client.stop();
}

void printWifiStatus() {
  Serial.println("[DEBUG] WiFi Status:");
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}
