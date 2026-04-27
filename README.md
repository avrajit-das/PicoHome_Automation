# 🏠 IoT Home Automation — Final Year Project Guide
### Raspberry Pi Pico W + DHT11 + SSR + Firebase

---

## 📋 PROJECT OVERVIEW

| Component | Detail |
|-----------|--------|
| Microcontroller | Raspberry Pi Pico W (Wi-Fi built-in) |
| Sensor | DHT11 (Temperature & Humidity) |
| Load Switching | 3× Solid State Relay (SSR) modules |
| Cloud Backend | Firebase Realtime Database |
| Authentication | Firebase Auth (Email/Password) |
| Web Hosting | Firebase Hosting |
| Firmware | MicroPython |

---

## 🔌 HARDWARE WIRING DIAGRAM

```
Raspberry Pi Pico W
        ┌─────────────────────────────┐
   GP2  │━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━► SSR-1 IN (Load 1)
   GP3  │━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━► SSR-2 IN (Load 2)
   GP4  │━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━► SSR-3 IN (Load 3)
   GP15 │━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━► DHT11 DATA
   3.3V │━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━► DHT11 VCC
        │         └──────────────────────► SSR VCC (if 3.3V type)
   GND  │━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━► DHT11 GND
        │         └──────────────────────► SSR GND
        └─────────────────────────────┘

DHT11:
  Pin 1 (VCC)  → 3.3V
  Pin 2 (DATA) → GP15 (+ 10kΩ pull-up to 3.3V)
  Pin 4 (GND)  → GND

SSR Module (per relay, ×3):
  IN+  → Pico GPIO (GP2 / GP3 / GP4)
  IN-  → Pico GND
  OUT  → Connect in series with AC Load (LINE side)
  ⚠️  NEVER touch AC side without proper insulation!
```

> **Safety:** AC mains voltage is lethal. Enclose all AC wiring in a proper enclosure. Use properly rated SSRs (≥ 10A, 240VAC). Keep AC and DC wiring separated.

---

## 📦 COMPONENTS LIST

| # | Component | Qty | Notes |
|---|-----------|-----|-------|
| 1 | Raspberry Pi Pico W | 1 | Wi-Fi enabled |
| 2 | DHT11 Sensor Module | 1 | With pull-up resistor |
| 3 | Solid State Relay (SSR) | 3 | 5–10A, 240VAC, 3–32VDC input |
| 4 | 10kΩ Resistor | 1 | DHT11 data pull-up |
| 5 | Breadboard + Jumper wires | – | For prototyping |
| 6 | USB Micro-B cable | 1 | Programming Pico W |
| 7 | AC Power supply (5V/2A) | 1 | For Pico W power |
| 8 | Electrical enclosure box | 1 | For safety |
| 9 | AC bulb/fan/load | 3 | For testing |

---

## 🚀 STEP-BY-STEP SETUP

---

### STEP 1 — Install MicroPython on Pico W

1. Download MicroPython UF2 for Pico W from:
   https://micropython.org/download/RPI_PICO_W/

2. Hold the **BOOTSEL** button on your Pico W, plug USB in, release button.

3. Pico appears as `RPI-RP2` USB drive.

4. **Drag & drop** the `.uf2` file onto the drive.

5. Pico reboots automatically with MicroPython.

---

### STEP 2 — Install Thonny IDE

1. Download Thonny from: https://thonny.org

2. Open Thonny → **Tools → Options → Interpreter**

3. Select: **MicroPython (Raspberry Pi Pico)**

4. Select correct COM port → Click OK

5. You should see `>>>` REPL prompt at the bottom.

---

### STEP 3 — Create Firebase Project

#### 3A. Create the Project

1. Go to: https://console.firebase.google.com

2. Click **"Add project"**

3. Name it: `home-automation` → Continue

4. **Disable** Google Analytics (optional) → Create project

#### 3B. Add Web App

1. In project dashboard, click **`</>`** (Web app icon)

2. App nickname: `nexhome-dashboard`

3. ✅ Check **"Also set up Firebase Hosting"**

4. Click **Register app**

5. **COPY the firebaseConfig object** — you'll need it!
   ```javascript
   const firebaseConfig = {
     apiKey: "AIza...",
     authDomain: "home-automation-xxxxx.firebaseapp.com",
     databaseURL: "https://home-automation-xxxxx-default-rtdb.firebaseio.com",
     projectId: "home-automation-xxxxx",
     storageBucket: "home-automation-xxxxx.appspot.com",
     messagingSenderId: "123456789",
     appId: "1:123456789:web:abc123"
   };
   ```

#### 3C. Enable Realtime Database

1. Left sidebar → **Build → Realtime Database**

2. Click **Create Database**

3. Choose location: **us-central1** (or nearest)

4. Start in **Test mode** (for now) → Enable

5. Go to **Rules** tab → paste:
   ```json
   {
     "rules": {
       "home-automation": {
         ".read":  "auth != null",
         ".write": "auth != null"
       }
     }
   }
   ```
6. Click **Publish**

#### 3D. Enable Firebase Authentication

1. Left sidebar → **Build → Authentication**

2. Click **Get started**

3. Under Sign-in providers → **Email/Password** → Enable → Save

4. Go to **Users** tab → **Add user**:
   - Email: `your@email.com`
   - Password: `yourStrongPassword123`
   → **Add user**

   This is your admin login for the dashboard.

#### 3E. Get Database Secret (for Pico W)

1. Go to **Project Settings** (gear icon) → **Service accounts**

2. Scroll to **Database secrets** → **Show** → Copy the secret key

3. Paste it in `pico_main.py` as `FIREBASE_AUTH`

---

### STEP 4 — Configure and Flash Pico W

1. Open `pico_main.py` in Thonny

2. Edit these lines:
   ```python
   WIFI_SSID     = "YourHomeWiFi"
   WIFI_PASSWORD = "YourWiFiPassword"
   FIREBASE_URL  = "https://home-automation-xxxxx-default-rtdb.firebaseio.com"
   FIREBASE_AUTH = "your_database_secret_from_step_3E"
   ```

3. In Thonny: **File → Save as → Raspberry Pi Pico**

4. Save the file as **`main.py`** (exactly this name — Pico auto-runs it)

5. Click the **Run ▶** button or press F5

6. Check the Shell panel — you should see:
   ```
   [WiFi] Connecting to YourHomeWiFi ...........
   [WiFi] Connected! ('192.168.x.x', ...)
   [Firebase] Sensor data pushed: ...
   [Relays] R1=False  R2=False  R3=False
   [System] Running. Polling Firebase every 2 s
   ```

7. Go to Firebase Console → Realtime Database → you should see data appearing under `/home-automation/`

---

### STEP 5 — Configure the Web Dashboard

1. Open `dashboard.html` in a text editor

2. Find the `firebaseConfig` block near the bottom and replace ALL values with your Firebase config from Step 3B:
   ```javascript
   const firebaseConfig = {
     apiKey:            "YOUR_ACTUAL_API_KEY",
     authDomain:        "home-automation-xxxxx.firebaseapp.com",
     databaseURL:       "https://home-automation-xxxxx-default-rtdb.firebaseio.com",
     projectId:         "home-automation-xxxxx",
     storageBucket:     "home-automation-xxxxx.appspot.com",
     messagingSenderId: "123456789012",
     appId:             "1:123456789:web:abcdef123456"
   };
   ```

3. Save the file.

---

### STEP 6 — Deploy to Firebase Hosting

1. Install Node.js from: https://nodejs.org (LTS version)

2. Open Terminal / Command Prompt in your project folder

3. Install Firebase CLI:
   ```bash
   npm install -g firebase-tools
   ```

4. Login to Firebase:
   ```bash
   firebase login
   ```
   (Opens browser → Sign in with Google)

5. Initialize Firebase Hosting:
   ```bash
   firebase init hosting
   ```
   - Select your project: `home-automation-xxxxx`
   - What to use as public directory? → Type: **`.`** (current folder)
   - Single-page app? → **N**
   - Overwrite index.html? → **N**

6. Rename `dashboard.html` to `index.html` (or set it as default):
   ```bash
   # OR edit firebase.json to point to dashboard.html
   ```
   Update `firebase.json`:
   ```json
   {
     "hosting": {
       "public": ".",
       "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
       "rewrites": [
         { "source": "**", "destination": "/dashboard.html" }
       ]
     }
   }
   ```

7. Deploy:
   ```bash
   firebase deploy --only hosting
   ```

8. Your dashboard is live at:
   ```
   https://home-automation-xxxxx.web.app
   ```

---

### STEP 7 — Test Everything

1. Open your hosted URL

2. Login with the email/password you created in Step 3D

3. You should see:
   - ✅ Device Status → Online
   - ✅ Temperature and Humidity updating every 10 seconds
   - ✅ Toggle switches controlling relays in real-time
   - ✅ Sensor chart updating
   - ✅ History log filling up

4. Try toggling a relay switch → within 2 seconds, the GPIO on Pico W changes → SSR switches the load

---

## 📁 FILE STRUCTURE

```
your-project/
├── dashboard.html        ← Web dashboard (login + control)
├── pico_main.py          ← Flash this to Pico W as main.py
├── firebase-database-rules.json  ← Paste into Firebase console
├── firebase.json         ← Created by firebase init
└── README.md             ← This file
```

---

## 🔒 SECURITY NOTES

1. **Never** share your `FIREBASE_AUTH` secret publicly
2. Use Firebase Database Rules to restrict access (already configured)
3. Only authenticated users can read/write data
4. For production: use environment variables for secrets
5. Enable HTTPS-only access in Firebase Hosting settings

---

## 🛠️ TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Pico can't connect to WiFi | Check SSID/password, ensure 2.4GHz band |
| Firebase data not appearing | Check FIREBASE_URL and FIREBASE_AUTH in pico_main.py |
| DHT11 read error | Add 10kΩ pull-up between DATA and 3.3V |
| Login fails | Verify email/password in Firebase Auth console |
| Relay not switching | Check GPIO wiring, verify SSR is active-HIGH or flip logic |
| Dashboard not loading | Check firebaseConfig values in dashboard.html |
| CORS error in browser | Use Firebase Hosting (not local file://) |

---

## 📊 FIREBASE DATABASE STRUCTURE

```
home-automation/
├── device/
│   ├── status: "online"
│   ├── firmware: "1.0.0"
│   └── board: "Pico W"
├── relays/
│   ├── relay1: false
│   ├── relay2: false
│   └── relay3: false
└── sensors/
    ├── temperature: 28
    ├── humidity: 65
    └── lastUpdated: 1720000000  (Unix timestamp)
```

---

## 🎓 PROJECT ENHANCEMENTS (For Viva / Extra Marks)

- [ ] Add automation rules (e.g., turn on fan if temp > 32°C)
- [ ] Email/SMS alerts using Firebase Functions + Twilio
- [ ] Add more sensors (MQ-2 gas sensor, PIR motion)
- [ ] Mobile app using Flutter + Firebase
- [ ] Voice control via Google Assistant webhook
- [ ] Offline mode with local relay state cache on Pico W
- [ ] Energy meter monitoring with PZEM-004T
- [ ] OTA (Over The Air) firmware update

---

## 🧑‍💻 TECH STACK SUMMARY

```
Pico W ──WiFi──► Firebase RTDB ──Realtime──► Web Dashboard
  │                    │                          │
  ├─ Reads relay       ├─ Stores sensor data      ├─ Firebase Auth
  │  states every 2s   ├─ Stores relay cmds       ├─ Toggle switches
  └─ Pushes DHT11      └─ Device status           └─ Live chart
     every 10s                                    └─ History log
```

---

*Final Year Project — IoT Home Automation using Raspberry Pi Pico W*
*Firebase + MicroPython + DHT11 + SSR*
