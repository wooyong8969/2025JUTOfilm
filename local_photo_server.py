import os
import uuid
from flask import Flask, request, send_from_directory, jsonify, abort

# ========================
# 설정
# ========================

BASE_DIR = os.path.abspath("shared_photos")  # 사진 저장 폴더
PORT = 5000                                  # 서버 포트

os.makedirs(BASE_DIR, exist_ok=True)

app = Flask(__name__)

# ========================
# 기본 확인
# ========================

@app.route("/")
def index():
    return "PHOTO BOOTH SERVER OK"

# ========================
# 업로드
# ========================

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
        "download_url": f"/photos/{filename}"
    })

# ========================
# 다운로드
# ========================

@app.route("/photos/<path:filename>")
def download(filename):
    path = os.path.join(BASE_DIR, filename)

    if not os.path.exists(path):
        abort(404, "File not found")

    return send_from_directory(
        BASE_DIR,
        filename,
        as_attachment=True
    )

# ========================
# 서버 시작
# ========================

if __name__ == "__main__":
    print("===================================")
    print(" Local Photo Server Running ")
    print(f" Save dir : {BASE_DIR}")
    print(f" Port     : {PORT}")
    print("===================================")

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False
    )
