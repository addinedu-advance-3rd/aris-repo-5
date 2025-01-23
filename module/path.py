import cv2
import numpy as np
from skimage.morphology import skeletonize
from collections import deque

# !pip install scikit-image

# 스켈레톤 추출
def extract_skeleton(image):
    edges = cv2.Canny(image, 100, 200)  # 엣지 검출
    skeleton = skeletonize(edges > 0)  # 스켈레톤 추출
    return skeleton

# # 스켈레톤 단순화 (겹쳐진 선 합치기)
# def simplify_skeleton(skeleton, dilate_iterations=5, erode_iterations=0, kernel_size=1):
#     kernel = np.ones((kernel_size, kernel_size), np.uint8)

#     # 팽창으로 선 연결 (dilate_iterations 조절 가능)
#     simplified = skeleton.astype(np.uint8)
#     for _ in range(dilate_iterations):
#         simplified = cv2.dilate(simplified, kernel)

#     # 침식으로 선을 단순화 (erode_iterations 조절 가능)
#     for _ in range(erode_iterations):
#         simplified = cv2.erode(simplified, kernel)

#     # 다시 스켈레톤화
#     simplified = skeletonize(simplified > 0)
#     return simplified

# BFS 기반 경로 생성
def extract_trajectories(skeleton):
    visited = set()
    trajectories = []

    def bfs(start):
        queue = deque([start])
        path = []
        while queue:
            y, x = queue.popleft()
            if (y, x) in visited:
                continue
            visited.add((y, x))
            path.append((y, x))

            # 8방향 탐색
            for dy, dx in [(-1, -1), (-1, 0), (-1, 1),
                           (0, -1),         (0, 1),
                           (1, -1), (1, 0), (1, 1)]:
                ny, nx = y + dy, x + dx
                if 0 <= ny < skeleton.shape[0] and 0 <= nx < skeleton.shape[1]:
                    if skeleton[ny, nx] and (ny, nx) not in visited:
                        queue.append((ny, nx))
        return path

    # 스켈레톤에서 BFS 시작점 설정
    for y in range(skeleton.shape[0]):
        for x in range(skeleton.shape[1]):
            if skeleton[y, x] and (y, x) not in visited:
                trajectories.append(bfs((y, x)))

    # 경로 확인
    # print("Extracted Trajectories:", trajectories)

    return trajectories


