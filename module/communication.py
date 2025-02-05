from flask import Flask, request, jsonify, send_file
import os

app = Flask(__name__)

CARICATURE_PATH = "/home/addinedu/aris/aris-repo-5/canny_img.jpg"  # `caricature.py`에서 저장하는 이미지 경로

@app.route('/result', methods=['GET'])
def get_caricature():
    """1번 노트북이 캐리커쳐 이미지를 요청하면 해당 이미지를 전송"""
    if os.path.exists(CARICATURE_PATH):
        return send_file(CARICATURE_PATH, mimetype="image/jpeg")
    else:
        return jsonify({"error": "캐리커쳐 없음"}), 400


if __name__ == "__main__":
    app.run(host="192.168.0.11", port=5000)
