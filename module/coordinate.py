## 얼굴 부위 별 좌표 추출 ##
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0: 모든 메시지, 3: 에러만
os.environ['GLOG_minloglevel'] = '3'
import cv2
from crop_image import crop_face_from_image
from landmark import get_landmark

def get_coordinates(landmark_results, image):

    landmarks = landmark_results.multi_face_landmarks[0].landmark  # 첫 번째 얼굴의 랜드마크

    shape = image.shape

    # 랜드마크 인덱스
    # https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/modules/face_geometry/data/canonical_face_model_uv_visualization.png
    landmark_indices = {
    "nose" : [168, 122,174,217,198,49,98,97, 2, 326,327,279,420,437,399,351],
    # "nose" : [217,198,209,49,64,98,2,326,327,278,360,420],
    # "nose_masking" : [6, 196,198,205,206, 164, 426,425,420,419],  # 코 마스킹 (임시)
    "center" : [19],  # 코의 중앙 인덱스와 얼굴의 중앙 인덱스로서 역할
    "left_eye" : [133, 173,157,158,159,160,161,246, 33,130, 7,163,144,145,153,154,155],
    # "left_eye" : [ 133, 173, 157, 158, 159, 160, 161, 246, 33, 130, 7, 163, 144, 145, 153, 154, 155 ],
    "right_eye" : [362, 398,384,385,386,387,388,466, 263,359, 249,390,373,374,380,381,382],
    # "right_eye" : [362,382,381,380,374,373,390,249,359,263,466,388,387,386,385,384,398,],
    "face_contour" : [10, 338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377, \
                      152, 148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109, 10],
    # "face_contour" : [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,\
    #                    152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109,10,],
    "lip" : [61, 185,40,39,37, 0, 267,269,270,409, 291, 375,321,405,314, 17, 84,181,91,146],
    # "lip" : [61, 185, 40, 39, 37, 0, 267, 270, 146, 91, 181, 84, 17, 314, 405, 321],
    # "top_lip" : [61, 185, 40, 39, 37, 0, 267, 270],
    # "bottom_lip" : [146, 91, 181, 84, 17, 314, 405, 321],
    }

    # 좌표를 저장할 리스트
    landmark_points = {
    "nose" : [],
    #"nose_masking" : [],
    "center" : [],
    "left_eye" : [],
    "right_eye" : [],
    "face_contour" : [],
    "lip" : [],
    }

    # 좌표 추출
    for part, indices in landmark_indices.items():
        for idx in indices:
            landmark = landmarks[idx]
            x = int(landmark.x * shape[1])
            y = int(landmark.y * shape[0])
            landmark_points[part].append((x,y))

    return landmark_points

if __name__ == "__main__":

    #image = cv2.imread("/home/addinedu/aris/image copy 2.png")
    cropped_face = crop_face_from_image("./image/1739411485911.jpg")
    landmark_results = get_landmark(cropped_face)
    landmark_points = get_coordinates(landmark_results, cropped_face)
    
    print("Nose Points:", landmark_points["nose"])
    #print("Nose Masking Points:", landmark_points["nose_masking"])
    print("Center Point:", landmark_points["center"])
    print("Left Eye Points:", landmark_points["left_eye"])
    print("Right Eye Points:", landmark_points["right_eye"])
    print("Face Contour Points:", landmark_points["face_contour"])
    print("lip_points", landmark_points["lip"])

    for part_name, points in landmark_points.items():
        viz_image = cropped_face.copy()
        # 랜드마크 점 표시
        for idx, point in enumerate(points):
            # 점 그리기
            cv2.circle(viz_image, point, 2, (0, 0, 255), -1)  # 빨간색 점
            # 점 번호 표시
            cv2.putText(viz_image, str(idx), point, cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1)
        # 점들을 선으로 연결
        for i in range(len(points)-1):
            cv2.line(viz_image, points[i], points[i+1], (0, 255, 0), 1)  # 초록색 선
        # 첫 점과 마지막 점 연결 (선택사항)
        if len(points) > 2:  # 점이 3개 이상일 때만
            cv2.line(viz_image, points[-1], points[0], (0, 255, 0), 1)
        # 결과 저장
        cv2.imwrite(f'./image/{part_name}_landmarks.jpg', viz_image)