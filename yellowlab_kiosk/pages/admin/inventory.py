import streamlit as st
import pandas as pd
from utils.db_connector import get_db_connection

# ✅ MySQL에서 재고 데이터 가져오기
def fetch_inventory():
    """MySQL에서 아이스크림 및 토핑 재고 데이터를 가져오는 함수"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT flavor_id, name, stock_quantity FROM flavor;")
    flavors = cursor.fetchall()

    cursor.execute("SELECT topping_id, name, stock_quantity FROM topping;")
    toppings = cursor.fetchall()

    conn.close()

    return {
        "flavors": [{"ID": f[0], "이름": f[1], "재고": f[2]} for f in flavors],
        "toppings": [{"ID": t[0], "이름": t[1], "재고": t[2]} for t in toppings],
    }

# ✅ MySQL에서 재고 업데이트
def update_stock(item_type, item_id, stock_change):
    """재고를 직접 설정하는 것이 아니라 기존 재고에 증감"""
    conn = get_db_connection()
    cursor = conn.cursor()

    table = "flavor" if item_type == "flavor" else "topping"
    
    try:
        # ✅ 현재 재고 조회
        cursor.execute(f"SELECT stock_quantity FROM {table} WHERE {table}_id = %s", (item_id,))
        current_stock = cursor.fetchone()[0]

        # ✅ 새로운 재고 계산 (기존 재고 + 입력된 값)
        new_stock = max(0, current_stock + stock_change)  # 음수가 되지 않도록 설정

        # ✅ 재고 업데이트
        cursor.execute(f"UPDATE {table} SET stock_quantity = %s WHERE {table}_id = %s", (new_stock, item_id))
        conn.commit()
        st.success(f"✅ {table.capitalize()} 재고가 {stock_change:+}만큼 변경되었습니다. (현재 재고: {new_stock})")
    except Exception as e:
        st.error(f"❌ 재고 업데이트 실패: {e}")
    finally:
        conn.close()

# ✅ Streamlit UI
def inventory_page():
    st.title("📦 재고 관리")
    st.write("현재 재고를 확인하고 수정할 수 있습니다.")

    # ✅ 데이터 가져오기
    data = fetch_inventory()

    # ✅ 1. 아이스크림 재고 관리
    st.subheader("🍦 아이스크림 재고")
    df_flavors = pd.DataFrame(data["flavors"])
    st.dataframe(df_flavors, use_container_width=True)

    # ✅ 아이스크림 재고 수정
    st.subheader("🛠️ 아이스크림 재고 조정")
    flavor_options = {f["이름"]: f["ID"] for f in data["flavors"]}
    selected_flavor = st.selectbox("수정할 맛 선택", list(flavor_options.keys()))
    stock_change_flavor = st.number_input("증감할 수량 (+ 증가, - 감소)", min_value=-100, max_value=100, value=0, step=1, key="flavor_stock")  # ✅ 음수 입력 가능

    if st.button("✅ 아이스크림 재고 변경"):
        update_stock("flavor", flavor_options[selected_flavor], stock_change_flavor)
        st.rerun()

    st.divider()

    # ✅ 2. 토핑 재고 관리
    st.subheader("🍫 토핑 재고")
    df_toppings = pd.DataFrame(data["toppings"])
    st.dataframe(df_toppings, use_container_width=True)

    # ✅ 토핑 재고 수정
    st.subheader("🛠️ 토핑 재고 조정")
    topping_options = {t["이름"]: t["ID"] for t in data["toppings"]}
    selected_topping = st.selectbox("수정할 토핑 선택", list(topping_options.keys()))
    stock_change_topping = st.number_input("증감할 수량 (+ 증가, - 감소)", min_value=-100, max_value=100, value=0, step=1, key="topping_stock")  # ✅ 음수 입력 가능

    if st.button("✅ 토핑 재고 변경"):
        update_stock("topping", topping_options[selected_topping], stock_change_topping)
        st.rerun()

    st.divider()

    # ✅ 대시보드로 돌아가는 버튼
    if st.button("⬅️ 대시보드로 돌아가기"):
        st.session_state.page = "dashboard"
        st.rerun()
