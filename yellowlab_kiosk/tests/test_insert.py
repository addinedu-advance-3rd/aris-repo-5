import sys
import os

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.db_connector import get_db_connection

def reset_and_insert_test_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ 기존 데이터 삭제 및 AUTO_INCREMENT 초기화
    cursor.execute("DELETE FROM flavor;")
    cursor.execute("DELETE FROM topping;")
    cursor.execute("ALTER TABLE flavor AUTO_INCREMENT = 1;")
    cursor.execute("ALTER TABLE topping AUTO_INCREMENT = 1;")

    # ✅ 아이스크림 맛 데이터 추가
    cursor.executemany(
        "INSERT INTO flavor (name, price, stock_quantity) VALUES (%s, %s, %s)",
        [("strawberry", 5000, 20), ("blueberry", 5500, 15)]
    )

    # ✅ 토핑 데이터 추가
    cursor.executemany(
        "INSERT INTO topping (name, price, stock_quantity) VALUES (%s, %s, %s)",
        [("jollypong", 1000, 30), ("chocoball", 1500, 25), ("sunflower_seeds", 1200, 20)]
    )

    conn.commit()
    print("✅ 기존 데이터 삭제 후 새로운 테스트 데이터 삽입 완료!")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    reset_and_insert_test_data()
