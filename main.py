import cv2
import argparse
from module.contour import get_contour_image
from module.landmark import get_landmark
from module.coordinate import get_coordinates
from module.expand_eye import expand_eye
from module.shrink_lip import *
from module.path import extract_skeleton,extract_trajectories
from module.contour import get_contour_image


def main(args):
     ##paser

    image = cv2.imread(args.image)

    contour_image = get_contour_image(image)

    results = get_landmark(contour_image) ## return results 랜드마크 계산

    landmark_points = get_coordinates(results, image) ## 부위별 좌표 추출

    left_eye_points = landmark_points["left_eye"]
    right_eye_points = landmark_points["right_eye"]
    lip_points = landmark_points["lip"]

    ## 눈 확장 
    expaded_eye_image = expand_eye(image,left_eye_points,right_eye_points,args.eye_scale_factor) 

    ## 입술 축소 
    inpainted_image, mask = fill_skin_color(expaded_eye_image, lip_points, args.mask_padding)

    lip_region, position = shrink_lip(image, lip_points, scale_factor=1.35)

    resized_lip_region = resize_lip(lip_region,args.lip_scale_factor)

    blended_image = blend_lip(inpainted_image, resized_lip_region, position)

    ## 선 따기 및 path 추출
    skeleton = extract_skeleton(blended_image)

    extract_trajectories(skeleton)

    print("get path!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, default="./module/25=11_Cartoonize Effect.jpg", help="입력 이미지 경로", required=False )
    parser.add_argument("--mask_padding", type=float, default=15, help="", required=False)
    parser.add_argument("--eye_scale_factor", type=float, default=1.5, help="눈 확대 비율", required=False)
    parser.add_argument("--lip_scale_factor", type=float, default=0.7, help="입 축소 비율", required=False)
    
    args= parser.parse_args()
    main(args)
