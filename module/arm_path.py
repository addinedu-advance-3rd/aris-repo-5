import numpy as np
import cv2
import math
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from scipy.special import comb
from .path_planning import path_planning




# image_center = (a/2,b/2)
# sticker_center = (alpha,beta)
# sticker_origin = (m,n)

alpha , beta ,n, m = 73.4 , 64.5 , -287,-68

def convert_coordinates(path,a,b):

    '''
    이미지상의 path를 실제 로봇의 path로 변환 (x,y)
    '''

    scale = (beta/b)
    converted_path = []
    converted_path.append([-218,10.2]) #시작점

    for x,y in path[1:]:
        if math.isnan(x):
            converted_path.append(('up','up'))
        else:
            y,x = int(alpha+m+(x-a)*scale),int(beta+n+(y-b)*scale) #좌표 변환
            if converted_path[-1] != (x,y): #중복 좌표 제거
                if converted_path[-1] == ('up','up'):
                    converted_path.append((x,y))
                else:
                    if (converted_path[-1][0] != x and abs(converted_path[-1][1] - y) > 1) or (converted_path[-1][1] != y and abs(converted_path[-1][0] - x) > 1): ## 2차이 이상
                        converted_path.append((x,y))
            
            # if converted_path[-1] == ('up','up'):
            #     converted_path.append((x,y))
            #     converted_path.append(('down','down'))
            # else:
            #     if converted_path[-1] != (x,y): #중복 좌표 제거
            #         converted_path.append((x,y))
    #print(converted_path[0])
    print(len(converted_path))
    return converted_path

# def del_coordinate(converted_path):
#     del_converted_path = []
#     for i in range(len(converted_path)):
#         if i//2==0:
#             x,y = 
#             del_converted_path.append()




def visualize_mapped_path(converted_path):
        """
        변환된 좌표를 종이에 시각화하는 함수.

        :param converted_path: 변환된 좌표 리스트 [(x1, y1), (x2, y2), ...]
        :param m: 종이의 왼쪽 위 x 좌표
        :param n: 종이의 왼쪽 위 y 좌표
        :param alpha: 종이 중심의 x 반지름
        :param beta: 종이 중심의 y 반지름
        """
        paper_width = alpha
        paper_height = beta

        # 종이의 영역 설정
        plt.figure(figsize=(8, 8))
        plt.xlim(m, m + paper_width)
        plt.ylim(n, n + paper_height)

        # 종이의 경계 그리기
        plt.gca().add_patch(plt.Rectangle((n, m), paper_width, paper_height, edgecolor='black', fill=False, linewidth=2))

        # 변환된 경로 시각화
        for x, y in converted_path:
            if not x == str:
                plt.scatter(x, y, c='red', s=10)  # 변환된 점을 빨간색으로 표시

        # 종이 중심 표시
        plt.scatter(m + alpha, n + beta, c='blue', label="Paper Center", s=50)

        plt.title("Mapped Path on Paper")
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.legend()
        plt.grid(True)
        plt.show()


def arm_coordinates(converted_path):
    
    '''
    (x,y)좌표를 [x,y,z,r,p,yaw]로 변환
    '''
    z,r,p,yaw = 164,130,85,-37.6 ##그림 그릴 때 초기 좌표 값
    arm_coordinates = []

    for (x,y) in converted_path:
        if x == 'up':
            arm_coordinates.append(['up'])
        elif x == 'down':
            arm_coordinates.append(['down'])
        else:
            arm_coordinates.append([x,y,z,r,p,yaw])

    # print(arm_coordinates)
    return arm_coordinates
    




# -287,-68 164 130 85 -37.6
# -158
# -158 78.8