#7-1단계: 캐리커쳐 진행 시 픽업대기 안내

import streamlit as st
import os
from utils.db_connector import get_db_connection  # ✅ MySQL 연결 추가

def get_caricature_from_db(order_id):
    """ MySQL에서 캐리커쳐 데이터 불러오기 """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT original_image_path, caricature_image_path FROM caricature WHERE order_id = %s", (order_id,))
        result = cursor.fetchone()
        if result:
            return result[0], result[1]  # (원본 이미지 경로, 스케치 이미지 경로)
        return None, None
    except Exception as e:
        st.error(f"❌ 캐리커쳐 데이터 불러오기 실패: {e}")
        return None, None
    finally:
        cursor.close()
        conn.close()

def result_page():
    st.title("로봇이 아이스크림 제조를 시작합니다! 🎉")

    # ✅ MySQL에서 캐리커쳐 데이터 불러오기
    if "order_id" in st.session_state:
        original_img, sketch_img = get_caricature_from_db(st.session_state.order_id)
        
        if sketch_img and os.path.exists(sketch_img):  # 스케치 이미지 존재 확인
            st.image(os.path.join(".", sketch_img), caption="최종 선택한 스케치", use_column_width=True)
            st.write("아이스크림 제조를 시작합니다! 🚀")
        else:
            st.warning("❗ 스케치 이미지가 없습니다. 이전 단계로 돌아가세요.")
            if st.button("돌아가기"):
                st.session_state.page = "camera_page"
                st.rerun()
    else:
        st.warning("❗ 주문 정보가 없습니다. 처음부터 다시 진행해주세요.")
    
    # ✅ 처음으로 돌아가기 버튼
    if st.button("처음으로 돌아가기"):
        # ✅ 주문 관련 데이터만 초기화 (로그인 정보 유지)
        keys_to_keep = ["role"]  # 로그인 정보 유지
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]  # 특정 키만 삭제

        # ✅ start_page로 이동
        st.session_state.page = None
        st.rerun()