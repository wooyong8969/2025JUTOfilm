import os
import uuid
import time
import threading
from flask import Flask, request, send_from_directory, jsonify, abort

# ========================
# 설정
# ========================

BASE_DIR = os.path.abspath("shared_photos")  # 사진 저장 폴더
PORT = 5000                                 # 서버 포트
EXPIRE_SECONDS = 60 * 10                    # 10분 후 자동 삭제

os.makedirs(BASE_DIR, exist_ok=True)

app = Flask(__name__)

@app.route("/")
def index():
    return "PHOTO BOOTH SERVER OK"


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        abort(400, "No file")

    file = request.files["file"]
    if file.filename == "":
        abort(400, "Empty filename")

    photo_id = str(uuid.uuid4())
    filename = f"{photo_id}.jpg"
    path = os.path.join(BASE_DIR, filename)

    file.save(path)

    return jsonify({
        "id": photo_id,
        "download_url": f"/photo/{photo_id}"
    })


@app.route("/photo/<photo_id>")
def download(photo_id):
    filename = f"{photo_id}.jpg"
    path = os.path.join(BASE_DIR, filename)

    if not os.path.exists(path):
        abort(404, "File not found")

    return send_from_directory(
        BASE_DIR,
        filename,
        as_attachment=True
    )


# ========================
# 자동 삭제 스레드
# ========================

def cleanup_loop():
    while True:
        now = time.time()
        for fname in os.listdir(BASE_DIR):
            path = os.path.join(BASE_DIR, fname)
            if os.path.isfile(path):
                if now - os.path.getmtime(path) > EXPIRE_SECONDS:
                    try:
                        os.remove(path)
                        print(f"[CLEANUP] removed {fname}")
                    except Exception as e:
                        print("[CLEANUP ERROR]", e)
        time.sleep(60)


# ========================
# 서버 시작
# ========================

if __name__ == "__main__":
    threading.Thread(target=cleanup_loop, daemon=True).start()

    print("===================================")
    print(" Local Photo Server Running ")
    print(f" Save dir : {BASE_DIR}")
    print(f" Port     : {PORT}")
    print("===================================")

    app.run(
        host="0.0.0.0",   # ⭐ 핫스팟에서 접속 가능하게
        port=PORT,
        debug=False
    )
