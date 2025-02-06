import streamlit as st
import pandas as pd
from utils.db_connector import get_db_connection

# ✅ MySQL에서 데이터 가져오기
def fetch_dashboard_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ 오늘의 총 주문 수
    cursor.execute("SELECT COUNT(*) FROM orders WHERE DATE(created_at) = CURDATE();")
    total_orders = cursor.fetchone()[0]

    # ✅ 오늘의 총 매출액
    cursor.execute("SELECT COALESCE(SUM(total_price), 0) FROM orders WHERE DATE(created_at) = CURDATE();")
    total_revenue = cursor.fetchone()[0]

    # ✅ 캐리커쳐 선택 비율
    cursor.execute("SELECT COUNT(*) FROM orders WHERE selected_caricature = 1 AND DATE(created_at) = CURDATE();")
    caricature_count = cursor.fetchone()[0]
    caricature_ratio = (caricature_count / total_orders * 100) if total_orders > 0 else 0

    # ✅ 최근 주문 내역 (최신 5개)
    cursor.execute("""
        SELECT order_id, flavor_id, total_price, created_at 
        FROM orders 
        ORDER BY created_at DESC 
        LIMIT 5;
    """)
    recent_orders = cursor.fetchall()

    # ✅ 아이스크림 & 토핑 재고 확인
    cursor.execute("SELECT name, stock_quantity FROM flavor;")
    flavors_stock = cursor.fetchall()
    
    cursor.execute("SELECT name, stock_quantity FROM topping;")
    toppings_stock = cursor.fetchall()

    conn.close()

    return {
        "total_orders": total_orders,
        "total_revenue": int(total_revenue),  # Decimal → int 변환
        "caricature_ratio": round(caricature_ratio, 2),  # 소수점 2자리
        "recent_orders": recent_orders,
        "flavors_stock": flavors_stock,
        "toppings_stock": toppings_stock
    }

# ✅ Streamlit UI
def dashboard_page():
    st.title("📊 관리자 대시보드")
    st.write("키오스크 주문 및 캐리커쳐 통계를 한눈에 확인하세요.")

    # ✅ 데이터 가져오기
    data = fetch_dashboard_data()

    # ✅ 1. 주요 통계 정보 (오늘의 주문, 매출, 캐리커쳐 비율)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="📦 총 주문 수", value=f"{data['total_orders']} 건")
    col2.metric(label="💰 총 매출액", value=f"{data['total_revenue']} 원")
    col3.metric(label="🎨 캐리커쳐 선택률", value=f"{data['caricature_ratio']} %")

    st.divider()  # 구분선

    # ✅ 2. 최근 주문 내역 테이블
    st.subheader("📜 최근 주문 내역")
    if data["recent_orders"]:
        df_orders = pd.DataFrame(
            data["recent_orders"],
            columns=["주문 ID", "맛 ID", "총 가격", "주문 시간"]
        )
        df_orders["주문 시간"] = df_orders["주문 시간"].astype(str)  # 시간 문자열 변환
        st.dataframe(df_orders)
    else:
        st.write("최근 주문 내역이 없습니다.")

    st.divider()

    # ✅ 3. 재고 현황
    st.subheader("📦 재고 현황")
    col1, col2 = st.columns(2)

    # ✅ 아이스크림 맛 재고
    with col1:
        st.write("🍦 **아이스크림 재고**")
        df_flavors = pd.DataFrame(data["flavors_stock"], columns=["맛", "재고"])
        st.dataframe(df_flavors)

    # ✅ 토핑 재고
    with col2:
        st.write("🍫 **토핑 재고**")
        df_toppings = pd.DataFrame(data["toppings_stock"], columns=["토핑", "재고"])
        st.dataframe(df_toppings)

    st.divider()

    # ✅ 4. 빠른 이동 버튼
    col1, col2, col3, col4, col5 = st.columns(5)
    if col1.button("📜 주문 관리"):
        st.session_state.page = "orders"
        st.rerun()
    if col2.button("📦 재고 관리"):
        st.session_state.page = "inventory"
        st.rerun()
    if col3.button("🍦 메뉴 관리"):
        st.session_state.page = "menu_management"
        st.rerun()
    if col4.button("🎨 캐리커쳐 기록 관리"):
        st.session_state.page = "caricature_logs"
        st.rerun()
    if col5.button("🚪 로그아웃"):
        st.session_state.role = None
        st.session_state.page = None
        st.rerun()
