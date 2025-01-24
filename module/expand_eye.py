## 눈 크기 확장 ##

import cv2

def calculate_center(points):
    x_center = sum(p[0] for p in points) / len(points)
    y_center = sum(p[1] for p in points) / len(points)
    return x_center, y_center

def scale_points(points, x_center, y_center, scale_factor):
    scaled = []
    for x, y in points:
        new_x = int(x_center + (x - x_center) * scale_factor)
        new_y = int(y_center + (y - y_center) * scale_factor)
        scaled.append((new_x, new_y))
    return scaled

def expand_region(image, points, x_center, y_center, scale_factor):
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)

    # 원본 눈 영역 크기 계산
    width = x_max - x_min
    height = y_max - y_min

    # 확장된 영역 계산
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    x_min_new = max(0, int(x_center - new_width // 2))
    x_max_new = min(image.shape[1], int(x_center + new_width // 2))
    y_min_new = max(0, int(y_center - new_height // 2))
    y_max_new = min(image.shape[0], int(y_center + new_height // 2))

    # 눈 영역 추출 및 확대
    eye_region = image[y_min:y_max, x_min:x_max]
    eye_region_resized = cv2.resize(eye_region, (x_max_new - x_min_new, y_max_new - y_min_new))

    # 확대된 눈 영역 삽입
    image[y_min_new:y_max_new, x_min_new:x_max_new] = eye_region_resized

def expand_eye(original_image, left_eye_points, right_eye_points, scale_factor):
    """
    눈 영역의 좌표를 중심점 기준으로 확장하고, 원본 이미지를 유지하며 확장된 이미지를 반환하는 함수.

    :param original_image: 원본 이미지
    :param left_eye_points: 왼쪽 눈 영역의 좌표 리스트 [(x1, y1), (x2, y2), ...]
    :param right_eye_points: 오른쪽 눈 영역의 좌표 리스트 [(x1, y1), (x2, y2), ...]
    :param scale_factor: 확장 비율
    :return: 확장된 이미지
    """

    image = original_image.copy()

    # 왼쪽 눈 중심점 계산 및 확장
    left_x_center, left_y_center = calculate_center(left_eye_points)
    left_eye_points = scale_points(left_eye_points, left_x_center, left_y_center, scale_factor)
    expand_region(image, left_eye_points, left_x_center, left_y_center, scale_factor)

    # 오른쪽 눈 중심점 계산 및 확장
    right_x_center, right_y_center = calculate_center(right_eye_points)
    right_eye_points = scale_points(right_eye_points, right_x_center, right_y_center, scale_factor)
    expand_region(image, right_eye_points, right_x_center, right_y_center, scale_factor)

    # 확장된 좌표 시각화
    # for point in left_eye_points + right_eye_points:
    #     cv2.circle(image, point, radius=2, color=(0, 0, 0), thickness=-1)  # 녹색 점 표시

    return image