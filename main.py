import cv2
import argparse
from module.segment import get_segment_face_image
from module.landmark import get_landmark
from module.coordinate import get_coordinates
from module.expand_eye import expand_eye
from module.shrink_lip import shrink_lip
from module.contour import get_contour_image
from module.path_planning import *
from module.arm_path import convert_coordinates, visualize_mapped_path, arm_coordinates

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
    #print(path)

    a,b,_ = image.shape
    converted_path = convert_coordinates(path,a,b)
    #print(converted_path)
    # visualize_mapped_path(converted_path)
    arm_result = arm_coordinates(converted_path)
    print(converted_path)
    
    return arm_result
    
    # cv2.imshow("Image", shrink_lip_image)
    # # cv2.imwrite('contour_image.jpg', contour_image)

    # while True:
    #     key = cv2.waitKey(1)  # 1ms 대기
    #     if key == ord('q'):  # 'q' 키의 ASCII 코드 확인
    #         break

    # cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, default="/home/addinedu/aris/123/aris-repo-5/module/image/25=11_Cartoonize Effect.jpg", help="입력 이미지 경로", required=False)
    parser.add_argument("--mask_padding", type=float, default=23, help="", required=False)
    parser.add_argument("--eye_scale_factor", type=float, default=1.3, help="눈 확대 비율", required=False)
    parser.add_argument("--lip_scale_factor", type=float, default=0.7, help="입 축소 비율", required=False)
    
    args= parser.parse_args()
    main(args)
