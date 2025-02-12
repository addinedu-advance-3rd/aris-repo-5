import requests
import json
import base64
import os
import streamlit as st
FLASK_SERVER_URL = "http://192.168.0.62:5000/upload"
# 저장할 경로 (원하는 경로로 변경)
TARGET_DIR = "images/caricatures"
if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)
class CommunicationClient:

    def __init__(self, order_info, image_paths):

        self.image_paths = image_paths
        self.order_info = order_info
        # [['strawberry', ['jollypong', 'chocoball'], True], ['blueberry', ['chocoball'], False]]

    def run(self):
        image_counter = 1
        files = {}

        data = {
            'order_info': json.dumps(st.session_state.order_info)
        }
        if self.image_paths:
            for info in st.session_state.order_info:
                if info[2] == True:
                    files[f'image{image_counter}'] = open(f'images/caricatures/original_{image_counter}.jpg','rb')
                    image_counter += 1

        # 서버로 데이터 전송
        response = requests.post(FLASK_SERVER_URL, files=files, data=data)

        if self.image_paths:
            # 서버로부터 받은 이미지 데이터 처리
            if response.status_code == 200:
                response_data = response.json()
                for key, value in response_data.items():
                    # base64로 인코딩된 문자열을 디코딩하여 이미지 데이터를 얻음
                    image_data = base64.b64decode(value)
                    # TARGET_DIR 경로에 파일 저장
                    target_path = os.path.join(TARGET_DIR, f'sketch_{key}.jpg')
                    with open(target_path, 'wb') as f:
                        f.write(image_data)
                    print(f'{target_path}에 이미지 저장 완료!')
                print('성공!')
            else:
                print(f'Failed to receive images. Status code: {response.status_code}')



def send_order_data(order_info, image_paths):
    client = CommunicationClient(order_info, image_paths)
    client.run()

# if __name__ == "__main__":
#     image_path = "/home/kang/aris-repo-5/image copy.png"
#     order_info = []
#     send_order_data(order_info,image_path)
