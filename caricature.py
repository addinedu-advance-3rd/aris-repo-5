import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0: 모든 메시지, 3: 에러만
os.environ['GLOG_minloglevel'] = '3'
import cv2
import argparse
from module.segment import get_segment_face_image
from module.contour import get_contour_image
from module.path_planning import *
from module.arm_path import RobotPathPlanner

def get_arm_path(image_path):
    '''
    캐리커쳐 생성 및 로봇 arm path 생성
    '''

    image = cv2.imread(image_path)

    _ , hair_mask, face_mask = get_segment_face_image(image)
    
    # 컨투어
    contour_image = get_contour_image(image, hair_mask, face_mask)

    # path planning
    path = path_planning(contour_image)

    robot_path_planner = RobotPathPlanner(image)

    arm_result = robot_path_planner.run(path,image)
    print(arm_result)
    print(len(arm_result))

    return arm_result

if __name__ == "__main__":
    
    image_path = ''
    get_arm_path(image_path)
    print(get_arm_path(image_path))



