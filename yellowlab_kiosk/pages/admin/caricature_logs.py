import streamlit as st
import pandas as pd
from utils.db_connector import get_db_connection
import os
import shutil

# ✅ MySQL에서 캐리커쳐 데이터 가져오기
def fetch_caricature_logs():
    """MySQL에서 캐리커쳐 기록을 가져오는 함수"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.caricature_id, c.order_id, c.original_image_path, c.caricature_image_path, c.created_at
        FROM caricature c
        JOIN orders o ON c.order_id = o.order_id
        ORDER BY c.created_at DESC;
    """)
    caricatures = cursor.fetchall()

    conn.close()

    return [
        {"ID": c[0], "주문 ID": c[1], "원본 이미지": c[2], "캐리커쳐 이미지": c[3], "생성 날짜": c[4]}
        for c in caricatures
    ]

# ✅ MySQL에서 캐리커쳐 삭제
def delete_caricature(caricature_id, original_image_path, caricature_image_path, order_id):
    """MySQL에서 특정 캐리커쳐 데이터를 삭제하고, 로컬 이미지 파일 및 폴더도 제거"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # ✅ MySQL에서 캐리커쳐 데이터 삭제
        cursor.execute("DELETE FROM caricature WHERE caricature_id = %s", (caricature_id,))
        conn.commit()

        # ✅ 로컬 이미지 파일 삭제
        for image_path in [original_image_path, caricature_image_path]:
            if image_path and os.path.exists(image_path):  # 파일이 존재하면 삭제
                os.remove(image_path)
                st.success(f"🗑️ 파일 삭제 완료: {image_path}")

        # ✅ 폴더 삭제 (해당 주문의 폴더가 비었을 경우)
        order_folder = f"images/caricatures/{order_id}/"
        if os.path.exists(order_folder) and not os.listdir(order_folder):  # 폴더가 비었으면 삭제
            shutil.rmtree(order_folder)
            st.success(f"🗑️ 폴더 삭제 완료: {order_folder}")

        st.success(f"✅ 캐리커쳐 ID {caricature_id}가 삭제되었습니다.")
    except Exception as e:
        st.error(f"❌ 삭제 실패: {e}")
    finally:
        conn.close()

# ✅ Streamlit UI
def caricature_logs_page():
    st.title("🎨 캐리커쳐 기록 조회")
    st.write("저장된 캐리커쳐 데이터를 조회하고 관리할 수 있습니다.")

    # ✅ 데이터 가져오기
    data = fetch_caricature_logs()

    # ✅ 캐리커쳐 데이터 테이블 표시
    st.subheader("📜 저장된 캐리커쳐 목록")
    df_caricatures = pd.DataFrame(data)
    st.dataframe(df_caricatures, use_container_width=True)

    # ✅ 특정 주문의 캐리커쳐 이미지 확인
    st.subheader("🔍 특정 캐리커쳐 조회")
    order_ids = [c["주문 ID"] for c in data]
    selected_order = st.selectbox("조회할 주문 ID 선택", order_ids)

    # ✅ 선택된 주문의 캐리커쳐 이미지 표시
    selected_caricature = next((c for c in data if c["주문 ID"] == selected_order), None)

    if selected_caricature:
        st.write(f"📸 주문 ID: {selected_order}")

        # ✅ 원본 이미지 표시
        if os.path.exists(selected_caricature["원본 이미지"]):
            st.image(selected_caricature["원본 이미지"], caption="원본 이미지", use_column_width=True)
        else:
            st.warning("⚠️ 원본 이미지 파일을 찾을 수 없습니다.")

        # ✅ 캐리커쳐 이미지 표시
        if os.path.exists(selected_caricature["캐리커쳐 이미지"]):
            st.image(selected_caricature["캐리커쳐 이미지"], caption="캐리커쳐 이미지", use_column_width=True)
        else:
            st.warning("⚠️ 캐리커쳐 이미지 파일을 찾을 수 없습니다.")

    st.divider()

    # ✅ 캐리커쳐 삭제 기능
    st.subheader("🗑️ 캐리커쳐 삭제")
    delete_caricature_id = st.number_input("삭제할 캐리커쳐 ID 입력", min_value=1, step=1)

    if st.button("🗑️ 삭제하기"):
        # ✅ 삭제할 캐리커쳐의 이미지 경로 및 주문 ID 가져오기
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT original_image_path, caricature_image_path, order_id FROM caricature WHERE caricature_id = %s", (delete_caricature_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            delete_caricature(delete_caricature_id, result[0], result[1], result[2])  # ✅ order_id 추가
        else:
            st.error("❌ 해당 ID의 캐리커쳐를 찾을 수 없습니다.")

        st.rerun()

    st.divider()

    # ✅ 대시보드로 돌아가는 버튼
    if st.button("⬅️ 대시보드로 돌아가기"):
        st.session_state.page = "dashboard"
        st.rerun()
