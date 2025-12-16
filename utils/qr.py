import requests
import qrcode
import os

SERVER_BASE = "http://10.138.24.168:5000"

def upload_photo(image_path):
    url = f"{SERVER_BASE}/upload"

    with open(image_path, "rb") as f:
        files = {"file": f}
        resp = requests.post(url, files=files)

    resp.raise_for_status()
    data = resp.json()

    return SERVER_BASE + data["download_url"]


def make_qr(download_url: str, save_dir: str, photo_id: str) -> str:
    """
    QR 코드를 생성해서 파일로 저장
    return: 저장된 QR 파일 경로
    """
    os.makedirs(save_dir, exist_ok=True)

    qr = qrcode.make(download_url)

    qr_path = os.path.join(save_dir, f"qr_{photo_id}.png")
    qr.save(qr_path)

    return qr_path
