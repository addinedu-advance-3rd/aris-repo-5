import requests
import base64
import streamlit as st

# Flask 서버 주소 (2번 노트북의 IP)
FLASK_SERVER_URL = "http://192.168.0.11:5000"

def send_image_to_server(image_path):
    """Flask 서버에 이미지를 전송하는 함수"""
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    data = {
        "image": image_base64,
        "order": {"flavor": "chocolate", "topping": "nuts"}
    }

    response = requests.post(f"{FLASK_SERVER_URL}/upload", json=data)

    if response.status_code == 200:
        print("✅ 이미지 업로드 성공:", response.json())
    else:
        print("❌ 서버 응답 실패:", response.text)

def get_caricature_result():
    """Flask 서버에서 캐리커쳐 결과를 요청하는 함수"""
    response = requests.get(f"{FLASK_SERVER_URL}/result")

    if response.status_code == 200:
        data = response.json()
        caricature_image = base64.b64decode(data["image"])

        # 받은 이미지를 저장
        with open("received_caricature.jpg", "wb") as f:
            f.write(caricature_image)
        print("✅ 캐리커쳐 이미지 저장 완료!")

    else:
        print("❌ 서버로부터 캐리커쳐 결과를 받지 못했습니다.")

# 1️⃣ 메인 실행부 추가
if __name__ == "__main__":
    print("📡 1번 노트북: 2번 노트북(Flask 서버)와 통신 시작!")

    # 2️⃣ 이미지를 Flask 서버로 전송
    image_path = "image.jpg"  # 보낼 이미지 경로
    send_image_to_server(image_path)

    # 3️⃣ 캐리커쳐 결과 요청 및 저장
    get_caricature_result()