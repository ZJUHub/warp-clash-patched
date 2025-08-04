import requests, uuid, datetime, os, json, time, random, subprocess

API_LIST = [
    "https://api.cloudflareclient.com/v0i2407010000/reg",
    "https://api.cloudflareclient.com/v0i2406010000/reg",
    "https://api.cloudflareclient.com/v0i2405010000/reg"
]

ACCOUNT_PATH = "account/account.json"

def random_license_key():
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

def fetch_account_details(account_id, access_token, retries=5):
    """获取完整账户详情（含 WireGuard 配置）"""
    url = f"https://api.cloudflareclient.com/v0i2407010000/reg/{account_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "1.1.1.1/6.33 (Android; arm64-v8a; Android 13; Build/1234567)"
    }
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 429:
                time.sleep(2 + random.random() * 3)
                continue
            resp.raise_for_status()
            data = resp.json()
            if data.get("peer_publickey") and data.get("private_key"):
                return data
        except Exception as e:
            if attempt == retries - 1:
                print(f"Failed to fetch account details: {e}")
        time.sleep(1)
    return {}

def save_account(data):
    os.makedirs(os.path.dirname(ACCOUNT_PATH), exist_ok=True)
    with open(ACCOUNT_PATH, "w") as f:
        json.dump(data, f)

def run_speedtest():
    """触发节点测速/刷新"""
    try:
        subprocess.run(["bash", "/app/entrypoint.sh"], check=True)
    except Exception as e:
        print(f"Warning: speedtest script failed: {e}")
    if not os.path.exists("result.csv"):
        with open("result.csv", "w") as f:
            f.write("")

def register(pubkey=None, privkey=None, **kwargs):
    """注册 + 补全信息 + 保存 + 刷新订阅"""
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
        "license_key": random_license_key()  # 自动 Warp+ Key
    }
    if "referrer" in kwargs:
        data["referrer"] = kwargs["referrer"]

    # 第一步：注册账号
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    resp.raise_for_status()
    account_data = resp.json()

    # 第二步：获取完整配置
    account_id = account_data.get("id")
    token = account_data.get("token")
    if account_id and token:
        detail_data = fetch_account_details(account_id, token)
        account_data.update(detail_data)

    # 第三步：保存账号信息
    save_account(account_data)

    # 第四步：刷新节点订阅
    run_speedtest()

    return account_data

def updatePublicKey(*args, **kwargs): return None
def updateLicenseKey(*args, **kwargs): return None

def getAccount(*args, **kwargs):
    if os.path.exists(ACCOUNT_PATH):
        with open(ACCOUNT_PATH) as f:
            return json.load(f)
    return register()


# trigger build
