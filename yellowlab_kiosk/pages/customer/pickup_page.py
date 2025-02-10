import streamlit as st
import qrcode
import io
from utils.db_connector import get_db_connection

# ✅ 내부 네트워크 IP 직접 지정
LOCAL_IP = "192.168.0.54"  # 📌 자신의 내부 IP 주소로 변경 필요
PORT = 8501  # ✅ Streamlit 실행 포트

def get_latest_orders():
    """ 최신 주문 목록 가져오기 (맛과 토핑 정보 포함) """
    if "latest_order_ids" not in st.session_state or not st.session_state.latest_order_ids:
        return []
    
    latest_order_ids = st.session_state.latest_order_ids  
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

def generate_qr_code(sketch_id):
    """스케치 번호를 기반으로 QR 코드 생성"""
    download_url = f"http://{LOCAL_IP}:{PORT}/?page=download&sketch_id={sketch_id}"  # ✅ sketch ID 기반으로 변경
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=2)  
    qr.add_data(download_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill="black", back_color="white")

    # ✅ QR 코드 디버깅 출력 추가
    print(f"🖼️ 스케치 {sketch_id} → QR 코드 다운로드 링크 생성됨: {download_url}")

    img_buffer = io.BytesIO()
    qr_img.save(img_buffer, format="PNG")
    return img_buffer.getvalue()

def pickup_page():
    st.title("🍦 아이스크림 픽업 안내")
    
    orders = get_latest_orders()

    if not orders:
        st.warning("🚨 픽업할 주문이 없습니다! 처음으로 돌아가세요.")
        return
    
    st.subheader("📜 픽업 대기 중인 주문 목록")
    
    # ✅ 주문 개수에 따라 컬럼 개수 동적으로 조절
    max_columns = 4  # 최대 컬럼 개수 설정
    num_orders = len(orders)
    num_columns = min(num_orders, max_columns)  # 주문 개수에 따라 컬럼 수 조정

    order_chunks = [orders[i:i+num_columns] for i in range(0, num_orders, num_columns)]

    sketch_index = 1  # ✅ 캐리커쳐를 선택한 주문의 스케치 번호
    for chunk in order_chunks:
        cols = st.columns(len(chunk))  # 현재 줄의 주문 수만큼 컬럼 생성
        for col, (order_id, flavor_name, topping_names, selected_caricature) in zip(cols, chunk):
            with col:
                st.markdown(f"**🆔 주문 번호: {order_id}**")
                st.write(f"🍦 **맛:** {flavor_name}")
                st.write(f"🍫 **토핑:** {topping_names if topping_names else '없음'}")
                
                # ✅ 캐리커쳐 선택 여부 확인
                if selected_caricature == 1:
                    st.write("🎨 **캐리커쳐 선택** ✅")
                    qr_code_image = generate_qr_code(sketch_index)
                    st.image(qr_code_image, caption="📱 QR 코드 스캔 후 스케치 다운로드", use_container_width=True)
                    sketch_index += 1  # ✅ 다음 스케치 번호 증가
                else:
                    st.write("🎨 **캐리커쳐 선택** ❌")

    if st.button("🔄 처음으로 돌아가기"):
        keys_to_keep = ["role"]  # 로그인 정보 유지
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]  # 특정 키만 삭제
        st.session_state.page = None
        st.rerun()
