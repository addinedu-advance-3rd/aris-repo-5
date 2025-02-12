# Flask 서버 코드 (server.py)
from flask import Flask, request, jsonify
from PIL import Image
import json
from io import BytesIO
import os
import cv2
from queue import Queue
import threading
import time
from caricature import get_arm_path
from module.model import get_caricature
from xArm_Python_SDK.xarm import version
from xArm_Python_SDK.xarm.wrapper import XArmAPI
from xArm_Python_SDK.arm_final import RobotMain
import base64
app = Flask(__name__)

# 저장할 디렉토리 설정
RAW_IMAGE_SAVE_DIR = 'raw_image'
CARI_IMAGE_SAVE_DIR = 'cari_image'

os.makedirs(RAW_IMAGE_SAVE_DIR, exist_ok=True)
os.makedirs(CARI_IMAGE_SAVE_DIR, exist_ok=True)

order_queue = Queue()
image_cnt = 1

#로봇 통신
RobotMain.pprint('xArm-Python-SDK Version:{}'.format(version.__version__))
arm = XArmAPI('192.168.1.167', baud_checkset=False)
robot_main = RobotMain(arm, "A")

def process_order():
    global order_queue

    while True:
        if not order_queue.empty():
            order_info, image_path = order_queue.get()
            if image_path:
                # 좌표 따기
                coor = get_arm_path(image_path)
                print("image 있음")
            else:
                coor = None
                print("image 없음")
            # 로봇암 동작(coor 없으면 로봇암 동작 코드에서 그림 그리기 패스)
            print("robot run")
            robot_main.run(order_info, coor)
            print()
        time.sleep(0.1)

def convert_pil_image_to_base64(image):
    """
    PIL 이미지 객체를 Base64 문자열로 변환하는 함수

    :param image: 변환할 PIL 이미지 객체 (Stable Diffusion 결과물)
    :return: Base64 인코딩된 이미지 문자열
    """
    buffered = BytesIO()
    image.save(buffered, format="JPEG")  # JPEG 포맷으로 저장 (저장 없이 메모리 내에서 처리)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')  # Base64 인코딩 후 문자열 반환

@app.route('/upload', methods=['POST'])
def upload():
    global order_queue, image_cnt

    order_infos_str = request.form.get('order_info', 'No order info provided')
    print(f'Received order details: {order_infos_str}')

    if order_infos_str == 'No order info provided':
        return jsonify({"error": "No order info provided"}), 400

    # JSON 문자열을 파싱하여 파이썬 리스트로 변환
    order_infos = json.loads(order_infos_str)

    response_data = {}

    # order_queue에 (주문내역, 이미지 경로) 저장
    file_cnt = 1
    if order_infos != 'No order info provided':
        
        for order_info in order_infos:
            print("order_info =", order_info)
            cari_image_path = None
            if order_info[2] == True: # 이미지 있음
                # 원본 이미지 저장
                if request.files:
                    print('requset.files =', request.files)
                image = request.files.get(f'image{file_cnt}')
                print("image 불러오기 성공!")
                if image is None:
                    print(f"image{file_cnt} 파일이 업로드되지 않았습니다.")
                    continue
                image_path = os.path.join(RAW_IMAGE_SAVE_DIR, f'image{image_cnt}.jpg')
                image.save(image_path)
                
                print(f'saved to {image_path}')
                
                #캐리커쳐
                cari_image = get_caricature(image_path)

                cari_image_path = os.path.join(CARI_IMAGE_SAVE_DIR, f'image{image_cnt}.jpg')
                cari_image.save(cari_image_path)

                cari_image_base64 = convert_pil_image_to_base64(cari_image)

                # 웹에 보낼 데이터
                response_data[f'image{file_cnt}'] = cari_image_base64

                file_cnt += 1
                image_cnt += 1
            else:
                image_path = None
            order_queue.put((order_info, cari_image_path))
    

    return jsonify(response_data)

if __name__ == '__main__':
    # 주문 처리 스레드 시작
    order_thread = threading.Thread(target=process_order, daemon=True)
    order_thread.start()
    app.run(host='0.0.0.0', port=5000)

