import sys
import os

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.db_connector import get_db_connection

def insert_order_test():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 테스트 주문 삽입
    cursor.execute("INSERT INTO orders (flavor_id, selected_caricature, total_price) VALUES (%s, %s, %s)",
                   (1, True, 6000))

    conn.commit()
    print("✅ 테스트 주문 삽입 완료!")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    insert_order_test()
