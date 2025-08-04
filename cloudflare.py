import requests, uuid, datetime, os, json

API_LIST = [
    "https://api.cloudflareclient.com/v0i2407010000/reg",
    "https://api.cloudflareclient.com/v0i2406010000/reg",
    "https://api.cloudflareclient.com/v0i2405010000/reg"
]

def get_available_api():
    for url in API_LIST:
        try:
            r = requests.post(url, timeout=3)
            if r.status_code in [200, 400]:
                return url
        except Exception:
            continue
    return API_LIST[0]

def register(pubkey, privkey):
    url = get_available_api()
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "1.1.1.1/6.33 (Android; arm64-v8a; Android 13; Build/1234567)"
    }
    data = {
        "key": pubkey,
        "install_id": str(uuid.uuid4()),
        "fcm_token": str(uuid.uuid4()) + ":APA91b" + os.urandom(33).hex(),
        "warp_enabled": True,
        "tos": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "model": "Pixel 7 Pro",
        "type": "Android",
        "locale": "en_US"
    }
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    resp.raise_for_status()
    return resp.json()
# trigger build
