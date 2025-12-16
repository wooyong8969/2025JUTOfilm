import requests
import qrcode

SERVER_BASE = "http://10.138.24.168:5000"

def upload_photo(image_path):
    url = f"{SERVER_BASE}/upload"

    with open(image_path, "rb") as f:
        files = {"file": f}
        resp = requests.post(url, files=files)

    resp.raise_for_status()
    data = resp.json()

    return SERVER_BASE + data["download_url"]

def make_qr(url, save_path="qr.png"):
    qr = qrcode.make(url)
    qr.save(save_path)
    return save_path
