import sys
import os

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.db_connector import get_db_connection  # utils 폴더의 db_connector.py 사용

def test_connection():
    try:
        conn = get_db_connection()
        if conn.is_connected():
            print("✅ MySQL 연결 성공!")
        conn.close()
    except Exception as e:
        print(f"❌ MySQL 연결 실패: {e}")

if __name__ == "__main__":
    test_connection()