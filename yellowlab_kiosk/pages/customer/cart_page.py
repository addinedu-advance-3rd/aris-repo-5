#4단계: 주문 내용 확인

import streamlit as st
from utils.db_connector import get_db_connection

def save_order_to_db():
    """ MySQL에 주문 데이터를 저장하는 함수 """
    if "cart" not in st.session_state or not st.session_state.cart:
        st.error("장바구니가 비어 있습니다.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        new_order_ids = []  # ✅ 새롭게 생성된 주문 ID 저장

        for item in st.session_state.cart:
            cursor.execute(
                "INSERT INTO orders (flavor_id, selected_caricature, total_price) VALUES (%s, %s, %s)",
                (item["menu_id"], None, item["total_price"])  # ✅ 캐리커쳐 선택 전이므로 None
            )
            order_id = cursor.lastrowid  # ✅ 방금 추가된 주문 ID 가져오기
            new_order_ids.append(order_id)

            # 토핑 저장
            for topping, details in item["toppings"].items():
                cursor.execute(
                    "INSERT INTO order_topping (order_id, topping_id, quantity) VALUES (%s, %s, %s)",
                    (order_id, details["id"], details["quantity"])
                )

            # 재고 감소 처리
            cursor.execute("UPDATE flavor SET stock_quantity = stock_quantity - %s WHERE flavor_id = %s",
                           (item["quantity"], item["menu_id"]))
            for topping, details in item["toppings"].items():
                cursor.execute("UPDATE topping SET stock_quantity = stock_quantity - %s WHERE topping_id = %s",
                               (details["quantity"], details["id"]))

        conn.commit()
        st.success("✅ 주문이 성공적으로 저장되었습니다!")

        # ✅ 최신 주문 목록을 세션에 저장
        st.session_state.latest_order_ids = new_order_ids
        print(f"🆕 최신 주문 목록 저장: {st.session_state.latest_order_ids}")

        # 장바구니 비우고 캐리커쳐 선택 페이지로 이동
        st.session_state.cart = []
        st.session_state.page = "caricature_page"
        st.rerun()

    except Exception as e:
        conn.rollback()
        st.error(f"❌ 주문 저장 실패: {e}")

    finally:
        cursor.close()
        conn.close()



def cart_page():
    st.title("주문 확인")
    st.header("장바구니 내용")

    # 주문 내역 표시
    if "cart" in st.session_state and st.session_state.cart:
        total_price = 0
        for item in st.session_state.cart:
            # 토핑 리스트 생성
            topping_details = []
            for topping, details in item["toppings"].items():
                topping_details.append(f"{topping} x{details['quantity']}개 ({details['price']}원)")
            topping_text = "\n".join(topping_details) if topping_details else "없음"

            st.markdown(
                f"- **{item['menu']}** (x{item['quantity']}): {item['base_price'] * item['quantity']}원  \n"
                f"  └ **토핑:** {topping_text}  \n"
                f"  **합계:** {item['total_price']}원"
            )
            total_price += item["total_price"]
        st.write(f"총 금액: {total_price}원")

        # ✅ 주문 확정 버튼 (MySQL 저장 기능 추가)
        if st.button("주문 확정"):
            save_order_to_db()  # MySQL에 주문 저장 함수 호출

    else:
        st.write("장바구니가 비어 있습니다.")

    # 메뉴 페이지로 돌아가기 버튼
    if st.button("메뉴로 돌아가기"):
        st.session_state.page = "menu"
        st.rerun()
