import requests
import base64
import streamlit as st

# Flask 서버 주소 (2번 노트북의 IP)
FLASK_SERVER_URL = "http://192.168.0.11"

def send_image_to_server(image):
    """Flask 서버에 이미지를 전송하는 함수"""
    image_bytes = image.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    data = {
        "image": image_base64,
        "order": {"flavor": "chocolate", "topping": "nuts"}
    }

    response = requests.post(f"{FLASK_SERVER_URL}/upload", json=data)

    if response.status_code == 200:
        return response.json()
    else:
        st.error("서버로부터 응답을 받지 못했습니다.")
        return None

def get_caricature_result():
    """Flask 서버에서 캐리커쳐 결과를 요청하는 함수"""
    response = requests.get(f"{FLASK_SERVER_URL}/result")

    if response.status_code == 200:
        data = response.json()
        return base64.b64decode(data["image"])
    else:
        st.error("서버로부터 캐리커쳐 결과를 받지 못했습니다.")
        return None