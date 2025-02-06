import cv2
import mediapipe as mp

def crop_face_from_image(image_path, margin=100):
    # MediaPipe 얼굴 감지 초기화
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

    # 이미지 파일 로드
    image = cv2.imread(image_path)

    # BGR -> RGB 변환 (MediaPipe는 RGB 사용)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 얼굴 감지 수행
    results = face_detection.process(rgb_image)

    if results.detections:
        h, w, _ = image.shape
        
        # 가장 큰 얼굴 찾기
        largest_face = None
        max_area = 0
        
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            x_min = int(bboxC.xmin * w)
            y_min = int(bboxC.ymin * h)
            width = int(bboxC.width * w)
            height = int(bboxC.height * h)
            
            face_area = width * height
            if face_area > max_area:
                max_area = face_area
                largest_face = (x_min, y_min, width, height)

        # 얼굴이 가까이 찍히면 crop 안함
        face_area_ratio = max_area / (w * h)
        if face_area_ratio > 0.3:
            filename = "cropped_face.jpg"
            cv2.imwrite(filename, image)
            print(f"이미지 저장됨: {filename}")
            return image

        # 크롭 영역 보정 (이미지 경계를 넘어가지 않도록 처리)
        x_min, y_min, width, height = largest_face
        x_min = max(0, x_min - margin)
        y_min = max(0, y_min - margin)
        x_max = min(w, x_min + width + margin * 2)
        y_max = min(h, y_min + height + margin * 2)

        # 얼굴 크롭
        cropped_face_image = image[y_min:y_max, x_min:x_max]

        # 디버깅용 저장
        filename = "cropped_face.jpg"
        cv2.imwrite(filename, cropped_face_image)
        print(f"이미지 저장됨: {filename}")

        return cropped_face_image
    else:
        print("얼굴을 감지하지 못했습니다.")
        return None

if __name__ == "__main__":
    image_path = "./image/25=11_Cartoonize Effect.jpg"  # 경로 이미지 파일
    cropped_face_image = crop_face_from_image(image_path)
    
    if cropped_face_image is not None:
        filename = "cropped_face.jpg"
        cv2.imwrite(filename, cropped_face_image)
        print(f"이미지 저장됨: {filename}")
