import requests
import base64
import time

# 2번 노트북 서버 주소 (Flask 서버)
FLASK_SERVER_URL = "http://192.168.0.11:5000"

class CommunicationClient:

    def __init__(self,image_path, people_count,order_info):

        self.people_count = people_count
        self.image_path = image_path  # 손님이 찍은 사진 경로
        self.order_info = order_info 
        # order_info 예시: [['strawberry', ['jollypong', 'chocoball']], ['blueberry', ['sunflower_seeds']]]
        # 1 menu : order_info[0][0]
        # 1 toppings : order_info[0][1]



    def send_image_to_server(self,image_path):
        """손님이 찍은 이미지를 2번 노트북으로 전송 (people_count 포함)"""
        with open(self.image_path, "rb") as image_file:
            image_bytes = image_file.read()
        
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        self.people_count = 1 ## 사람 수 받아오기(주문 수) ##

        data = {
            "image": image_base64,
            "people_count": self.people_count  # 다른 파일에서 불러온 사람 수
        }

        response = requests.post(f"{FLASK_SERVER_URL}/upload", json=data)

        if response.status_code == 200:
            print("✅ 손님 이미지 전송 완료!")
        else:
            print("❌ 이미지 전송 실패:", response.json())

    def get_caricature_result(self):
        """2번 노트북에서 변환된 캐리커쳐 이미지를 받아 저장"""
        response = requests.get(f"{FLASK_SERVER_URL}/result")

        if response.status_code == 200:
            data = response.json()
            caricature_image = base64.b64decode(data["image"])

            # 받은 이미지를 저장
            with open("received_caricature.jpg", "wb") as f:
                f.write(caricature_image)

            print("✅ 캐리커쳐 저장 완료!")
            return True  # 서버가 정상 종료될 수 있도록 True 반환

        else:
            print("❌ 캐리커쳐 요청 실패:", response.json())
            return False  # 실패 시 False 반환
        
    def send_order(self):
        data = {
            "order": self.order_info
        }
        response = requests.post(f"{FLASK_SERVER_URL}/order", json=data)
        if response.status_code == 200:
            print("✅ 주문 정보 전송 완료!")
        else:
            print("❌ 주문 정보 전송 실패:", response.text)


    def run(self):
        
        while self.people_count: ## 아이스크림 개수만큼 반복
            self.send_image_to_server(image_path)  # 1) 손님 이미지 전송
            success = self.get_caricature_result()  # 5) 변환된 캐리커쳐 받아 저장

            if success:
                print("🚀 1번 노트북 동작 유지 (다음 요청 가능)")
    
            time.sleep(2)  # 2초 대기 후 다시 실행 (반복)

def send_order_data(order_info, image_path,people_count=1):
    client = CommunicationClient(order_info, image_path,people_count=len(order_info))
    client.run()

if __name__ == "__main__":
    
    image_path = "/home/kang/aris-repo-5/image copy.png"
    people_count = 1
    order_info = []
    send_order_data(order_info,image_path,people_count=len(order_info))
    ######서버에서 people_count 만큼 반복한 후 서버 종료하기##########
    ####2번 : 디렉토리 만들고 각각 저장시켜서 