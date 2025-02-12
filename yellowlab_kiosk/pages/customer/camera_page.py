import streamlit as st
import os
from PIL import Image
import cv2
import time
from utils.db_connector import get_db_connection
from utils.communication import CommunicationClient,send_order_data

# 기본 저장 디렉토리
BASE_IMAGE_PATH = "images/caricatures"
os.makedirs(BASE_IMAGE_PATH, exist_ok=True)  # ✅ 디렉토리가 없으면 생성

def get_next_original_filename(index):
    """ original_1, original_2, ... 형식으로 저장하되 새로운 주문마다 덮어쓰기 """
    return os.path.join(BASE_IMAGE_PATH, f"original_{index}.jpg")

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
    st.header("📷 사진 촬영 및 스케치 변환")
    
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

    # ✅ 초기 상태 설정
    if "photo_taken" not in st.session_state:
        st.session_state.photo_taken = False
    if "camera_active" not in st.session_state:
        st.session_state.camera_active = False
    if "captured_frame" not in st.session_state:
        st.session_state.captured_frame = None

    # ✅ "촬영 시작" 또는 "재촬영" 버튼 설정
    button_label = "📸 촬영 시작" if not st.session_state.photo_taken else "🔄 재촬영"
    button_disabled = st.session_state.camera_active  # 촬영 중에는 버튼 비활성화
    if st.button(button_label, disabled=button_disabled):
        st.session_state.camera_active = True
        st.session_state.photo_taken = False
        st.session_state.captured_frame = None  # 기존 촬영된 이미지 초기화
        st.rerun()

    # ✅ 타이머 기반 자동 촬영 실행
    if st.session_state.camera_active:
        cap = cv2.VideoCapture(0)
        image_placeholder = st.empty()
        timer_placeholder = st.empty()  # 타이머 표시

        TIMER_SECONDS = 5
        start_time = time.time()

        while time.time() - start_time < TIMER_SECONDS:
            ret, frame = cap.read()
            if not ret:
                st.error("🚨 카메라에서 영상을 가져올 수 없습니다.")
                cap.release()
                st.session_state.camera_active = False
                st.rerun()

            remaining_time = TIMER_SECONDS - int(time.time() - start_time)
            timer_placeholder.markdown(f"⏳ **{remaining_time} 초 후 촬영...**")

            image_placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption="📷 실시간 카메라", use_container_width=True)
            time.sleep(0.01)  # UI 부드럽게 갱신
        
        ret, frame = cap.read()
        cap.release()
        timer_placeholder.empty()  # 타이머 표시 제거

        if ret:
            st.session_state.photo_taken = True
            st.session_state.captured_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            st.session_state.camera_active = False  # 촬영 종료
            st.rerun()

    if st.session_state.photo_taken and st.session_state.captured_frame is not None:
        st.image(st.session_state.captured_frame, caption="📸 촬영된 사진", use_container_width=True)
        try:
            original_path = get_next_original_filename(current_order_index + 1)
            img = Image.fromarray(st.session_state.captured_frame)
            img.save(original_path)  # ✅ 원본 사진 저장

            sketch_path = os.path.join(BASE_IMAGE_PATH, f"sketch_{current_order_index + 1}.jpg")
            
            save_caricature_to_db(current_order_id, original_path, sketch_path)  # ✅ MySQL 저장
        
        except Exception as e:
            st.error(f"❌ 사진 저장 실패: {e}")
            st.session_state["photo_taken"] = False  # 🚀 저장 실패 시 False로 유지

    # ✅ "다음 주문 사진 촬영" 버튼을 사진 촬영 전까지 비활성화
    next_button_disabled = not st.session_state["photo_taken"]

    if next_button_disabled:
        st.warning("🚨 촬영 시작 버튼을 눌러 사진을 촬영해주세요!")
        
    # ✅ 다음 촬영으로 이동
    if current_order_index + 1 < len(caricature_orders):
        if st.button("➡️ 다음 주문 사진 촬영", disabled=next_button_disabled):
            st.session_state["current_order_index"] += 1
            st.session_state["photo_taken"] = False  # 다음 촬영을 위해 초기화
            st.session_state["captured_frame"] = None  # 🚀 기존 카메라 입력 삭제
            st.rerun()
    else:
        if st.button("🚀 캐리커쳐 변환하기", disabled=next_button_disabled):
            ##통신
            send_order_data(st.session_state.order_info, original_path)
            st.session_state.page = "pickup_page"
            st.rerun()
