import streamlit as st
import numpy as np
import os
from PIL import Image
import cv2
from utils.db_connector import get_db_connection
from utils.communication import CommunicationClient,send_order_data
# 기본 저장 디렉토리
BASE_IMAGE_PATH = "images/caricatures"

def get_next_original_filename(index):
    """ original_1, original_2, ... 형식으로 저장하되 새로운 주문마다 덮어쓰기 """
    return os.path.join(BASE_IMAGE_PATH, f"original_{index}.jpg")

def get_next_sketch_filename(index):
    """ sketch_1, sketch_2, ... 형식으로 저장하되 새로운 주문마다 덮어쓰기 """
    return os.path.join(BASE_IMAGE_PATH, f"sketch_{index}.jpg")

def dodgeV2(x, y):
    return cv2.divide(x, 255 - y, scale=256)

def pencilsketch(inp_img):
    img_gray = cv2.cvtColor(inp_img, cv2.COLOR_BGR2GRAY)
    img_invert = cv2.bitwise_not(img_gray)
    img_smoothing = cv2.GaussianBlur(img_invert, (21, 21), sigmaX=0, sigmaY=0)
    final_img = dodgeV2(img_gray, img_smoothing)
    return final_img

def save_caricature_to_db(order_id, original_image_path, caricature_image_path):
    """ MySQL에 캐리커쳐 데이터 저장 """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO caricature (order_id, original_image_path, caricature_image_path) VALUES (%s, %s, %s)",
            (order_id, original_image_path, caricature_image_path)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        st.error(f"❌ 스케치 데이터 저장 실패: {e}")
    finally:
        cursor.close()
        conn.close()

def camera_page():
    st.title("📷 사진 촬영 및 스케치 변환")
    
    if "latest_order_ids" not in st.session_state or not st.session_state.latest_order_ids:
        st.warning("🚨 새로운 주문 정보가 없습니다! 이전 단계로 돌아가세요.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT order_id FROM orders WHERE order_id IN ({}) AND selected_caricature = 1
    """.format(','.join(['%s'] * len(st.session_state.latest_order_ids)))
    cursor.execute(query, st.session_state.latest_order_ids)
    caricature_orders = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    if not caricature_orders:
        st.session_state.page = "pickup_page"
        st.rerun()
        return

    st.session_state["caricature_order_ids"] = caricature_orders

    if "current_order_index" not in st.session_state:
        st.session_state["current_order_index"] = 0
        st.session_state["photo_taken"] = False

    current_order_index = st.session_state["current_order_index"]

    if current_order_index >= len(caricature_orders):
        st.session_state.page = "pickup_page"
        st.rerun()
        return

    current_order_id = caricature_orders[current_order_index]
    st.subheader(f"🧑‍🎨 주문 번호 {current_order_id} 고객의 사진을 촬영하세요!")

    # ✅ 주문이 변경될 때마다 카메라 입력을 강제 초기화
    if "prev_order_index" not in st.session_state or st.session_state["prev_order_index"] != current_order_index:
        st.session_state["photo_taken"] = False
        st.session_state["prev_order_index"] = current_order_index  # 주문 변경 감지

    # ✅ st.empty()를 사용하여 카메라 입력 강제 초기화
    camera_container = st.empty()
    image = camera_container.camera_input("📸 'Take Photo'를 눌러 사진을 촬영하세요!", key=f"camera_{current_order_index}")
    st.write("재촬영을 원하시면 'Clear photo'를 눌러 새로운 사진을 촬영하세요!")
    if image:
        try:
            original_path = get_next_original_filename(current_order_index + 1)
            input_img = Image.open(image)
            input_img.save(original_path)

            sketch_path = get_next_sketch_filename(current_order_index + 100)
            final_sketch = pencilsketch(np.array(input_img))
            Image.fromarray(final_sketch).save(sketch_path)

            save_caricature_to_db(current_order_id, original_path, sketch_path)

            st.session_state["photo_taken"] = True  # ✅ 사진이 저장된 후에만 True 설정
        except Exception as e:
            st.error(f"❌ 사진 저장 실패: {e}")
            st.session_state["photo_taken"] = False  # 🚀 저장 실패 시 False로 유지
     # ✅ "다음 주문 사진 촬영" 버튼을 사진 촬영 전까지 비활성화
    next_button_disabled = not st.session_state["photo_taken"]

    if next_button_disabled:
        st.warning("🚨 사진을 촬영해주세요!")
        
    # ✅ 다음 촬영으로 이동
    if current_order_index + 1 < len(caricature_orders):
        if st.button("➡️ 다음 주문 사진 촬영", disabled=next_button_disabled):
            st.session_state["current_order_index"] += 1
            st.session_state["photo_taken"] = False  # 다음 촬영을 위해 초기화
            camera_container.empty()  # 🚀 기존 카메라 입력 삭제
            st.rerun()
    else:
        if st.button("🚀 캐리커쳐 변환하기", disabled=next_button_disabled):
            ##통신
            send_order_data(st.session_state.order_info, original_path)
            st.session_state.page = "pickup_page"
            st.rerun()
