#2단계: 시작화면

import streamlit as st

def start_page():
    st.title("주문 시작")
    st.header("환영합니다! 주문을 시작하려면 아래 버튼을 클릭하세요.")
    
    # "주문 시작" 버튼 추가
    if st.button("주문 시작"):
        # 메뉴 선택 페이지로 이동
        st.session_state.page = "menu"
        st.rerun()