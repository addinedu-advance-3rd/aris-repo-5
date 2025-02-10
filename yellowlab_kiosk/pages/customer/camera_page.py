#6단계: 카메라 캡쳐 및 스케치 변환

import streamlit as st
import numpy as np
import os
from PIL import Image
import cv2
from utils.db_connector import get_db_connection  # ✅ MySQL 연결 추가
from utils.communication import send_order_data


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
        st.success("✅ 스케치 이미지가 MySQL에 저장되었습니다!")

    except Exception as e:
        conn.rollback()
        st.error(f"❌ 스케치 데이터 저장 실패: {e}")
    
    finally:
        cursor.close()
        conn.close()

def camera_page():
    st.title("📷 사진 촬영 및 스케치 변환")

    if "photos" not in st.session_state:
        st.session_state["photos"] = []
        st.session_state["selected_photo"] = None
        st.session_state["final_sketch"] = None

    image = st.camera_input("📸 사진을 촬영하세요!")

    if image:
        if len(st.session_state["photos"]) < 3:
            st.session_state["photos"].append(image)
            st.success(f"✅ 사진이 저장되었습니다! 현재 {len(st.session_state['photos'])}/3")
        else:
            st.warning("⚠️ 최대 3장의 사진만 촬영할 수 있습니다!")
    
    if st.session_state["photos"]:
        st.subheader("📸 촬영된 사진")
        cols = st.columns(3)
        for i, photo in enumerate(st.session_state["photos"]):
            with cols[i]:
                st.image(photo, use_column_width=True, caption=f"사진 {i + 1}")
        
        st.session_state["selected_photo"] = st.radio(
            "🎨 스케치 변환할 사진을 선택하세요:",
            options=list(range(len(st.session_state["photos"]))),
            format_func=lambda x: f"사진 {x + 1}",
        )
        image_path = "/home/addinedu/aris/aris-repo-5_통신/yellowlab_kiosk/images/caricatures/10"
        ########################################    
        send_order_data(st.session_state.order_info,image_path,len(st.session_state.order_info) )
        #########################################
    if st.button("🖌️ 스케치 변환하기"):
        if st.session_state["selected_photo"] is not None:
            selected_index = st.session_state["selected_photo"]
            selected_image = st.session_state["photos"][selected_index]

            input_img = Image.open(selected_image)
            final_sketch = pencilsketch(np.array(input_img))

            # ✅ 주문 번호별 폴더 생성
            order_id = st.session_state.order_id
            order_folder = create_order_folder(order_id)

            # ✅ 개별 폴더 내에 파일 저장
            original_path = os.path.join(order_folder, "original.jpg")
            sketch_path = os.path.join(order_folder, "sketch.jpg")

            input_img.save(original_path)
            Image.fromarray(final_sketch).save(sketch_path)

            save_caricature_to_db(order_id, original_path, sketch_path)

            st.session_state["final_sketch"] = sketch_path

            st.success(f"✅ 사진 {selected_index + 1}이(가) 스케치로 변환되었습니다!")
            one, two = st.columns(2)
            with one:
                st.write("📸 **원본 사진**")
                st.image(original_path, use_column_width=True)
            with two:
                st.write("🖼️ **스케치 사진**")
                st.image(sketch_path, use_column_width=True)

        else:
            st.warning("⚠️ 변환할 사진을 선택하세요!")

    if st.button("🍦 아이스크림 제조 시작"):
        if st.session_state["final_sketch"] is not None:
            st.session_state.page = "result_page"
            st.rerun()
        else:
            st.warning("⚠️ 스케치 변환을 완료한 후 진행해주세요!")
