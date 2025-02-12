import streamlit as st
from utils.db_connector import get_db_connection

def save_order_to_db():
    """MySQL에 주문 데이터를 저장하는 함수"""
    if "cart" not in st.session_state or not st.session_state.cart:
        st.error("🚨 장바구니가 비어 있습니다. 메뉴를 선택해주세요!")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        new_order_ids = []  # ✅ 새롭게 생성된 주문 ID 저장 리스트

        for item in st.session_state.cart:
            # ✅ 주문 테이블에 저장
            cursor.execute(
                "INSERT INTO orders (flavor_id, selected_caricature, total_price) VALUES (%s, %s, %s)",
                (item["menu_id"], None, item["total_price"])  # ✅ 캐리커쳐 선택 전이므로 None
            )
            order_id = cursor.lastrowid  # ✅ 생성된 주문 ID 저장
            new_order_ids.append(order_id)

            # ✅ 토핑 테이블에 저장
            for topping, details in item["toppings"].items():
                cursor.execute(
                    "INSERT INTO order_topping (order_id, topping_id, quantity) VALUES (%s, %s, %s)",
                    (order_id, details["id"], details["quantity"])
                )

            # ✅ 재고 감소 처리
            cursor.execute(
                "UPDATE flavor SET stock_quantity = stock_quantity - %s WHERE flavor_id = %s",
                (item["quantity"], item["menu_id"])
            )
            for topping, details in item["toppings"].items():
                cursor.execute(
                    "UPDATE topping SET stock_quantity = stock_quantity - %s WHERE topping_id = %s",
                    (details["quantity"], details["id"])
                )

        conn.commit()
        ## server에 전송할 order_info 생성
        order_info = []

        for i in range(len(st.session_state.cart)):
            print('{0}번 menu :'.format(i+1), st.session_state.cart[i]['menu'])
            print('{0}번 topping :'.format(i+1) , st.session_state.cart[i]['toppings'].keys())
        
        for i in range(len(st.session_state.cart)):
            menu = st.session_state.cart[i]['menu']
            toppings = list(st.session_state.cart[i]['toppings'].keys())
            order_info.append([menu,toppings,False])

        st.session_state.order_info = order_info
        print('order_info : ' , order_info)

        st.success("✅ 주문이 성공적으로 저장되었습니다!")

        # ✅ 최신 주문 목록을 세션에 저장
        st.session_state.latest_order_ids = new_order_ids
        print(f"🆕 최신 주문 목록 저장: {st.session_state.latest_order_ids}")

        for i in range(len(st.session_state.order_info)):
            st.session_state.order_info[i].append(False)
            
        st.session_state.page = "caricature_page"
        st.rerun()

    except Exception as e:
        conn.rollback()
        st.error(f"❌ 주문 저장 실패: {e}")

    finally:
        cursor.close()
        conn.close()

def display_cart():
    """장바구니 내용을 Streamlit UI로 출력"""
    if "cart" in st.session_state and st.session_state.cart:
        total_price = 0
        st.subheader("🛒 장바구니 목록")
        with st.container(border=True):
            for idx, item in enumerate(st.session_state.cart, start=1):
                topping_text = ", ".join(
                    [f"{topping} x{details['quantity']}개 ({details['price']}원)" for topping, details in item["toppings"].items()]
                ) if item["toppings"] else "없음"

                with st.container():  # ✅ 개별 주문을 박스로 감싸기
                    st.markdown(
                        f"""
                        <div style='padding: 12px; border: 2px solid #ddd; border-radius: 10px; margin-bottom: 10px; background-color: #f9f9f9;'>
                            <p style='font-size: 25px; font-weight: bold;'> 📌 {idx}</p>
                            <p style='font-size: 20px; font-weight: bold; margin: 5px 0;'>🍨 {item['menu']} (x{item['quantity']})</p>
                            <p style='font-size: 18px; margin: 5px 0;'>└ 🍫 <strong>토핑:</strong> {topping_text}</p>
                            <p style='font-size: 20px; font-weight: bold; margin: 20px 0;'>💰 합계: {item['total_price']}원</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                total_price += item["total_price"]

            st.subheader(f"**🛍 총 주문 금액: {total_price}원**")

        if st.button("✅ 주문 확정"):
            save_order_to_db()
    else:
        st.warning("🚨 장바구니가 비어 있습니다. 메뉴를 선택해주세요.")

def cart_page():
    """주문 확인 페이지"""
    st.header("📋 주문 목록을 확인해주세요")
    display_cart()

    if st.button("🔙 메뉴로 돌아가기"):
        st.session_state.page = "menu"
        st.rerun()
