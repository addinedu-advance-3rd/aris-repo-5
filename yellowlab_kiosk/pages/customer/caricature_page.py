import streamlit as st
from utils.db_connector import get_db_connection
from utils.communication import CommunicationClient,send_order_data

def update_order_with_caricature(order_id, selected):
    """ MySQL에 개별 주문의 캐리커쳐 선택 여부 업데이트 """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE orders SET selected_caricature = %s WHERE order_id = %s",
                       (1 if selected else 0, order_id))
        conn.commit()
        print(f"✅ 주문 {order_id}의 캐리커쳐 선택 여부 업데이트 완료: {selected}")
    except Exception as e:
        conn.rollback()
        st.error(f"❌ 캐리커쳐 선택 정보 저장 실패: {e}")
        print(f"❌ 업데이트 오류: {e}")
    finally:
        cursor.close()
        conn.close()

def caricature_page():
    st.header("🎨 로봇팔이 그려주는 당신의 캐리커쳐")
    st.subheader("📜주문번호를 확인하고 캐리커쳐를 선택하세요.")

    # 현재 세션에 저장된 최신 주문 목록 가져오기
    if "latest_order_ids" not in st.session_state or not st.session_state.latest_order_ids:
        st.warning("🚨 새로운 주문 정보가 없습니다! 이전 단계로 돌아가세요.")
        return

    latest_order_ids = st.session_state.latest_order_ids  # 최신 주문 ID 리스트
    print(f"🔍 최신 주문 목록: {latest_order_ids}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ 주문 정보 + flavor 및 토핑 정보 가져오기
    query = """
        SELECT o.order_id, f.name AS flavor_name, 
               GROUP_CONCAT(t.name SEPARATOR ', ') AS topping_names
        FROM orders o
        JOIN flavor f ON o.flavor_id = f.flavor_id
        LEFT JOIN order_topping ot ON o.order_id = ot.order_id
        LEFT JOIN topping t ON ot.topping_id = t.topping_id
        WHERE o.order_id IN ({})
        GROUP BY o.order_id, f.name
    """.format(','.join(['%s'] * len(latest_order_ids)))
    
    cursor.execute(query, latest_order_ids)
    orders = cursor.fetchall()
    cursor.close()
    conn.close()

    print(f"✅ 가져온 최신 주문 목록: {orders}")

    if not orders:
        st.warning("🚨 선택할 주문이 없습니다! 이전 단계로 돌아가세요.")
        return

    caricature_choices = {}
    
    for order_id, flavor_name, topping_names in orders:
        with st.container(border=True):  # ✅ 모든 내용을 박스 안에 포함
            st.markdown(
                f"""
                <div style='padding: 15px; border: 2px solid #ddd; border-radius: 10px; background-color: #f9f9f9; margin-bottom: 10px;'>
                    <p style='font-size: 18px; font-weight: bold; color: #007BFF;'>🆔 주문 번호: {order_id}</p>
                    <p style='font-size: 20px; font-weight: bold; margin: 5px 0;'>🍨 {flavor_name}</p>
                    <p style='font-size: 18px; margin: 5px 0;'>└ 🍫 <strong>토핑:</strong> {topping_names if topping_names else '없음'}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # ✅ 라디오 버튼을 컨테이너 내부로 이동
            choice = st.radio(
                f"🎨 **주문 {order_id}**의 캐리커쳐 선택 여부:",
                ["캐리커쳐 선택", "선택 안함"],
                index=1,  
                key=f"caricature_{order_id}",
                horizontal=True  # ✅ 가로 정렬로 선택하기 쉽게 함
            )

            caricature_choices[order_id] = (choice == "캐리커쳐 선택")


    print(f"✅ 선택된 캐리커쳐 상태: {caricature_choices}")

    ## 캐리커쳐 선택 유무 변경 ##
    for i in range(len(st.session_state.order_info)):
        st.session_state.order_info[i][2] = list(caricature_choices.values())[i]
    print('order_info :', st.session_state.order_info)

    if st.button("➡️ 다음 단계로 이동"):
        for order_id, selected in caricature_choices.items():
            update_order_with_caricature(order_id, selected)
        
        # 선택된 주문이 있는지 확인
        if any(caricature_choices.values()):
            st.session_state.page = "camera_page"  # 하나라도 선택했으면 camera_page 이동
        else:
             ## 통신 - 캐리커쳐 안 그릴 경우 
            send_order_data(st.session_state.order_info, image_path=None)

            st.session_state.page = "pickup_page"  # 모두 선택 안 했으면 pickup_page 이동
        print(f"🔀 이동할 페이지: {st.session_state.page}")
        st.rerun()