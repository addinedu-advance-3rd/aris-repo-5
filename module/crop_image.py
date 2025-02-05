import cv2
import mediapipe as mp

def crop_face_from_image(image_path, margin=70):

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
        detection = results.detections[0]
        bboxC = detection.location_data.relative_bounding_box
        h, w, _ = image.shape
        
        # 얼굴 영역을 픽셀 단위로 변환
        x_min = int(bboxC.xmin * w)
        y_min = int(bboxC.ymin * h)
        width = int(bboxC.width * w)
        height = int(bboxC.height * h)

        # 얼굴이 가까이 찍히면 crop 안하게
        face_area_ratio = (width * height) / (w * h)  # 얼굴 크기가 이미지에서 차지하는 비율

        if face_area_ratio > 0.3:
            # 디버깅용
            filename = "cropped_face.jpg"
            cv2.imwrite(filename, image)
            print(f"이미지 저장됨: {filename}")
            return image

        # 크롭 영역 보정 (이미지 경계를 넘어가지 않도록 처리)
        x_min = max(0, x_min - margin)
        y_min = max(0, y_min - margin)
        x_max = min(w, x_min + width + margin * 2)
        y_max = min(h, y_min + height + margin * 2)

        # 얼굴 크롭
        cropped_face_image = image[y_min:y_max, x_min:x_max]

        # 얼굴 감지 박스 표시 (디버깅용)
        # cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

        # 디버깅용
        filename = "cropped_face.jpg"
        cv2.imwrite(filename, cropped_face_image)
        print(f"이미지 저장됨: {filename}")
        
        return cropped_face_image
    
    else:
        return None

if __name__ == "__main__":

    image_path = "./image/25=11_Cartoonize Effect.jpg"  # 경로 이미지 파일
    cropped_face_image = crop_face_from_image(image_path)

    # 크롭된 얼굴 저장
    filename = "cropped_face.jpg"
    cv2.imwrite(filename, cropped_face_image)
    print(f"이미지 저장됨: {filename}")