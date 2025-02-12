import os
import cv2
import argparse
from module.crop_image import crop_face_from_image
from module.segment import get_segment_face_image
from module.landmark import get_landmark
from module.coordinate import get_coordinates
from module.contour import get_contour_image
from module.overlay_nose import *
from module.path_planning import *
from module.arm_path import RobotPathPlanner

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0: 모든 메시지, 3: 에러만
os.environ['GLOG_minloglevel'] = '3'

def get_arm_path(image_path):
    '''
    캐리커쳐 생성 및 로봇 arm path 생성
    '''

    image = crop_face_from_image(image_path)

    image = crop_face_from_image(image)
    if image == None:
        return None

    _ , hair_mask, face_mask = get_segment_face_image(image)
    
    landmark_results = get_landmark(image)

    landmark_points = get_coordinates(landmark_results)
    nose_points = landmark_points["nose"]
    center_point = landmark_points["center"]

    # 컨투어
    contour_image = get_contour_image(image, hair_mask, face_mask)

    # 코 합성
    print("코 합성을 시작합니다.")
    contour_image = nose_masking(contour_image, nose_points)
    contour_image = overlay_nose(contour_image, center_point)

    # path planning
    path = path_planning(contour_image)

    robot_path_planner = RobotPathPlanner(image)

    arm_result = robot_path_planner.run(path,image)
    print(arm_result)

    return arm_result

if __name__ == "__main__":
    
    image_path = ''
    get_arm_path(image_path)
    print(get_arm_path(image_path))



