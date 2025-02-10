import streamlit as st
import os
from utils.db_connector import get_db_connection

#------------------------
# ✅ 장바구니 최대 개수 제한
MAX_CART_ITEMS = 2
#--------------------------

def fetch_menu_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 아이스크림 맛 데이터 가져오기
    cursor.execute("SELECT flavor_id, name, price, stock_quantity FROM flavor")
    flavors = cursor.fetchall()
    flavor_options = {
        flavor[1]: {
            "id": flavor[0],
            "price": flavor[2],
            "stock": flavor[3],
            "image": f"images/{flavor[1]}.png"  # 이미지 경로
        } for flavor in flavors
    }

    # 토핑 데이터 가져오기
    cursor.execute("SELECT topping_id, name, price, stock_quantity FROM topping")
    toppings = cursor.fetchall()
    topping_options = {
        topping[1]: {
            "id": topping[0],
            "price": topping[2],
            "stock": topping[3],
            "image": f"images/{topping[1]}.png"  # 이미지 경로
        } for topping in toppings
    }

    cursor.close()
    conn.close()
    return flavor_options, topping_options

def get_flavor_cart_count(flavor_id):
    """장바구니에서 특정 flavor가 몇 개 담겨있는지 확인하는 함수"""
    return sum(item["quantity"] for item in st.session_state.cart if item["menu_id"] == flavor_id)

def get_topping_cart_count(topping_id, topping_options):
    """현재 선택된 토핑 개수 + 장바구니 내 동일 토핑 개수를 정확히 합산"""
    
    # ✅ 현재 선택된 토핑 개수 (중복 가능)
    selected_count = sum(1 for topping in st.session_state.selected_toppings if topping_options[topping]["id"] == topping_id)

    # ✅ 장바구니 내 동일 토핑 개수 반영
    cart_count = 0  # 장바구니 내 특정 토핑 개수를 저장할 변수
    for cart in st.session_state.cart:
        for key, value in cart['toppings'].items():
            if value['id'] == topping_id:
                cart_count += 1
                print(f'{key}의 토핑 개수 {cart_count}')
                
    return selected_count + cart_count  # ✅ 현재 선택한 개수 + 장바구니 개수 합산



def menu_page():
    st.title("🍦 메뉴 선택")
    st.header("원하는 메뉴를 선택하세요.")

    # MySQL에서 아이스크림 맛과 토핑 데이터 가져오기
    flavor_options, topping_options = fetch_menu_data()

    # ✅ 장바구니 session_state 초기화
    if "cart" not in st.session_state:
        st.session_state.cart = []

    # ✅ 선택한 메뉴를 저장하는 session_state 초기화
    if "selected_menu" not in st.session_state:
        st.session_state.selected_menu = None

    # ✅ 선택한 토핑을 저장하는 session_state 초기화
    if "selected_toppings" not in st.session_state:
        st.session_state.selected_toppings = []

    # ✅ modal 형식 초기화
    if "show_modal" not in st.session_state:
        st.session_state.show_modal = False

#----------------------------------------------------------------------------
    # ✅ 장바구니 개수 확인
    cart_count = len(st.session_state.cart)
    if cart_count >= MAX_CART_ITEMS:
        st.warning(f"⚠️ 장바구니에는 최대 {MAX_CART_ITEMS}개까지만 담을 수 있습니다!")
#----------------------------------------------------------------------------

    # ✅ 아이스크림 선택 화면
    st.subheader("🍨 아이스크림 선택")
    cols = st.columns(len(flavor_options))  # 메뉴 수에 맞춰 컬럼 생성

    for index, (menu, details) in enumerate(flavor_options.items()):
        with cols[index]:  # 각 컬럼에 개별 아이스크림 배치
            if os.path.exists(details["image"]):
                st.image(details["image"], caption=menu, use_container_width=True)
            st.write(f"{menu} - {details['price']}원")

            if details["stock"] == 0:  # ✅ 재고가 없으면 '품절' 메시지 출력
                st.write("❌ 품절")
            else:
                #----------------------------------------------------
                disabled = cart_count >= MAX_CART_ITEMS
                #----------------------------------------------------
                if st.button(f"선택하기", key=f"select_{menu}", disabled=disabled):
                    #---------------------------------------------------
                    if cart_count < MAX_CART_ITEMS:
                    #---------------------------------------------------
                        st.session_state.selected_menu = menu  # 선택한 메뉴 저장
                        st.session_state.selected_toppings = []  # ✅ 새 메뉴 선택 시 기존 토핑 초기화
                        st.session_state.show_modal = True  # ✅ Show modal
                        st.rerun()  # UI 새로고침
                    #----------------------------------------------------------------------
                    else:
                        st.error(f"❌ 장바구니에는 최대 {MAX_CART_ITEMS}개까지만 담을 수 있습니다!")
                    #----------------------------------------------------------------------

    # ✅ Display modal-like options
    if st.session_state.show_modal and st.session_state.selected_menu:
        selected_details = flavor_options[st.session_state.selected_menu]
        with st.expander(f"🛠️ {st.session_state.selected_menu} 옵션 선택", expanded=True):

            # ✅ 토핑 선택 체크박스 (최대 2개 선택 가능)
            st.subheader("🍫 토핑 추가 (최대 2개)")
            topping_cols = st.columns(len(topping_options))

            def update_topping_selection(topping_name, topping_id, topping_options):
                """토핑 선택 시 최대 2개까지만 유지"""
                if topping_name in st.session_state.selected_toppings:
                    st.session_state.selected_toppings.remove(topping_name)  # 선택 해제
                else:
                    if len(st.session_state.selected_toppings) >= 2:
                        st.session_state.selected_toppings.pop(0)  # 가장 오래된 선택 삭제

                    st.session_state.selected_toppings.append(topping_name)  # 새로운 선택 추가

            for index, (topping, details) in enumerate(topping_options.items()):
                with topping_cols[index]:  # 각 컬럼에 개별 토핑 배치
                    if os.path.exists(details["image"]):
                        st.image(details["image"], caption=topping, use_container_width=True)
                    st.write(f"{topping} - {details['price']}원")

                    if details["stock"] == 0:
                        st.write("🚫 품절")
                    else:
                        # ✅ 체크박스 UI 적용 (선택하면 quantity=1 자동 설정)
                        selected = st.checkbox(
                            label=topping,
                            value=topping in st.session_state.selected_toppings,
                            key=f"topping_{topping}"
                        )

                        # ✅ 체크박스 상태 변경 시, 업데이트 함수 실행 (재고 체크 포함)
                        if selected != (topping in st.session_state.selected_toppings):
                            update_topping_selection(topping, details["id"], topping_options)
                            st.rerun()  # UI 업데이트

            # ✅ 가격 계산
            topping_total = sum(topping_options[t]["price"] for t in st.session_state.selected_toppings)
            total_price = selected_details["price"] + topping_total

            st.write(f"🛒 총 가격: {total_price}원")

            # ✅ 장바구니 담기 버튼
            if st.button("🛒 장바구니 담기"):
                current_cart_count = get_flavor_cart_count(selected_details["id"])
                total_after_add = current_cart_count + 1  # ✅ 추가될 개수 포함

                # ✅ 아이스크림 재고 초과 여부 체크
                if total_after_add > selected_details["stock"]:
                    st.session_state.warning_message = f"⚠️ {st.session_state.selected_menu} 아이스크림의 재고가 부족합니다! 더 이상 담을 수 없습니다."
                    st.rerun()

                # ✅ 토핑 재고 초과 여부 체크
                for topping in st.session_state.selected_toppings:
                    topping_id = topping_options[topping]["id"]
                    total_topping_after_add = get_topping_cart_count(topping_id, topping_options)  # ✅ 추가될 개수 반영

                    if total_topping_after_add > topping_options[topping]["stock"]:
                        st.session_state.warning_message = f"⚠️ {topping} 토핑의 재고가 부족합니다! 추가할 수 없습니다."
                        st.rerun()

                # ✅ 모든 재고가 충분한 경우에만 실행
                selected_toppings_data = {
                    topping: {
                        "id": topping_options[topping]["id"],
                        "price": topping_options[topping]["price"],
                        "quantity": 1  # ✅ 항상 1개로 설정
                    }
                    for topping in st.session_state.selected_toppings
                }

                #---------------------------------------------------------
                if len(st.session_state.cart) >= MAX_CART_ITEMS:
                    st.error(f"❌ 장바구니에는 최대 {MAX_CART_ITEMS}개까지만 담을 수 있습니다!")
                else:
                #------------------------------------------------------------
                    st.session_state.cart.append({
                        "menu_id": selected_details["id"],
                        "menu": st.session_state.selected_menu,
                        "quantity": 1,
                        "base_price": selected_details["price"],
                        "toppings": selected_toppings_data,
                        "total_price": selected_details["price"] + sum(t["price"] for t in selected_toppings_data.values()),
                    })

                    st.session_state.warning_message = None  # ✅ 성공적으로 추가되었으면 경고 메시지 제거
                    st.success(f"{st.session_state.selected_menu}이(가) 장바구니에 추가되었습니다!")
                    st.session_state.selected_menu = None  # ✅ 선택 초기화
                    st.session_state.show_modal = False  # ✅ Hide modal
                    st.rerun()


            # ✅ 경고 메시지가 있으면 표시
            if "warning_message" in st.session_state and st.session_state.warning_message:
                st.warning(st.session_state.warning_message)

            # ✅ Close button (hide modal)
            if st.button("❌ 닫기"):
                st.session_state.selected_menu = None
                st.session_state.show_modal = False  # ✅ Hide modal
                st.rerun()

    # ✅ 장바구니 UI 추가 (삭제 버튼 포함)
    st.sidebar.header("🛒 장바구니")
    if st.session_state.cart:
        for i, item in enumerate(st.session_state.cart):
            topping_details = [f"{t} (x{d['quantity']}) ({d['price']}원)" for t, d in item["toppings"].items()]
            topping_text = ", ".join(topping_details) if topping_details else "없음"

            st.sidebar.markdown(
                f"- **{item['menu']}** (x{item['quantity']}): {item['base_price'] * item['quantity']}원  \n"
                f"  └ **토핑:** {topping_text}  \n"
                f"  **합계:** {item['total_price']}원"
            )

            col1, col2 = st.sidebar.columns(2)
            with col1:
                # ✅ + 버튼 추가 (메뉴 개별 추가)
                if st.button("➕", key=f"plus_{i}", disabled=len(st.session_state.cart) >= MAX_CART_ITEMS):
                    #----------------------------------------------------------------------
                    if len(st.session_state.cart) < MAX_CART_ITEMS:
                        st.session_state.cart.append(item.copy())  # 같은 항목 추가
                        st.rerun()
                    else:
                        st.error(f"❌ 장바구니에는 최대 {MAX_CART_ITEMS}개까지만 담을 수 있습니다!")
                    #----------------------------------------------------------------------

            with col2:
                # ✅ 개별 삭제 버튼 추가
                if st.button("➖", key=f"remove_{i}"):
                    del st.session_state.cart[i]
                    st.rerun()

        st.sidebar.write(f"총 금액: {sum(item['total_price'] for item in st.session_state.cart)}원")

        # ✅ 장바구니 전체 초기화 버튼 추가
        if st.sidebar.button("🗑 장바구니 초기화"):
            st.session_state.cart = []
            st.rerun()
        # 주문하기 버튼 추가
        if st.sidebar.button("주문하기"):
            st.session_state.page = "cart_page"
            st.rerun()
    else:
        st.sidebar.write("장바구니가 비어 있습니다.")
    

    if st.button("🏠 처음으로 돌아가기"):
        # ✅ 주문 관련 데이터만 초기화 (로그인 정보 유지)
        keys_to_keep = ["role"]  # 로그인 정보 유지
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]  # 특정 키만 삭제

        # ✅ start_page로 이동
        st.session_state.page = None
        st.rerun()