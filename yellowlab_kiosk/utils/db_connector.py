import mysql.connector

def get_db_connection():
    """ MySQL 연결을 생성하는 함수 """
    conn = mysql.connector.connect(
        host="localhost",
        user="admin",
        password="admin123",
        database="yellowlab_kiosk"
    )
    return conn
