#5단계: 캐리커쳐 진행 여부 선택

import streamlit as st

def caricature_page():
    st.title("로봇팔이 그려주는 당신의 캐리커쳐")
    
    # 버튼 2개 생성
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("사진 촬영"):
            st.session_state.page = "camera_page"  # 카메라 캡쳐 페이지로 이동
            st.rerun()
    
    with col2:
        if st.button("캐리커쳐 선택 안함"):
            st.session_state.page = "pickup_page"  # 픽업 대기 안내 페이지로 이동
            st.rerun()

