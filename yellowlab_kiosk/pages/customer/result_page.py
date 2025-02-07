import streamlit as st
from utils.db_connector import get_db_connection

def get_latest_caricatures():
    """ 최신 주문의 캐리커쳐 변환 결과 가져오기 (맛과 토핑 정보 포함) """
    if "latest_order_ids" not in st.session_state or not st.session_state.latest_order_ids:
        return []
    
    latest_order_ids = st.session_state.latest_order_ids  # 최신 주문 목록
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT o.order_id, f.name AS flavor_name, 
               GROUP_CONCAT(t.name SEPARATOR ', ') AS topping_names, 
               c.original_image_path, c.caricature_image_path
        FROM caricature c
        JOIN orders o ON c.order_id = o.order_id
        JOIN flavor f ON o.flavor_id = f.flavor_id
        LEFT JOIN order_topping ot ON o.order_id = ot.order_id
        LEFT JOIN topping t ON ot.topping_id = t.topping_id
        WHERE o.order_id IN ({})
        GROUP BY o.order_id, f.name, c.original_image_path, c.caricature_image_path
    """.format(','.join(['%s'] * len(latest_order_ids)))
    cursor.execute(query, latest_order_ids)
    caricatures = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return caricatures

def result_page():
    st.title("🎨 캐리커쳐 변환 결과")
    
    caricatures = get_latest_caricatures()
    
    if not caricatures:
        st.warning("🚨 변환된 캐리커쳐가 없습니다! 이전 단계로 돌아가세요.")
        return
    
    st.subheader("🖼️ 캐리커쳐 변환 결과를 확인하세요")
    
    selected_order = st.selectbox(
        "📜 주문을 선택하세요:",
        options=list(set(c[0] for c in caricatures)),  # 중복 제거
        format_func=lambda x: f"주문 {x}"
    )
    
    selected_caricature = next((c for c in caricatures if c[0] == selected_order), None)
    
    if selected_caricature:
        order_id, flavor_name, topping_names, original_path, sketch_path = selected_caricature
        
        toppings_display = topping_names if topping_names else "토핑 없음"
        st.subheader(f"📝 주문 번호 {order_id} | 🍦 맛: {flavor_name} | 🍫 토핑: {toppings_display}")
        
        cols = st.columns(2)
        with cols[0]:
            st.write("📸 **원본 사진**")
            st.image(original_path, use_container_width=True)
        with cols[1]:
            st.write("🎨 **스케치 변환 결과**")
            st.image(sketch_path, use_container_width=True)
    
    if st.button("🍦 주문 마치기 및 픽업 안내로 이동"):
        st.session_state.page = "pickup_page"
        st.rerun()
