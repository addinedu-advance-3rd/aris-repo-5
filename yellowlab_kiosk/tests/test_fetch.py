import sys
import os

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.db_connector import get_db_connection

def fetch_test_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("🟢 등록된 아이스크림 맛:")
    cursor.execute("SELECT * FROM flavor")
    for row in cursor.fetchall():
        print(row)

    print("\n🟢 등록된 토핑:")
    cursor.execute("SELECT * FROM topping")
    for row in cursor.fetchall():
        print(row)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    fetch_test_data()