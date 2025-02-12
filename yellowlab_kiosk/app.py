#1단계: 로그인 페이지

import streamlit as st

from urllib.parse import urlparse, parse_qs

from pages.customer.start_page import start_page
from pages.customer.menu_page import menu_page  # 메뉴 선택 페이지
from pages.customer.cart_page import cart_page  # 주문 확인 페이지
from pages.customer.caricature_page import caricature_page  # 캐리커쳐 선택 페이지
from pages.customer.camera_page import camera_page  # 카메라 캡쳐 페이지
from pages.customer.pickup_page import pickup_page  # 픽업 페이지(캐리커쳐 선택 안했을 때)
from pages.customer.download_page import download_page  # 다운로드 페이지 추가

from pages.admin.dashboard import dashboard_page # 관리자 대시보드 페이지
from pages.admin.orders import orders_page # 관리자 주문관리 페이지
from pages.admin.inventory import inventory_page # 관리자 재고관리 페이지
from pages.admin.menu_management import menu_management_page # 관리자 메뉴관리 페이지

# Initialize session state
if "role" not in st.session_state:
    st.session_state.role = None

if "page" not in st.session_state:
    st.session_state.page = None

ROLES = [None, "Customer Service", "Admin"]

# URL 파라미터 처리
query_params = st.query_params
if "sketch_id" in query_params:
    try:
        sketch_id = int(query_params["sketch_id"][0])  # ✅ 정수 변환
        st.session_state.page = "download"
        
        # ✅ 로그인 체크 없이 download_page 실행
        if st.session_state.page == "download":
            download_page()
            st.stop()

        print(f"🔗 URL에서 추출한 sketch_id: {sketch_id}")
    except (ValueError, KeyError) as e:
        st.warning(f"🚨 잘못된 sketch_id 값이 감지되었습니다: {e}")


# Login Page
def login_page():
    st.header("Log in")
    st.title("로그인")
    role = st.selectbox("Choose your role", ROLES)
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        if role == "Customer Service" and password == "1234":
            st.session_state.role = role
            st.success("✅ Customer Service로 로그인 성공!")
            st.rerun()
        elif role == "Admin" and password == "admin123":  # ✅ 관리자 로그인 조건 수정
            st.session_state.role = role
            st.success("✅ Admin으로 로그인 성공!")
            st.rerun()
        else:
            st.error("❌ 잘못된 사용자 이름 또는 비밀번호입니다.")
def logout():
    st.session_state.role = None
    st.rerun()

role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

# 분기 처리
# ✅ 다운로드 페이지는 로그인 없이 접근 가능하도록 예외 처리
if st.session_state.page == "download":
    download_page()

elif st.session_state.role == "Customer Service":
    if st.session_state.page == "menu":
        menu_page()
    elif st.session_state.page == "cart_page":
        cart_page()
    elif st.session_state.page == "caricature_page":
        caricature_page()
    elif st.session_state.page == "camera_page":
        camera_page()
    elif st.session_state.page == "pickup_page":
        pickup_page()
    elif st.session_state.page is None:
        start_page()

elif st.session_state.role == "Admin":
    if st.session_state.page == "dashboard":
        dashboard_page()
    elif st.session_state.page == "orders":
        orders_page()  # 주문 관리 페이지 이동
    elif st.session_state.page == "inventory":  # 재고 관리 페이지 이동
        inventory_page()
    elif st.session_state.page == "menu_management":  # 메뉴 관리 페이지 이동
        menu_management_page()
    else:
        dashboard_page()

else:
    login_page()
