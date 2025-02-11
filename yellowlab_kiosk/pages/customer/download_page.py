import streamlit as st
import os

# ✅ 스케치 파일 저장 경로
BASE_IMAGE_PATH = "images/caricatures"

def get_sketch_file_path(sketch_id):
    """ sketch_X.jpg 경로 반환 """
    file_path = os.path.join(BASE_IMAGE_PATH, f"sketch_{sketch_id}.jpg")

    # ✅ 파일 존재 여부 확인
    if os.path.exists(file_path):
        print(f"✅ 스케치 {sketch_id} → 파일 경로: {file_path}")
        return file_path
    else:
        print(f"🚨 스케치 {sketch_id} 파일 존재하지 않음: {file_path}")
        return None

def download_page():
    """ 스케치 다운로드 페이지 """
    st.subheader("📥 캐리커쳐 다운로드")

    query_params = st.query_params
    if "sketch_id" not in query_params:
        st.warning("🚨 다운로드할 스케치 ID가 없습니다! 이전 단계로 돌아가세요.")
        if st.button("🔙 픽업 페이지로 이동"):
            st.session_state.page = "pickup_page"
            st.rerun()
        return

    try:
        sketch_id = int(query_params["sketch_id"][0])  # ✅ 올바른 정수 변환
        file_path = get_sketch_file_path(sketch_id)

        if file_path:
            with open(file_path, "rb") as file:
                st.download_button(
                    label=f"🖼️ 스케치 {sketch_id} 다운로드",
                    data=file,
                    file_name=f"sketch_{sketch_id}.jpg",
                    mime="image/jpeg"
                )
        else:
            st.warning(f"🚨 스케치 {sketch_id} 파일을 찾을 수 없습니다.")
    except ValueError:
        st.warning("🚨 잘못된 스케치 ID 값입니다.")
