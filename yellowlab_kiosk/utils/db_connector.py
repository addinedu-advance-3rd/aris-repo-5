import mysql.connector

def get_db_connection():
    """ MySQL 연결을 생성하는 함수 """
    conn = mysql.connector.connect(
        host="192.168.0.54",
        user="yellowlab",
        password="1234",
        database="yellowlab_kiosk"
    )
    return conn
