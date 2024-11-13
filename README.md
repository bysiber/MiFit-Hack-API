# MiFit-Hack-API
Reverse Engineering Mi Fit API to Access Your Fitness Data from the app
# Reverse Engineering Mi Fit API to Retrieve Fitness Data

## Prerequisites

### Tools Needed:
- A spare Android device (version >= 7.1.1)
- Root access via Magisk (or another root/superuser method)
  - If using Magisk, ensure you have the `MagiskTrustUserCerts` module installed and activated
  - Alternatively, use a tool like "certInstaller [Root]" for cert installation
- mitmproxy (must be on the same network as the Android device)

### Setup Instructions:

1. Install the Mi Fit app on your Android device (from the Play Store or APK).
2. On your PC, run mitmproxy to intercept HTTP(S) traffic.
3. Copy mitmproxy's root CA certificate to your Android device (this can be done via email, USB file transfer, or ADB push).
4. Import the certificate into your Android device. 
   - On devices with Android >7.1.1 and the Magisk module or "certInstaller [Root]", reboot the device after importing to ensure the cert works as a system certificate.
5. On the Android device, open Wi-Fi settings, select the connected network, and configure it to use mitmproxy as the proxy (set mitmproxy’s IP and port).
6. Ensure internet traffic, including HTTPS requests, flows through mitmproxy.

## Hacking the Mi Fit API

### 1. Logging into Mi Fit Account:
- Log in to your Mi Fit account (e.g., using email).
- Monitor the traffic in mitmproxy to intercept the API calls.

### 2. Obtaining Access Token:
- A POST request is made to `https://api-user.huami.com/registrations/[EMAIL-ADDRESS]/tokens`.
- The request uses URL encoding, and the password is sent in plain text.
- Required fields:
  - `state`: 'REDIRECTION'
  - `client_id`: 'HuaMi'
  - `redirect_uri`: `https://s3-us-west-2.amazonws.com/hm-registration/successsignin.html`
  - `token`: 'access'
  - `password`: [your password]
- The response contains a redirect URI with URL parameters including `access` (the access token) and `country_code`.

### 3. Getting API Credentials:
- A POST request is sent to `https://account.huami.com/v2/client/login`.
- Required fields:
  - `app_name`: 'com.xiaomi.hm.health'
  - `country_code`: [from the previous step]
  - `code`: [access token]
  - `device_id`: '02:00:00:00:00:00'
  - `device_model`: 'android_phone'
  - `grant_type`: 'access_token'
  - `third_name`: 'huami'
  - `lang`: 'de'
- On success, the response returns a JSON object containing the `login_token`, `app_token`, and `user_id`. These values are used for further API communication.

### 4. Retrieving Mi Band Data:
- A GET request is made to `https://api-mifit.huami.com/v1/data/band_data.json`.
- Required GET parameters:
  - `query_type`: 'summary'
  - `device_type`: 'android_phone'
  - `userid`: [user_id from the previous step]
  - `from_date`: '2019-01-01'
  - `to_date`: '2019-12-31'
- A header `apptoken` must be set with the `app_token` from the API credentials.

The response contains daily fitness data for the specified period. The `summary` field for each day contains a BASE64-encoded JSON structure.

### 5. Decoding the Data:
After decoding, the following information is available:

- **Step Data (`stp`)**:
  - `ttl`: Total steps for the day
  - `dis`: Total distance walked (in meters)
  - `cal`: Calories burned
  - `stage`: List of individual activities (e.g., walking, running) with detailed information:
    - `start`: Start time (minutes since midnight)
    - `end`: End time
    - `step`: Number of steps during the activity
    - `dis`: Distance in meters
    - `cal`: Calories burned during the activity
    - `mode`: Activity type (1 = walking, 7 = normal steps, others TBD)

- **Sleep Data (`slp`)**:
  - `st`: Start of sleep (epoch seconds)
  - `ed`: End of sleep (epoch seconds)
  - `dp`: Deep sleep duration (in minutes)
  - `lt`: Light sleep duration (in minutes)
  - `stage`: List of sleep phases with details:
    - `start`: Start time of the phase (minutes since midnight)
    - `end`: End time of the phase
    - `mode`: Sleep type (4 = light sleep, 5 = deep sleep, others TBD)

### Example Implementation:

To run the script:

```bash
./mifit_api.py --email me@mydomain.com --password s3cr3t
