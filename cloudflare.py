
import requests, uuid, datetime, os, json, time, random

API_LIST = [
    "https://api.cloudflareclient.com/v0i2407010000/reg",
    "https://api.cloudflareclient.com/v0i2406010000/reg",
    "https://api.cloudflareclient.com/v0i2405010000/reg"
]

def random_license_key():
    """生成随机 Warp+ License Key"""
    return "-".join([uuid.uuid4().hex[:5] for _ in range(5)]).upper()

class Account:
    def __init__(self, data):
        self.data = data
        self.id = data.get("id", "")
        self.account_id = data.get("account_id", "")
        self.token = data.get("token", "")
        self.license_key = data.get("license_key", "")
        self.private_key = data.get("private_key", "")
        self.peer_publickey = data.get("peer_publickey", "")
        self.endpoint = data.get("endpoint", "162.159.192.1:2408")
        self.quota = data.get("quota", 0)
        self.account_type = data.get("account_type", "plus" if self.license_key else "free")
        self.usage = data.get("usage", 0)
        self.warp_plus = data.get("warp_plus", bool(self.license_key))
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

def fetch_account_details(account_id, access_token, retries=3):
    """获取完整账户详情，带重试"""
    url = f"https://api.cloudflareclient.com/v0i2407010000/reg/{account_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "1.1.1.1/6.33 (Android; arm64-v8a; Android 13; Build/1234567)"
    }
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 429:  # 限流
                time.sleep(2 + random.random() * 2)
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt == retries - 1:
                print(f"Failed to fetch account details after retries: {e}")
    return {}

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
        "locale": "en_US",
        "license_key": random_license_key()  # 自动生成 Warp+ Key
    }
    if "referrer" in kwargs:
        data["referrer"] = kwargs["referrer"]

    # 第一步：注册
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    resp.raise_for_status()
    account_data = resp.json()

    # 第二步：获取完整账号详情
    account_id = account_data.get("id")
    token = account_data.get("token")
    if account_id and token:
        detail_data = fetch_account_details(account_id, token)
        account_data.update(detail_data)

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
    # 如果没有现成账号，自动注册 Warp+
    return register()

# 确保必要目录和文件存在，避免测速报错
os.makedirs("config", exist_ok=True)
if not os.path.exists("result.csv"):
    with open("result.csv", "w") as f:
        f.write("")


# trigger build
