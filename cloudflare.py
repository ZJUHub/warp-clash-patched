import requests, uuid, datetime, os, json

API_LIST = [
    "https://api.cloudflareclient.com/v0i2407010000/reg",
    "https://api.cloudflareclient.com/v0i2406010000/reg",
    "https://api.cloudflareclient.com/v0i2405010000/reg"
]

class Account:
    def __init__(self, data):
        self.data = data
        self.id = data.get("id", "")
        self.token = data.get("token", "")
        self.license_key = data.get("license_key", "")
        self.quota = data.get("quota", 0)
        self.account_type = data.get("account_type", "free")
        self.usage = data.get("usage", 0)
        self.path = "account/account.json"
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f)

def get_available_api():
    for url in API_LIST:
        try:
            r = requests.post(url, timeout=3)
            if r.status_code in [200, 400]:
                return url
        except Exception:
            continue
    return API_LIST[0]

def fetch_account_details(account_id, access_token):
    """获取完整账户详情"""
    url = f"https://api.cloudflareclient.com/v0i2407010000/reg/{account_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "1.1.1.1/6.33 (Android; arm64-v8a; Android 13; Build/1234567)"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def register(pubkey=None, privkey=None, **kwargs):
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
    if "referrer" in kwargs:
        data["referrer"] = kwargs["referrer"]

    # 第一步：注册
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    resp.raise_for_status()
    account_data = resp.json()

    # 第二步：获取完整账号详情
    try:
        account_id = account_data.get("id")
        token = account_data.get("token")
        if account_id and token:
            detail_data = fetch_account_details(account_id, token)
            account_data.update(detail_data)
    except Exception as e:
        print(f"Warning: failed to fetch full account details: {e}")

    # 创建账户对象并保存
    acc = Account(account_data)
    acc.save()
    return acc

def updatePublicKey(*args, **kwargs): return None
def updateLicenseKey(*args, **kwargs): return None

def getAccount(*args, **kwargs):
    if os.path.exists("account/account.json"):
        with open("account/account.json") as f:
            data = json.load(f)
        return Account(data)
    return Account({})

os.makedirs("config", exist_ok=True)


# trigger build
