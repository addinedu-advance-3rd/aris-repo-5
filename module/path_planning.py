# import cv2
# import numpy as np
# from scipy.spatial.distance import cdist




# class ImagePathPlanner:
#     '''
#     이미지 path 생성
#     '''

#     # 8방향 (좌측부터 시계방향)
#     DIRECTIONS = [
#         (-1,  0),  # 왼쪽
#         (-1,  1),  # 왼쪽 위 대각선
#         ( 0,  1),  # 위
#         ( 1,  1),  # 오른쪽 위 대각선
#         ( 1,  0),  # 오른쪽
#         ( 1, -1),  # 오른쪽 아래 대각선
#         ( 0, -1),  # 아래
#         (-1, -1)   # 왼쪽 아래 대각선
#     ]

#     def __init__(self,image,DIRECTIONS,current_pos,prev_direction):
#         self.DIRECTIONS = DIRECTIONS

    
    
#     def find_next_pixel(self,image, current_pos, prev_direction):
#         """ 현재 전진 방향을 우선 고려하여 8방향 탐색 후, 없으면 가까운 흰색 픽셀 탐색 수행 """
#         x, y = current_pos
#         h, w = image.shape

#         # 1. 저장된 전진 방향부터 탐색
#         directions = [prev_direction] + [d for d in self.DIRECTIONS if d != prev_direction]

#         for dx, dy in directions:
#             nx, ny = x + dx, y + dy
#             if 0 <= nx < h and 0 <= ny < w and image[nx, ny] == 255:  # 경로 존재 확인
#                 return (nx, ny), (dx, dy)

#         # 2. 모든 방향에서 경로를 찾지 못했을 경우, 가까운 흰색 픽셀 탐색
#         return None, None

#     def find_nearest_white_pixel(self,image, current_pos):
#         """ 가까운 흰색 픽셀 찾기 """
#         # 흰색 픽셀 좌표 찾기
#         white_pixels = np.argwhere(image == 255)
        
#         if len(white_pixels) == 0:
#             return None  # 더 이상 탐색할 픽셀 없음

#         # 가장 가까운 흰색 픽셀 찾기
#         distances = cdist([current_pos], white_pixels)
#         nearest_pixel_idx = np.argmin(distances)
        
#         return tuple(white_pixels[nearest_pixel_idx])

#     def find_path(self,image, start_pos):
#         """ 이미지 기반 경로 탐색 """
#         current_pos = start_pos
#         prev_direction = (0, 1)  # 기본 전진 방향 (오른쪽)
#         path = [current_pos]

#         while True:
#             next_pos, direction = self.find_next_pixel(image, current_pos, prev_direction)

#             if next_pos is None:
#                 path.append((np.nan, np.nan))
#                 next_pos = self.find_nearest_white_pixel(image, current_pos)
#                 if next_pos is None:
#                     break  # 더 이상 이동할 경로 없음

#             path.append(next_pos)
#             current_pos = next_pos
#             prev_direction = direction if direction else prev_direction  # 방향 갱신

#             # 경로를 지나간 것으로 처리
#             image[current_pos] = 0

#         return path

#     # 이미지 로드 및 이진화
#     def load_binary_image(self,path):
#         """ 이미지 로드 후 이진화 """
#         image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
#         _, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)
#         return binary_image

#     # 시작점 찾기
#     def find_start_point(self,image):
#         """ 이미지에서 가장 먼저 나오는 흰색 픽셀을 시작점으로 설정 """
#         white_pixels = np.argwhere(image == 255)
#         return tuple(white_pixels[0]) if len(white_pixels) > 0 else None

#     def path_planning(self,image):
#             # path planning
#         start_pos = self.find_start_point(image)

#         if start_pos:
#             path = self.find_path(image, start_pos)
#         else:
#             return None

#         return path

# if __name__ == "__main__":

#     image_path = "./image/25=11_Cartoonize Effect.jpg"  # 경로 이미지 파일
#     image = load_binary_image(image_path)
    
#     start_pos = find_start_point(image)
#     if start_pos:
#         path = path_planning(image, start_pos)
#     else:
#         print("경로를 찾을 수 없습니다.")

import cv2
import numpy as np
from scipy.spatial.distance import cdist

# 8방향 (좌측부터 시계방향)
DIRECTIONS = [
    (-1,  0),  # 왼쪽
    (-1,  1),  # 왼쪽 위 대각선
    ( 0,  1),  # 위
    ( 1,  1),  # 오른쪽 위 대각선
    ( 1,  0),  # 오른쪽
    ( 1, -1),  # 오른쪽 아래 대각선
    ( 0, -1),  # 아래
    (-1, -1)   # 왼쪽 아래 대각선
]
def find_next_pixel(image, current_pos, prev_direction):
    """ 현재 전진 방향을 우선 고려하여 8방향 탐색 후, 없으면 가까운 흰색 픽셀 탐색 수행 """
    x, y = current_pos
    h, w = image.shape

    # 1. 저장된 전진 방향부터 탐색
    directions = [prev_direction] + [d for d in DIRECTIONS if d != prev_direction]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < h and 0 <= ny < w and image[nx, ny] == 255:  # 경로 존재 확인
            return (nx, ny), (dx, dy)

    # 2. 모든 방향에서 경로를 찾지 못했을 경우, 가까운 흰색 픽셀 탐색
    return None, None

def find_nearest_white_pixel(image, current_pos):
    """ 가까운 흰색 픽셀 찾기 """
    # 흰색 픽셀 좌표 찾기
    white_pixels = np.argwhere(image == 255)
    
    if len(white_pixels) == 0:
        return None  # 더 이상 탐색할 픽셀 없음

    # 가장 가까운 흰색 픽셀 찾기
    distances = cdist([current_pos], white_pixels)
    nearest_pixel_idx = np.argmin(distances)
    
    return tuple(white_pixels[nearest_pixel_idx])

def find_path(image, start_pos):
    """ 이미지 기반 경로 탐색 """
    current_pos = start_pos
    prev_direction = (0, 1)  # 기본 전진 방향 (오른쪽)
    path = [current_pos]

    while True:
        next_pos, direction = find_next_pixel(image, current_pos, prev_direction)

        if next_pos is None:
            path.append((np.nan, np.nan))
            next_pos = find_nearest_white_pixel(image, current_pos)
            if next_pos is None:
                break  # 더 이상 이동할 경로 없음

        path.append(next_pos)
        current_pos = next_pos
        prev_direction = direction if direction else prev_direction  # 방향 갱신

        # 경로를 지나간 것으로 처리
        image[current_pos] = 0

    return path

# 이미지 로드 및 이진화
def load_binary_image(path):
    """ 이미지 로드 후 이진화 """
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    _, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)
    return binary_image

# 시작점 찾기
def find_start_point(image):
    """ 이미지에서 가장 먼저 나오는 흰색 픽셀을 시작점으로 설정 """
    white_pixels = np.argwhere(image == 255)
    return tuple(white_pixels[0]) if len(white_pixels) > 0 else None

def path_planning(image):
        # path planning
    start_pos = find_start_point(image)

    if start_pos:
        path = find_path(image, start_pos)
        print(path)
    else:
        return None

    return path

if __name__ == "__main__":

    image_path = "./image/25=11_Cartoonize Effect.jpg"  # 경로 이미지 파일
    image = load_binary_image(image_path)
    
    start_pos = find_start_point(image)
    if start_pos:
        path = path_planning(image, start_pos)
    else:
        print("경로를 찾을 수 없습니다.")