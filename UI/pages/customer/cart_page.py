#4단계: 주문 내용 확인

import streamlit as st

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

        # 주문 확정 버튼
        if st.button("주문 확정"):
            st.session_state.cart = []
            st.session_state.page = "caricature_page"  # 캐리커쳐 선택 페이지로 이동
            st.rerun()
    else:
        st.write("장바구니가 비어 있습니다.")

    # 메뉴 페이지로 돌아가기 버튼
    if st.button("메뉴로 돌아가기"):
        st.session_state.page = "menu"
        st.rerun()
