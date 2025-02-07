#5단계: 캐리커쳐 진행 여부 선택

import streamlit as st
from utils.db_connector import get_db_connection

def update_order_with_caricature(selected):
    """ MySQL에 캐리커쳐 선택 여부 업데이트 """
    if "order_id" not in st.session_state:
        st.error("🚨 주문 정보가 없습니다! 먼저 주문을 완료해주세요.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print(f"🔹 업데이트할 주문 ID: {st.session_state.order_id}, 선택 여부: {selected}")
        cursor.execute("UPDATE orders SET selected_caricature = %s WHERE order_id = %s",
                       (1 if selected else 0, st.session_state.order_id))  # ✅ True(1), False(0) 변환
        conn.commit()
        print("✅ 캐리커쳐 선택 여부 저장 완료!")

    except Exception as e:
        conn.rollback()
        st.error(f"❌ 캐리커쳐 선택 정보 저장 실패: {e}")

    finally:
        cursor.close()
        conn.close()

def caricature_page():
    st.title("로봇팔이 그려주는 당신의 캐리커쳐")

    # 버튼 2개 생성
    col1, col2 = st.columns(2)

    with col1:
        if st.button("사진 촬영"):
            update_order_with_caricature(True)  # 캐리커쳐 선택 (True)
            st.session_state.page = "camera_page"  # 카메라 캡쳐 페이지로 이동
            st.rerun()

    with col2:
        if st.button("캐리커쳐 선택 안함"):
            update_order_with_caricature(False)  # 캐리커쳐 선택 안함 (False)
            st.session_state.page = "pickup_page"  # 픽업 대기 안내 페이지로 이동
            st.rerun()
