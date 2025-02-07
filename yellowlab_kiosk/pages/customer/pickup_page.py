import streamlit as st
from utils.db_connector import get_db_connection

def get_latest_orders():
    """ 최신 주문 목록 가져오기 (맛과 토핑 정보 포함) """
    if "latest_order_ids" not in st.session_state or not st.session_state.latest_order_ids:
        return []
    
    latest_order_ids = st.session_state.latest_order_ids  # 최신 주문 목록
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT o.order_id, f.name AS flavor_name, 
               GROUP_CONCAT(t.name SEPARATOR ', ') AS topping_names, 
               o.selected_caricature
        FROM orders o
        JOIN flavor f ON o.flavor_id = f.flavor_id
        LEFT JOIN order_topping ot ON o.order_id = ot.order_id
        LEFT JOIN topping t ON ot.topping_id = t.topping_id
        WHERE o.order_id IN ({})
        GROUP BY o.order_id, f.name, o.selected_caricature
    """.format(','.join(['%s'] * len(latest_order_ids)))
    cursor.execute(query, latest_order_ids)
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return orders

def pickup_page():
    st.title("🍦 아이스크림 픽업 안내")
    
    orders = get_latest_orders()
    
    if not orders:
        st.warning("🚨 픽업할 주문이 없습니다! 처음으로 돌아가세요.")
        return
    
    st.subheader("📜 픽업 대기 중인 주문 목록")
    
    for order_id, flavor_name, topping_names, selected_caricature in orders:
        status = "✅ 캐리커쳐 포함" if selected_caricature == 1 else "❌ 캐리커쳐 없음"
        toppings_display = topping_names if topping_names else "토핑 없음"
        st.write(f"🆔 주문 번호: {order_id} | 🍦 맛: {flavor_name} | 🍫 토핑: {toppings_display} | {status}")
    
    if st.button("🔄 처음으로 돌아가기"):
        keys_to_keep = ["role"]  # 로그인 정보 유지
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]  # 특정 키만 삭제
        st.session_state.page = None
        st.rerun()

