import streamlit as st
import pandas as pd
from utils.db_connector import get_db_connection

# ✅ MySQL에서 주문 데이터 가져오기
def fetch_orders():
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ 주문 목록 가져오기
    cursor.execute("""
        SELECT o.order_id, f.name AS flavor, o.total_price, o.selected_caricature, o.created_at
        FROM orders o
        JOIN flavor f ON o.flavor_id = f.flavor_id
        ORDER BY o.created_at DESC;
    """)
    orders = cursor.fetchall()

    # ✅ 토핑 정보 가져오기
    cursor.execute("""
        SELECT ot.order_id, t.name 
        FROM order_topping ot
        JOIN topping t ON ot.topping_id = t.topping_id;
    """)
    toppings = cursor.fetchall()

    conn.close()

    # ✅ 주문별 토핑을 정리
    toppings_dict = {}
    for order_id, topping in toppings:
        if order_id not in toppings_dict:
            toppings_dict[order_id] = []
        toppings_dict[order_id].append(topping)

    # ✅ 최종 데이터 정리
    orders_data = []
    for order in orders:
        order_id, flavor, total_price, selected_caricature, created_at = order
        orders_data.append({
            "주문 ID": order_id,
            "맛": flavor,
            "토핑": ", ".join(toppings_dict.get(order_id, [])),  # 토핑 리스트
            "가격": total_price,
            "캐리커쳐": "✅" if selected_caricature else "❌",
            "주문 시간": created_at.strftime("%Y-%m-%d %H:%M:%S")  # 시간 포맷 변경
        })

    return orders_data

# ✅ 주문 삭제 기능
def delete_order(order_id):
    """주문을 삭제하는 함수"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # ✅ 관련 테이블 데이터 삭제 (토핑 → 캐리커쳐 → 주문)
        cursor.execute("DELETE FROM order_topping WHERE order_id = %s", (order_id,))
        cursor.execute("DELETE FROM caricature WHERE order_id = %s", (order_id,))
        cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
        conn.commit()
        st.success(f"✅ 주문 {order_id}가 삭제되었습니다.")
    except Exception as e:
        st.error(f"❌ 주문 삭제 실패: {e}")
    finally:
        cursor.close()
        conn.close()

# ✅ Streamlit UI
def orders_page():
    st.title("📜 주문 관리")
    st.write("모든 주문을 확인하고, 필요하면 삭제할 수 있습니다.")

    # ✅ MySQL에서 주문 데이터 가져오기
    orders = fetch_orders()
    df_orders = pd.DataFrame(orders)

    # ✅ 주문 목록 테이블 표시
    st.subheader("📝 주문 목록")
    st.dataframe(df_orders, use_container_width=True)

    # ✅ 주문 선택 및 삭제 기능
    st.subheader("🗑️ 주문 삭제")
    order_ids = [order["주문 ID"] for order in orders]
    selected_order = st.selectbox("삭제할 주문을 선택하세요:", order_ids if order_ids else ["삭제할 주문 없음"])

    if st.button("🗑️ 삭제하기") and selected_order != "삭제할 주문 없음":
        delete_order(selected_order)
        st.rerun()

    # ✅ 대시보드로 돌아가는 버튼
    if st.button("⬅️ 대시보드로 돌아가기"):
        st.session_state.page = "dashboard"
        st.rerun()
