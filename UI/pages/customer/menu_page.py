#3단계: 메뉴선택

import streamlit as st

def menu_page():
    # Initialize session state for cart
    if "cart" not in st.session_state:
        st.session_state.cart = []

    st.title("메뉴 선택")
    st.header("원하는 메뉴를 선택하세요.")

    # 메뉴와 가격 리스트
    menu_prices = {
        "아이스크림": 4000,
        "음료": 3000,
        "디저트": 6000
    }
    topping_prices = {
        "초콜릿 칩": 500,
        "과일": 700,
        "카라멜": 600
    }

    # 메뉴 선택
    menu = st.selectbox("메뉴를 고르세요", list(menu_prices.keys()))
    base_price = menu_prices[menu]

    # 옵션 선택 창
    with st.expander("옵션 선택"):
        st.subheader(f"{menu} 옵션 선택")
        
        # 수량 선택
        quantity = st.number_input("수량", min_value=1, max_value=10, value=1)
        
        # 토핑 선택
        toppings = {}
        for topping, price in topping_prices.items():
            qty = st.number_input(f"{topping} 수량 (개당 {price}원)", min_value=0, max_value=5, value=0)
            if qty > 0:
                toppings[topping] = {"quantity": qty, "price": price * qty}

        # 가격 계산
        topping_total = sum(t["price"] for t in toppings.values())
        total_price = base_price * quantity + topping_total

        st.write(f"메뉴 가격: {base_price}원 x {quantity}개 = {base_price * quantity}원")
        st.write(f"토핑 가격: {topping_total}원")
        st.write(f"총 금액: {total_price}원")

        # 장바구니 담기 버튼
        if st.button("장바구니 담기"):
            # 장바구니에 추가
            st.session_state.cart.append({
                "menu": menu,
                "quantity": quantity,
                "base_price": base_price,
                "toppings": toppings,
                "total_price": total_price,
            })
            st.success(f"{menu}이(가) 장바구니에 추가되었습니다!")

    # 왼쪽 사이드바에 장바구니 표시
    with st.sidebar:
        st.header("🛒 장바구니")
        if st.session_state.cart:
            total_price = 0
            for item in st.session_state.cart:
                # 토핑 리스트 생성
                topping_details = []
                for topping, details in item["toppings"].items():
                    topping_details.append(f"{topping} x{details['quantity']}개 ({details['price']}원)")
                topping_text = "\n".join(topping_details) if topping_details else "없음"

                # Markdown 형식으로 장바구니 항목 표시
                st.markdown(
                    f"- **{item['menu']}** (x{item['quantity']}): {item['base_price'] * item['quantity']}원  \n"
                    f"  └ **토핑:** {topping_text}  \n"
                    f"  **합계:** {item['total_price']}원"
                )
                total_price += item["total_price"]
            st.write(f"총 금액: {total_price}원")

            # 주문하기 버튼 추가
            if st.button("주문하기"):
                st.session_state.page = "cart_page"  # 주문 페이지로 이동
                st.rerun()
        else:
            st.write("장바구니가 비어 있습니다.")


