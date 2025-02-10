import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0: 모든 메시지, 3: 에러만
os.environ['GLOG_minloglevel'] = '3'
import cv2
import argparse
from module.segment import get_segment_face_image
from module.landmark import get_landmark
from module.coordinate import get_coordinates
from module.expand_eye import expand_eye
from module.shrink_lip import shrink_lip
from module.contour import get_contour_image
from module.path_planning import *
from module.arm_path import RobotPathPlanner

def caricature(args):
    '''
    캐리커쳐 생성 및 로봇 arm path 생성
    '''

    image = cv2.imread(args.image)

    segment_face_image, hair_mask, face_mask = get_segment_face_image(image)

    landmark_results = get_landmark(segment_face_image) ## results 얼굴 랜드마크 계산

    landmark_points = get_coordinates(landmark_results, image) ## 부위별 좌표 추출

    contour_image = get_contour_image(image, hair_mask, face_mask)
    # path planning
    path = path_planning(contour_image)

    robot_path_planner = RobotPathPlanner(image)

    arm_result = robot_path_planner.run(path,image)
    print(arm_result)
    print(len(arm_result))

    return arm_result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, default="/home/addinedu/aris/image copy 3.png", help="입력 이미지 경로", required=False)
    parser.add_argument("--mask_padding", type=float, default=16, help="", required=False)
    parser.add_argument("--eye_scale_factor", type=float, default=1.0, help="눈 확대 비율", required=False)
    parser.add_argument("--lip_scale_factor", type=float, default=1.0, help="입 축소 비율", required=False)
    parser.add_argument("--output_dir", type=str, default="/home/addinedu/aris/aris-repo-5_통신/cari_image",
                        help="결과 이미지 저장 경로", required=False)
    
    args= parser.parse_args()
    caricature(args)
    print(caricature(args))
