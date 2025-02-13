## mediapipe landmark 계산 ##
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0: 모든 메시지, 3: 에러만
os.environ['GLOG_minloglevel'] = '3'
import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)
import cv2
import mediapipe as mp
#from segment import get_segment_face_image
from crop_image import crop_face_from_image

def get_landmark(image):
    """
    Mediapipe FaceMesh를 사용하여 얼굴 랜드마크를 추출하는 함수.

    :param image: 입력 이미지
    :return: Mediapipe FaceMesh 랜드마크 결과
    """
    mp_drawing = mp.solutions.drawing_utils
    mp_face_mesh = mp.solutions.face_mesh

    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        #max_num_faces=9,  # 한 이미지에서 최대 얼굴 감지 개수 설정 (디버깅용)
        min_detection_confidence=0.5) as face_mesh:

        # Convert the BGR image to RGB before processing.
        landmark_results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # 랜드마크 결과 리턴
        if landmark_results.multi_face_landmarks:
            # 시각화
            # for face_landmarks in landmark_results.multi_face_landmarks:
            #     annotated_image = image.copy()
            #     mp_drawing.draw_landmarks(
            #         image=annotated_image,
            #         landmark_list=face_landmarks,
            #         connections=mp_face_mesh.FACEMESH_CONTOURS,
            #         landmark_drawing_spec=drawing_spec,
            #         connection_drawing_spec=drawing_spec)
            return landmark_results
        return None
      
if __name__ == "__main__":

    #image = cv2.imread("./image/1739411485911.jpg")

    cropped_face = crop_face_from_image("./image/1739411485911.jpg")
    """
    segment_face_image, _, _ = get_segment_face_image(cropped_face)
    print("segment_face_image Type:", type(segment_face_image))
    landmark_results = get_landmark(segment_face_image)
    """
    landmark_results = get_landmark(cropped_face)

    print("\n=== landmark_results 상세 분석 ===")
    print("Type:", type(landmark_results))
    print("All attributes:", dir(landmark_results))

    # 모든 속성의 값 출력
    for attr in dir(landmark_results):
        if not attr.startswith('_'):  # 내부 속성 제외
            try:
                value = getattr(landmark_results, attr)
                print(f"\n{attr}:", value)
                print(f"{attr} type:", type(value))
            except:
                print(f"Cannot access {attr}")

    # landmark_results가 None이 아닌지 먼저 확인한 후, multi_face_landmarks 속성이 있는지 확인
    if landmark_results is not None and landmark_results.multi_face_landmarks:
        landmark_visualized_image = cropped_face.copy()

        # 모든 얼굴의 랜드마크들을 순회
        for face_landmarks in landmark_results.multi_face_landmarks:
            for idx, landmark in enumerate(face_landmarks.landmark):
                # 이미지 크기에 맞게 좌표 변환
                x = int(landmark.x * landmark_visualized_image.shape[1])
                y = int(landmark.y * landmark_visualized_image.shape[0])
                # 랜드마크 표시
                cv2.circle(landmark_visualized_image, (x, y), 2, (0, 0, 255), -1)
                # 랜드마크 번호 표시 (선택사항)
                #cv2.putText(landmark_visualized_image, str(idx), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1)
        
        # 랜드마크 시각화하여 파일로 저장
        cv2.imwrite('./image/face_landmarks_visualization.jpg', landmark_visualized_image)
        
        # 랜드마크 개수 출력
        print(f"\n총 랜드마크 개수: {len(face_landmarks.landmark)}")
    else:
        print("랜드마크가 감지되지 않았습니다!")
