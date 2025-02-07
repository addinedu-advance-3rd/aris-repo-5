import streamlit as st
import numpy as np
import os
from PIL import Image
import cv2
from utils.db_connector import get_db_connection

# 기본 저장 디렉토리
BASE_IMAGE_PATH = "images/caricatures"

def create_order_folder(order_id):
    """ 주문 번호별 폴더 생성 """
    order_folder = os.path.join(BASE_IMAGE_PATH, str(order_id))
    os.makedirs(order_folder, exist_ok=True)  # 폴더가 없으면 생성
    return order_folder

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
    
    # 최신 주문 목록 가져오기
    if "latest_order_ids" not in st.session_state or not st.session_state.latest_order_ids:
        st.warning("🚨 새로운 주문 정보가 없습니다! 이전 단계로 돌아가세요.")
        return
    
    latest_order_ids = st.session_state.latest_order_ids  # 최신 주문 ID 리스트
    
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT order_id FROM orders WHERE selected_caricature = 1 AND order_id IN ({}) ORDER BY order_id ASC".format(
        ','.join(['%s'] * len(latest_order_ids)))
    cursor.execute(query, latest_order_ids)
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    
    order_list = [order[0] for order in orders]
    
    if not order_list:
        st.warning("🚨 촬영할 주문이 없습니다! 이전 단계로 돌아가세요.")
        return
    
    if "current_order_index" not in st.session_state:
        st.session_state.current_order_index = 0
    
    current_order_id = order_list[st.session_state.current_order_index]
    
    st.subheader(f"🧑‍🎨 주문 번호 {current_order_id} 고객의 사진을 촬영하세요!")
    
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
            order_folder = create_order_folder(current_order_id)
            original_path = os.path.join(order_folder, "original.jpg")
            
            input_img = Image.open(st.session_state["captured_photo"])
            input_img.save(original_path)
            st.session_state["original_path"] = original_path  # 저장된 원본 이미지 경로 유지
            
            st.success("✅ 사진이 저장되었습니다! '스케치 변환하기' 버튼을 눌러주세요.")
        
        if st.button("🖌️ 스케치 변환하기"):
            if st.session_state["original_path"] is None:
                st.warning("🚨 먼저 '현재 사진 사용하기' 버튼을 눌러주세요!")
            else:
                input_img = Image.open(st.session_state["captured_photo"])
                final_sketch = pencilsketch(np.array(input_img))
                
                sketch_path = os.path.join(os.path.dirname(st.session_state["original_path"]), "sketch.jpg")
                Image.fromarray(final_sketch).save(sketch_path)
                
                save_caricature_to_db(current_order_id, st.session_state["original_path"], sketch_path)
                st.success("✅ 사진이 어떻게 변환될까요? 결과 페이지에서 확인해주세요! ^^")
                st.session_state["final_sketch"] = sketch_path
    
    if st.session_state.current_order_index + 1 < len(order_list):
        if st.session_state["final_sketch"]:
            if st.button("➡️ 다음 주문 사진 촬영"):
                st.session_state.current_order_index += 1
                st.session_state["captured_photo"] = None
                st.session_state["final_sketch"] = None
                st.session_state["original_path"] = None
                st.rerun()
    else:
        if st.session_state["final_sketch"]:
            if st.button("🖼️ 변환된 스케치 보기"):
                st.session_state.page = "result_page"
                st.rerun()
