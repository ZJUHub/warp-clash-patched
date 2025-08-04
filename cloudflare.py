import requests, uuid, datetime, os, json, time, random

API_LIST = [
    "https://api.cloudflareclient.com/v0i2407010000/reg",
    "https://api.cloudflareclient.com/v0i2406010000/reg",
    "https://api.cloudflareclient.com/v0i2405010000/reg"
]

def random_license_key():
    """生成随机 Warp+ License Key"""
    return "-".join([uuid.uuid4().hex[:5] for _ in range(5)]).upper()

def get_available_api():
    for url in API_LIST:
        try:
            r = requests.post(url, timeout=3)
            if r.status_code in [200, 400]:
                return url
        except Exception:
            continue
    return API_LIST[0]

def register(pubkey=None, privkey=None, **kwargs):
    """原版注册逻辑 + 补丁：Warp+ Key + 429 重试"""
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
        "locale": "en_US",
        "license_key": random_license_key()  # 自动生成 Warp+ Key
    }
    if "referrer" in kwargs:
        data["referrer"] = kwargs["referrer"]

    # 带重试的请求，防止 429 失败
    for attempt in range(5):
        try:
            resp = requests.post(url, headers=headers, data=json.dumps(data))
            if resp.status_code == 429:  # 限流，等待后重试
                time.sleep(2 + random.random() * 2)
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt == 4:
                raise e
            time.sleep(1)
    return {}

def updatePublicKey(*args, **kwargs): return None
def updateLicenseKey(*args, **kwargs): return None


# trigger build
