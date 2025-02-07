import streamlit as st
import pandas as pd
from utils.db_connector import get_db_connection

# ✅ MySQL에서 메뉴 데이터 가져오기
def fetch_menu():
    """MySQL에서 아이스크림 및 토핑 목록을 가져오는 함수"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT flavor_id, name, price FROM flavor;")
    flavors = cursor.fetchall()

    cursor.execute("SELECT topping_id, name, price FROM topping;")
    toppings = cursor.fetchall()

    conn.close()

    return {
        "flavors": [{"ID": f[0], "이름": f[1], "가격": f[2]} for f in flavors],
        "toppings": [{"ID": t[0], "이름": t[1], "가격": t[2]} for t in toppings],
    }

# ✅ MySQL에서 메뉴 추가
def add_menu_item(item_type, name, price):
    """새로운 아이스크림 맛 또는 토핑을 추가하는 함수"""
    conn = get_db_connection()
    cursor = conn.cursor()

    table = "flavor" if item_type == "flavor" else "topping"

    try:
        cursor.execute(f"INSERT INTO {table} (name, price, stock_quantity) VALUES (%s, %s, %s)", (name, price, 0))
        conn.commit()
        st.success(f"✅ {table.capitalize()} '{name}'이(가) 추가되었습니다.")
    except Exception as e:
        st.error(f"❌ 추가 실패: {e}")
    finally:
        conn.close()

# ✅ MySQL에서 메뉴 삭제
def delete_menu_item(item_type, item_id):
    """기존 아이스크림 맛 또는 토핑을 삭제하는 함수"""
    conn = get_db_connection()
    cursor = conn.cursor()

    table = "flavor" if item_type == "flavor" else "topping"

    try:
        cursor.execute(f"DELETE FROM {table} WHERE {table}_id = %s", (item_id,))
        conn.commit()
        st.success(f"✅ {table.capitalize()} ID {item_id}가 삭제되었습니다.")
    except Exception as e:
        st.error(f"❌ 삭제 실패: {e}")
    finally:
        conn.close()

# ✅ MySQL에서 가격 업데이트
def update_price(item_type, item_id, new_price):
    """기존 아이스크림 맛 또는 토핑의 가격을 변경하는 함수"""
    conn = get_db_connection()
    cursor = conn.cursor()

    table = "flavor" if item_type == "flavor" else "topping"

    try:
        cursor.execute(f"UPDATE {table} SET price = %s WHERE {table}_id = %s", (new_price, item_id))
        conn.commit()
        st.success(f"✅ {table.capitalize()} 가격이 {new_price}원으로 변경되었습니다.")
    except Exception as e:
        st.error(f"❌ 가격 변경 실패: {e}")
    finally:
        conn.close()

# ✅ Streamlit UI
def menu_management_page():
    st.title("🍦 메뉴 관리")
    st.write("현재 등록된 아이스크림 맛과 토핑을 관리할 수 있습니다.")

    # ✅ 데이터 가져오기
    data = fetch_menu()

    # ✅ 1. 아이스크림 맛 관리
    st.subheader("🍦 아이스크림 메뉴")
    df_flavors = pd.DataFrame(data["flavors"])
    st.dataframe(df_flavors, use_container_width=True)

    # ✅ 아이스크림 추가
    st.subheader("➕ 새로운 아이스크림 추가")
    new_flavor_name = st.text_input("새로운 맛 이름")
    new_flavor_price = st.number_input("가격 (원)", min_value=0, max_value=30000, step=10)

    if st.button("✅ 추가하기", key="add_flavor"):
        add_menu_item("flavor", new_flavor_name, new_flavor_price)
        st.rerun()

    # ✅ 아이스크림 삭제
    st.subheader("🗑️ 아이스크림 삭제")
    flavor_options = {f["이름"]: f["ID"] for f in data["flavors"]}
    selected_flavor = st.selectbox("삭제할 아이스크림 선택", list(flavor_options.keys()))

    if st.button("🗑️ 삭제하기", key="delete_flavor"):
        delete_menu_item("flavor", flavor_options[selected_flavor])
        st.rerun()

    st.divider()

    # ✅ 2. 토핑 관리
    st.subheader("🍫 토핑 메뉴")
    df_toppings = pd.DataFrame(data["toppings"])
    st.dataframe(df_toppings, use_container_width=True)

    # ✅ 토핑 추가
    st.subheader("➕ 새로운 토핑 추가")
    new_topping_name = st.text_input("새로운 토핑 이름")
    new_topping_price = st.number_input("가격 (원)", min_value=0, max_value=10000, step=10)

    if st.button("✅ 추가하기", key="add_topping"):
        add_menu_item("topping", new_topping_name, new_topping_price)
        st.rerun()

    # ✅ 토핑 삭제
    st.subheader("🗑️ 토핑 삭제")
    topping_options = {t["이름"]: t["ID"] for t in data["toppings"]}
    selected_topping = st.selectbox("삭제할 토핑 선택", list(topping_options.keys()))

    if st.button("🗑️ 삭제하기", key="delete_topping"):
        delete_menu_item("topping", topping_options[selected_topping])
        st.rerun()

    st.divider()

    # ✅ 대시보드로 돌아가는 버튼
    if st.button("⬅️ 대시보드로 돌아가기"):
        st.session_state.page = "dashboard"
        st.rerun()
