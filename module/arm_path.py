import numpy as np
import cv2
import math
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from scipy.special import comb
from .path_planning import path_planning


class RobotPathPlanner:
    '''이미지 경로를 로봇 경로로 변환'''
    def __init__(self,image):

        self.converted_path = []
        self.image = image

    def convert_coordinates(self,path,image):
        '''
        이미지상의 path를 실제 로봇의 path로 변환 (x,y)
        image_center = (a/2,b/2)
        sticker_center = (alpha,beta)
        sticker_origin = (m,n) (가장 왼쪽 위 좌표)
        '''
        alpha , beta ,n, m = 92 , 94 , -268 ,-102.2

        if len(image.shape) == 3:
            a,b,_ = image.shape
        else:
            a,b = image.shape
        
        print(a,b)

        scale = (beta/b)
        self.converted_path.append([-212,-57]) #시작점

        for x,y in path[1:]:
            if math.isnan(x):
                self.converted_path.append(('up','up'))
            else:
                y,x = int(alpha+m+(x-a)*scale),int(beta+n+(y-b)*scale) #좌표 변환
                if self.converted_path[-1] != (x,y): #중복 좌표 제거
                    if self.converted_path[-1] == ('up','up'):
                        self.converted_path.append((x,y))
                    else:
                        if (self.converted_path[-1][0] != x and abs(self.converted_path[-1][1] - y) > 2) or (self.converted_path[-1][1] != y and abs(self.converted_path[-1][0] - x) > 2): ## 2차이 이상
                            self.converted_path.append((x,y))
        
    def del_up(self):
        '''
        불필요한 ('up','up') 제거
        '''
        arm_path = []
        for i in range(len(self.converted_path)-1):
            if self.converted_path[i][0] == 'up':
                if abs(self.converted_path[i-1][0]-self.converted_path[i+1][0]) > 2 or abs(self.converted_path[i-1][1]-self.converted_path[i+1][1]) > 2 :
                    arm_path.append(self.converted_path[i])
            else :
                arm_path.append(self.converted_path[i])
        arm_path.append(('up','up')) 

        self.converted_path = arm_path

    def add_down(self):
        i=1
        while i <len(self.converted_path) -2 :
            if self.converted_path[i][0] == 'up':
                self.converted_path.insert(i+2,('down','down'))
                i+=1
            i+=1

    def arm_coordinates(self):
        
        '''
        (x,y)좌표를 [x,y,z,r,p,yaw]로 변환
        '''

        z,r,p,yaw = 150.5,74.4,86.6,-105.4 ##그림 그릴 때 초기 좌표 값

        ## 초기값 세팅
        arm_coordinates = [[self.converted_path[0][0],self.converted_path[0][1],z+10,r,p,yaw]
                           ,[self.converted_path[1][0],self.converted_path[1][1],z+10,r,p,yaw]]

        for (x,y) in self.converted_path[1:]:
            if arm_coordinates[-1] == ['up']:
                arm_coordinates.append([x,y,160.5,r,p,yaw])
            else :    
                if x == 'up':
                    arm_coordinates.append(['up'])
                elif x == 'down':
                    arm_coordinates.append(['down'])
                else:
                    arm_coordinates.append([x,y,z,r,p,yaw])
        #print('arm_coods =' , arm_coordinates)
        return arm_coordinates

    def run(self,path,image):
        '''
        전체 과정 실행
        '''
        self.convert_coordinates(path,image)
        self.del_up()
        self.add_down()
        
        return self.arm_coordinates()