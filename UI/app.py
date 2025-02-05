#1단계: 로그인 페이지

import streamlit as st
from pages.customer.start_page import start_page
from pages.customer.menu_page import menu_page  # 메뉴 선택 페이지
from pages.customer.cart_page import cart_page  # 주문 확인 페이지
from pages.customer.caricature_page import caricature_page  # 캐리커쳐 선택 페이지
from pages.customer.camera_page import camera_page  # 카메라 캡쳐 페이지
from pages.customer.result_page import result_page
from pages.customer.pickup_page import pickup_page  # 픽업 페이지(캐리커쳐 선택 안했을 때)
from utils.communication import get_caricature_result,send_image_to_server
# Initialize session state
if "role" not in st.session_state:
    st.session_state.role = None

if "page" not in st.session_state:
    st.session_state.page = None

ROLES = [None, "Customer Service", "Admin"]

# Login Page
def login_page():
    st.header("Log in")
    st.title("로그인")
    role = st.selectbox("Choose your role", ROLES)
    password = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        if role == "Customer Service" and password == "1234":
            st.session_state.role = role
            st.success("Customer Service로 로그인 성공!")
            st.rerun()
        elif password == "admin123" and password == "admin123":
            st.session_state.role = role
            st.success("Admin으로 로그인 성공!")
            st.experimental_rerun()
        else:
            st.error("잘못된 사용자 이름 또는 비밀번호입니다.")
def logout():
    st.session_state.role = None
    st.rerun()

role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

# 분기 처리
if st.session_state.role == "Customer Service":
    if st.session_state.page == "menu":
        menu_page()  # 메뉴 선택 페이지로 이동
    elif st.session_state.page == "cart_page":
        cart_page()  # 주문 확인 페이지로 이동
    elif st.session_state.page == "caricature_page":
        caricature_page()  # 캐리커쳐 선택 페이지로 이동
    elif st.session_state.page == "camera_page":
        camera_page()  # 카메라 캡쳐 페이지로 이동
    elif st.session_state.page == "result_page":
        result_page()  # 스케치 변환 결과 및 픽업대기 안내 페이지로 이동
    elif st.session_state.page == "pickup_page":
        pickup_page()  # 캐리커쳐 선택 안함 후 픽업대기 안내 페이지로 이동
    elif st.session_state.page is None:
        start_page()  # 시작 화면
elif st.session_state.role == "admin":
    st.write("관리자 페이지 시작")
    # 여기서 관리자 페이지 코드를 추가
else:
    login_page()
