import streamlit as st
import qrcode
import io
from utils.db_connector import get_db_connection
import socket

def get_local_ip():
    """ 현재 실행 중인 컴퓨터의 내부 IP 주소를 올바르게 감지 """
    try:
        # ✅ 올바른 내부 IP 가져오기 (네트워크 인터페이스 확인)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # ✅ Google DNS에 연결하여 네트워크 인터페이스 확인
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"🚨 내부 IP를 감지할 수 없음: {e}")
        return "127.0.0.1"  # 감지 실패 시 기본값 반환

# ✅ 내부 네트워크 IP 자동 감지
LOCAL_IP = get_local_ip()
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
    """스케치 ID를 기반으로 QR 코드 생성 (자동 감지된 IP 사용)"""
    download_url = f"http://{LOCAL_IP}:{PORT}/?page=download&sketch_id={sketch_id}"
    print(f"🖼️ QR 코드 생성된 다운로드 URL: {download_url}")  # ✅ 디버깅용 로그 추가
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=2)  
    qr.add_data(download_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill="black", back_color="white")

    img_buffer = io.BytesIO()
    qr_img.save(img_buffer, format="PNG")
    return img_buffer.getvalue()
def pickup_page():
    st.header("🍦 아이스크림을 픽업해주세요!")
    
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
                with st.container(border=True):
                    st.markdown(f"""<p style='font-size: 20px; font-weight: bold; color: #007BFF;'>🆔 주문 번호: {order_id}</p>""", unsafe_allow_html=True)
                    st.write(f"🍦 **맛:** {flavor_name} | 🍫 **토핑:** {topping_names if topping_names else '없음'}")
                               
                    # ✅ 캐리커쳐 선택 여부 확인
                    if selected_caricature == 1:
                        st.write("🎨 **캐리커쳐 선택** ✅")
                        qr_code_image = generate_qr_code(sketch_index)
                        st.image(qr_code_image, caption="📱 QR 코드 스캔 후 스케치 다운로드", use_container_width=True)
                        sketch_index += 1  # ✅ 다음 스케치 번호 증가
                    else:
                        st.write("🎨 **캐리커쳐 선택** ❌")
                        
    st.markdown(
    """
    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 10px; border: 2px solid #ddd; text-align: center; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1); margin: 20px 0;">
        <h2 style="color: #14148C; margin-bottom: 10px;"> "🤖 로봇은 실수할 수 있어요!" </h2>
        <p style="font-size: 18px; color: #333; font-weight: bold;"> 열심히 응원해주면 더 잘할지도..? 💙 </p>
    </div>
    """,
    unsafe_allow_html=True
)

    if st.button("🔄 처음으로 돌아가기"):
        keys_to_keep = ["role"]  # 로그인 정보 유지
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]  # 특정 키만 삭제
        st.session_state.page = None
        st.rerun()
