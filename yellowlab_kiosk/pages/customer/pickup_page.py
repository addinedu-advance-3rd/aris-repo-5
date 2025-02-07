#7-2단계: 캐리커쳐 안함 시 픽업대기 안내

import streamlit as st

def pickup_page():
    st.title("로봇이 아이스크림 제조를 시작합니다! 🎉")

    if st.button("처음으로 돌아가기"):
        st.session_state.page = None
        st.rerun()
