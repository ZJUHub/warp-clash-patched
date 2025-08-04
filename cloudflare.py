import json

# === 固定 Warp+ 账号（真实账号信息写在这里） ===
WARP_PLUS_ACCOUNT = {
    "id": "abcd1234-xxxx-xxxx-xxxx-abcdef123456",
    "token": "eyJh...your_token_here",
    "license_key": "ABCDE-FGHIJ-KLMNO-PQRST-UVWXY",
    "account_type": "plus",
    "warp_plus": True,
    "private_key": "your_private_key_here",
    "peer_publickey": "your_peer_publickey_here",
    "endpoint": "162.159.192.1:2408",
    "quota": 10737418240,
    "usage": 0
}

# === 程序接口，兼容原版调用 ===
def getAccount(*args, **kwargs):
    return WARP_PLUS_ACCOUNT

def register(*args, **kwargs):
    return WARP_PLUS_ACCOUNT

def updatePublicKey(*args, **kwargs): return None
def updateLicenseKey(*args, **kwargs): return None

# trigger build
