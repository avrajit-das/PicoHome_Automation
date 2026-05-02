"""
========================================================
  IoT Home Automation - Raspberry Pi Pico W Firmware
  DHT11 Sensor + 3 SSR Loads + Firebase Realtime DB
========================================================
  Wiring:
    DHT11  DATA  → GP15
    SSR-1  IN    → GP2
    SSR-2  IN    → GP3
    SSR-3  IN    → GP4
    (All SSR GND → Pico GND, SSR VCC → 3.3V or 5V per module)
========================================================
"""

import network
import urequests
import ujson
import time
import machine
import dht

# ─────────────────────────────────────────────────────────
#  USER CONFIGURATION  –  Fill these before flashing
# ─────────────────────────────────────────────────────────
WIFI_SSID     = "YOUR_SSID"
WIFI_PASSWORD = "YOUR_PASSWORD"

# Firebase project settings
FIREBASE_URL  = "https://your-project.rtdb.firebaseio.com/"
FIREBASE_AUTH = ""
# If using database rules (open for testing), leave FIREBASE_AUTH = ""
# For production use a server-side secret from Firebase console

# How often Pico polls Firebase for relay commands (seconds)
POLL_INTERVAL = 0.5

# How often Pico pushes sensor data (seconds)
SENSOR_INTERVAL = 10
# ─────────────────────────────────────────────────────────

# GPIO Pin setup
dht_sensor = dht.DHT11(machine.Pin(15))

relay1 = machine.Pin(2, machine.Pin.OUT)
relay2 = machine.Pin(3, machine.Pin.OUT)
relay3 = machine.Pin(4, machine.Pin.OUT)

# SSR is active-HIGH (relay ON when GPIO = 1)
# Change to: relay.value(not value)  if your module is active-LOW
def set_relay(pin, state: bool):
    pin.value(1 if state else 0)

# Start all relays OFF
set_relay(relay1, False)
set_relay(relay2, False)
set_relay(relay3, False)

# ─── Internal state ───────────────────────────────────────
last_sensor_push = 0
last_poll        = 0
temp             = 0
humidity         = 0


def connect_wifi():
    """Connect to WiFi and wait until connected."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        print("[WiFi] Already connected:", wlan.ifconfig())
        return wlan

    print(f"[WiFi] Connecting to {WIFI_SSID} ...", end="")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    timeout = 20
    while not wlan.isconnected() and timeout > 0:
        print(".", end="")
        time.sleep(1)
        timeout -= 1

    if wlan.isconnected():
        print("\n[WiFi] Connected!", wlan.ifconfig())
    else:
        print("\n[WiFi] FAILED – rebooting in 5 s")
        time.sleep(5)
        machine.reset()

    return wlan


def firebase_url(path: str) -> str:
    """Build a Firebase REST URL for the given path."""
    auth_param = f"?auth={FIREBASE_AUTH}" if FIREBASE_AUTH else ".json"
    if FIREBASE_AUTH:
        return f"{FIREBASE_URL}/{path}.json?auth={FIREBASE_AUTH}"
    return f"{FIREBASE_URL}/{path}.json"


def firebase_get(path: str):
    """GET a value from Firebase RTDB. Returns parsed JSON or None."""
    try:
        url = firebase_url(path)
        r = urequests.get(url, timeout=8)
        data = r.json()
        r.close()
        return data
    except Exception as e:
        print(f"[Firebase GET] Error at {path}: {e}")
        return None


def firebase_patch(path: str, payload: dict):
    """PATCH (merge-update) data at a Firebase RTDB path."""
    try:
        url = firebase_url(path)
        r = urequests.patch(
            url,
            data=ujson.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=8
        )
        r.close()
    except Exception as e:
        print(f"[Firebase PATCH] Error at {path}: {e}")


def read_dht11():
    """Read temperature and humidity from DHT11. Returns (temp_c, humidity)."""
    global temp, humidity
    try:
        dht_sensor.measure()
        temp     = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        print(f"[DHT11] Temp={temp}°C  Humidity={humidity}%")
        return temp, humidity
    except Exception as e:
        print(f"[DHT11] Read error: {e}")
        return temp, humidity  # Return last known values


def push_sensor_data():
    """Push sensor readings to Firebase."""
    t, h = read_dht11()
    payload = {
        "temperature": t,
        "humidity":    h,
        "lastUpdated": int(time.time())
    }
    firebase_patch("home-automation/sensors", payload)
    print(f"[Firebase] Sensor data pushed: {payload}")


def poll_relays():
    """Read relay states from Firebase and apply to GPIO pins."""
    data = firebase_get("home-automation/relays")
    if data and isinstance(data, dict):
        r1 = bool(data.get("relay1", False))
        r2 = bool(data.get("relay2", False))
        r3 = bool(data.get("relay3", False))
        set_relay(relay1, r1)
        set_relay(relay2, r2)
        set_relay(relay3, r3)
        print(f"[Relays] R1={r1}  R2={r2}  R3={r3}")
    else:
        # Initialize relay keys in Firebase if they don't exist
        firebase_patch("home-automation/relays", {
            "relay1": False,
            "relay2": False,
            "relay3": False
        })


def init_device_status():
    """Register device as online in Firebase."""
    firebase_patch("home-automation/device", {
        "status": "online",
        "firmware": "1.0.0",
        "board": "Pico W"
    })


# ─────────────────────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────────────────────
def main():
    global last_sensor_push, last_poll

    wlan = connect_wifi()

    # Initial push
    init_device_status()
    push_sensor_data()
    poll_relays()

    last_sensor_push = time.time()
    last_poll        = time.time()

    print("\n[System] Running. Polling Firebase every", POLL_INTERVAL, "s")

    while True:
        now = time.time()

        # Reconnect WiFi if dropped
        if not wlan.isconnected():
            print("[WiFi] Lost connection – reconnecting...")
            connect_wifi()

        # Poll relays from Firebase
        if now - last_poll >= POLL_INTERVAL:
            poll_relays()
            last_poll = now

        # Push sensor data
        if now - last_sensor_push >= SENSOR_INTERVAL:
            push_sensor_data()
            last_sensor_push = now

        time.sleep(0.1)


main()
