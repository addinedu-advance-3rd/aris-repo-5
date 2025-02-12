## 코 합성 ##
import cv2
import numpy as np
from module.contour import simplify_skeleton
from skimage.morphology import skeletonize
from pathlib import Path
import random

expanded_hull = []

def nose_masking(contour_image, nose_points):
    
    global expanded_hull
    
    offset = 15  # 마스크 크기를 얼마나 키울지 설정 (픽셀 단위)
    
    # NumPy 배열로 변환
    nose_points = np.array(nose_points, dtype=np.int32)

    # Convex Hull 적용 (코 부분 외곽선 만들기)
    hull = cv2.convexHull(nose_points)

    # 마스크 크기 키우기 (외곽선 확장)
    M = cv2.moments(hull)
    if M['m00'] != 0:
        cx = int(M['m10'] / M['m00'])  # 중심점 x
        cy = int(M['m01'] / M['m00'])  # 중심점 y
        # 중심점을 기준으로 확장
        for point in hull:
            x, y = point[0]
            # 중심점에서 바깥쪽으로 offset만큼 확장
            new_x = x + (x - cx) * offset // 50
            new_y = y + (y - cy) * offset // 50
            expanded_hull.append([new_x, new_y])
        expanded_hull = np.array(expanded_hull, dtype=np.int32)

    # 확장된 코 부분 검은색으로 채우기
    cv2.fillPoly(contour_image, [expanded_hull], (0, 0, 0))

    return contour_image

def overlay_nose(contour_image, center_point):

    global expanded_hull

    nose_list = ["nose_1", "nose_2", "nose_3", "nose_4_moustache", "nose_dog_1", "nose_dog_2", "nose_dog_3", "nose_cat_1"]

    '''
    # 코 이미지 로드
    if Path(nose).is_file():
        animal_nose = cv2.imread(nose, cv2.IMREAD_GRAYSCALE)
    else:
        if "dog" in nose:
            print("개코를 랜덤하게 결정합니다.")
            nose = random.choice(nose_list[4:7])
        elif "cat" in nose:
            print("고양이코를 랜덤하게 결정합니다.")
            nose = random.choice(nose_list[8:])
        else:
            print("사람 코를 랜덤하게 결정합니다.")
            nose = random.choice(nose_list[:3])
        animal_nose = cv2.imread("./noses/" + nose + ".jpg", cv2.IMREAD_GRAYSCALE)
    if animal_nose is None:
        raise FileNotFoundError("코 이미지를 불러올 수 없습니다.")
    '''

    nose = random.choice(nose_list)
    nose = cv2.imread("./image/nose/" + nose + ".jpg", cv2.IMREAD_GRAYSCALE)

    # 얼굴 사진에서 마스킹된 코 영역의 바운딩 박스 계산
    x, y, w, h = cv2.boundingRect(expanded_hull)

    # 불러온 코의 흰색 contour 부분만 찾고 추출
    _, nose_binary = cv2.threshold(nose, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(nose_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    nose_contour = max(contours, key=cv2.contourArea)
    nose_x, nose_y, nose_w, nose_h = cv2.boundingRect(nose_contour)
    nose_roi = nose[nose_y:nose_y+nose_h, nose_x:nose_x+nose_w]

    ## Resize
    # 마스킹된 얼굴 코 영역에 맞게 합성할 코 크기 조절
    padding = 5  # 여유 공간
    target_w = w - 2*padding
    target_h = h - 2*padding
    # 원본 비율 유지하면서 최종 target 크기 계산
    aspect_ratio = nose_w / nose_h
    if w/h > aspect_ratio:
        target_h = h - 2*padding
        target_w = int(target_h * aspect_ratio)
        if target_w > (w - 2*padding):
            target_w = w - 2*padding
            target_h = int(target_w / aspect_ratio)
    else:
        target_w = w - 2*padding
        target_h = int(target_w / aspect_ratio)
        if target_h > (h - 2*padding):
            target_h = h - 2*padding
            target_w = int(target_h * aspect_ratio)
    resized_nose = cv2.resize(nose_roi, (target_w, target_h), interpolation=cv2.INTER_AREA)

    # 최종 이진화
    _, resized_nose = cv2.threshold(resized_nose, 127, 255, cv2.THRESH_BINARY)

    ## 스켈레톤 처리
    resized_nose = (simplify_skeleton(skeletonize(resized_nose // 255) * 255) * 255).astype(np.uint8)

    ## 코 합성될 위치 계산 (중앙 정렬)
    center_x = center_point[0][0]
    center_y = center_point[0][1]
    paste_x = center_x - target_w//2
    paste_y = center_y - target_h//2

    # expanded_hull의 경계 확인
    hull_x, hull_y, hull_w, hull_h = cv2.boundingRect(expanded_hull)
    paste_x = max(hull_x + padding, min(paste_x, hull_x + hull_w - target_w - padding))
    paste_y = max(hull_y + padding, min(paste_y, hull_y + hull_h - target_h - padding))

    ## 코 합성
    mask = np.zeros(contour_image.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [expanded_hull], 255)
    
    # contour 이미지에 합성 (단일 채널)
    roi = contour_image[paste_y:paste_y+target_h, paste_x:paste_x+target_w]
    roi[:] = cv2.bitwise_or(roi, resized_nose)
    cv2.imwrite('canny_with_overlayed_nose.jpg', contour_image)

    return contour_image