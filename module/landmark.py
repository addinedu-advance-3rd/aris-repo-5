## mediapipe landmark 계산 ##

import cv2
import mediapipe as mp
from .segment import get_segment_face_image

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

  image = cv2.imread("./image/25=11_Cartoonize Effect.jpg")
  segment_face_image = get_segment_face_image(image)

  get_landmark(segment_face_image)
