import cv2
import argparse
from module.segment import get_segment_face_image
from module.landmark import get_landmark
from module.coordinate import get_coordinates
from module.expand_eye import expand_eye
from module.shrink_lip import shrink_lip
from module.contour import get_contour_image
from module.path_planning import *


def main(args):

    image = cv2.imread(args.image)

    segment_face_image, hair_mask, face_mask = get_segment_face_image(image)

    landmark_results = get_landmark(segment_face_image) ## results 얼굴 랜드마크 계산

    landmark_points = get_coordinates(landmark_results, image) ## 부위별 좌표 추출

    left_eye_points = landmark_points["left_eye"]
    right_eye_points = landmark_points["right_eye"]
    lip_points = landmark_points["lip"]

    # 눈 확장 
    expaded_eye_image = expand_eye(image, left_eye_points, right_eye_points, args.eye_scale_factor) 

    # 입술 축소 
    shrink_lip_image = shrink_lip(expaded_eye_image, lip_points, args.mask_padding)

    # 컨투어
    contour_image = get_contour_image(shrink_lip_image, hair_mask, face_mask)

    # path planning
    path = path_planning(contour_image)
    print(path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, default="./module/image/25=11_Cartoonize Effect.jpg", help="입력 이미지 경로", required=False)
    parser.add_argument("--mask_padding", type=float, default=15, help="", required=False)
    parser.add_argument("--eye_scale_factor", type=float, default=1.2, help="눈 확대 비율", required=False)
    parser.add_argument("--lip_scale_factor", type=float, default=0.7, help="입 축소 비율", required=False)
    
    args= parser.parse_args()
    main(args)
