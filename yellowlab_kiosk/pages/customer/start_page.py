#2단계: 시작화면

import streamlit as st

def start_page():
    st.title("📜주문 시작")
    st.header("🤗환영합니다!")
    st.subheader("👇아래 버튼을 클릭하여 주문을 시작하세요")
    
    # "주문 시작" 버튼 추가
    if st.button("▶ 주문 시작 ◀", use_container_width=True):
        # 메뉴 선택 페이지로 이동
        st.session_state.page = "menu"
        st.rerun()
    
    # if st.button("로그인 페이지"):
    #     st.session_state.clear()
    #     st.rerun()