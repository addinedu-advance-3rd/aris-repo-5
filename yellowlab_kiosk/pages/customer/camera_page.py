import streamlit as st
import numpy as np
import os
from PIL import Image
import cv2
from utils.db_connector import get_db_connection

# 기본 저장 디렉토리
BASE_IMAGE_PATH = "images/caricatures"

def reset_old_sketches():
    """ 기존 스케치 파일 삭제하여 새로운 주문 팀의 스케치 저장 전에 초기화 """
    folder = BASE_IMAGE_PATH
    for file in os.listdir(folder):
        if file.startswith("sketch_") and file.endswith(".jpg"):
            os.remove(os.path.join(folder, file))

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
    
    if "current_team_size" not in st.session_state:
        st.session_state.current_team_size = None
    
    if "current_order_index" not in st.session_state:
        st.session_state.current_order_index = 0  # 초기화 추가
    
    if "latest_order_ids" not in st.session_state or not st.session_state.latest_order_ids:
        st.warning("🚨 새로운 주문 정보가 없습니다! 이전 단계로 돌아가세요.")
        return
    
    latest_order_ids = st.session_state.latest_order_ids
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT order_id FROM orders WHERE selected_caricature = 1 AND order_id IN ({}) ORDER BY order_id ASC".format(
        ','.join(['%s'] * len(latest_order_ids)))
    cursor.execute(query, latest_order_ids)
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    
    order_list = [order[0] for order in orders]
    st.session_state.current_team_size = len(order_list)
    
    if not order_list:
        st.warning("🚨 촬영할 주문이 없습니다! 이전 단계로 돌아가세요.")
        return
    
    current_order_index = st.session_state.current_order_index
    current_order_id = order_list[current_order_index]
    
    st.subheader(f"🧑‍🎨 주문 번호 {current_order_id} 고객의 사진을 촬영하세요!")
    
    # 촬영 데이터 초기화
    if "captured_photo" not in st.session_state:
        st.session_state["captured_photo"] = None
    if "final_sketch" not in st.session_state:
        st.session_state["final_sketch"] = None
    if "original_path" not in st.session_state:
        st.session_state["original_path"] = None
    
    image = st.camera_input("📸 사진을 촬영하세요!")
    
    if image:
        st.session_state["captured_photo"] = image
        st.success("✅ 사진이 캡처되었습니다! '현재 사진 사용하기'를 눌러주세요.")
    
    if st.session_state["captured_photo"]:
        st.image(st.session_state["captured_photo"], use_container_width=True, caption="📸 현재 캡처된 사진")
        
        if st.button("🚀 현재 사진 사용하기"):
            original_path = get_next_original_filename(current_order_index + 1)
            input_img = Image.open(st.session_state["captured_photo"])
            input_img.save(original_path)
            st.session_state["original_path"] = original_path
            st.success(f"✅ 사진이 저장되었습니다! 파일명: {os.path.basename(original_path)}")
        
    if st.session_state.get("original_path") and os.path.exists(st.session_state["original_path"]):
        if st.button("🖌️ 스케치 변환하기"):
            sketch_path = get_next_sketch_filename(current_order_index + 1)
            input_img = Image.open(st.session_state["original_path"])
            final_sketch = pencilsketch(np.array(input_img))
            Image.fromarray(final_sketch).save(sketch_path)
            save_caricature_to_db(current_order_id, st.session_state["original_path"], sketch_path)
            st.success(f"✅ 사진이 변환되었습니다! 파일명: {os.path.basename(sketch_path)}")
            st.session_state["final_sketch"] = sketch_path
    
    if current_order_index + 1 < len(order_list):
        if st.session_state["final_sketch"]:
            if st.button("➡️ 다음 주문 사진 촬영"):
                st.session_state.current_order_index += 1
                st.session_state["captured_photo"] = None
                st.session_state["final_sketch"] = None
                st.session_state["original_path"] = None

                st.rerun()
        st.rerun()
    else:
        if st.session_state["final_sketch"]:
            if st.button("🖼️ 변환된 스케치 보기"):
                st.session_state.page = "result_page"
