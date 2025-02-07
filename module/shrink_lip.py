## 입술 축소 ##

import cv2
import numpy as np
from .segment import get_segment_face_image
from .landmark import get_landmark
from .coordinate import get_coordinates

def remove_lip(image, lip_points, mask_padding):
    """
    입술 영역과 주변을 피부색으로 채우는 함수.

    :param image: 원본 이미지
    :param lip_points: 입술 좌표 리스트 [(x1, y1), (x2, y2), ...]
    :param mask_padding: 입술 근처 마스크 영역 추가 크기
    :return: 피부색으로 채워진 이미지, 확장된 마스크
    """
    # 입술 영역 마스크 생성
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    lip_polygon = np.array(lip_points, dtype=np.int32)
    cv2.fillPoly(mask, [lip_polygon], 255)

    # 마스크 영역 확장 (입술 주변까지 포함)
    kernel = np.ones((mask_padding, mask_padding), np.uint8)
    expanded_mask = cv2.dilate(mask, kernel, iterations=1)

    # 검은색으로 마스킹
    image_masked = image.copy()
    image_masked[expanded_mask == 255] = (0, 0, 0)

    # 검은 영역을 피부색으로 채우기
    inpainted_image = cv2.inpaint(image_masked, expanded_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

    return inpainted_image

def scale_points(points, x_center, y_center, scale_factor):
    scaled = []
    for x, y in points:
        new_x = int(x_center + (x - x_center) * scale_factor)
        new_y = int(y_center + (y - y_center) * scale_factor)
        scaled.append((new_x, new_y))
    return scaled

def resize_lip_region(image, lip_points, scale_factor=1.35):
    """
    입술 영역 이미지를 생성하는 함수.
    """
    # 입술 중심점 계산
    x_center = sum(p[0] for p in lip_points) / len(lip_points)
    y_center = sum(p[1] for p in lip_points) / len(lip_points)

    shrunk_lip_points = scale_points(lip_points, x_center, y_center, scale_factor)

    # 축소된 입술 영역 생성
    x_coords = [p[0] for p in shrunk_lip_points]
    y_coords = [p[1] for p in shrunk_lip_points]
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)

    lip_region = image[y_min:y_max, x_min:x_max]
    lip_region_resized = cv2.resize(lip_region, (x_max - x_min, y_max - y_min))

    return lip_region_resized, (x_min, x_max, y_min, y_max)

def resize_lip(lip_region, lip_scale_factor=0.8):
    """
    입술 영역 축소.
    """
    resized_lip_region = cv2.resize(lip_region, None, fx=lip_scale_factor, fy=lip_scale_factor)
    
    return resized_lip_region

def blend_lip(inpainted_image, resized_lip_region, position):
    """
    축소한 입술 영역 삽입.
    """
    x_min, x_max, y_min, y_max = position

    # blended_image 생성
    blended_image = inpainted_image.copy()

    # resized_lip_region 삽입 위치 계산
    lip_height, lip_width = resized_lip_region.shape[:2]
    target_height = y_max - y_min
    target_width = x_max - x_min

    # 삽입 시작 좌표 계산
    y_start = y_min + (target_height - lip_height) // 2
    y_end = y_start + lip_height
    x_start = x_min + (target_width - lip_width) // 2
    x_end = x_start + lip_width

    # 경계 체크 (이미지 범위를 벗어나지 않도록)
    y_start = max(0, y_start)
    y_end = min(blended_image.shape[0], y_end)
    x_start = max(0, x_start)
    x_end = min(blended_image.shape[1], x_end)

    # 삽입할 영역의 크기를 resized_lip_region에 맞게 조정
    lip_region_cropped = resized_lip_region[
        0 : y_end - y_start, 0 : x_end - x_start
    ]

    # 복사
    blended_image[y_start:y_end, x_start:x_end] = lip_region_cropped

    return blended_image

def blur(image, blended_image, inpainted_image, blur_ksize=15):
    """
    입술 영역 경계 깔끔하게.
    """
    # 원본 이미지와 blended_image의 차이를 계산하여 경계 생성
    diff = cv2.absdiff(image, blended_image)

    # 차이를 강조하여 마스크 생성
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)

    # 경계 부분에 가우시안 블러 적용
    blurred_mask = cv2.GaussianBlur(mask, (blur_ksize, blur_ksize), 0)

    # 알파 블렌딩
    blurred_mask = blurred_mask / 255.0  # 정규화
    final_image = (blended_image * blurred_mask[:, :, None] + inpainted_image * (1 - blurred_mask[:, :, None])).astype(np.uint8)

    return final_image

def shrink_lip(image, lip_points, mask_padding=25):
    # 입술 지우기
    inpainted_image = remove_lip(image, lip_points, mask_padding)

    # 입술 영역 생성
    lip_region, position = resize_lip_region(image, lip_points, scale_factor=1.35)

    # 입술 축소
    resized_lip_region = resize_lip(lip_region,lip_scale_factor=0.7)

    # 입술 그리기
    shrink_lip_image = blend_lip(inpainted_image,resized_lip_region,position)

    return shrink_lip_image

if __name__ == "__main__":

    image = cv2.imread("./image/25=11_Cartoonize Effect.jpg") 
    contour_image = get_segment_face_image(image)
    results = get_landmark(contour_image)
    landmark_points = get_coordinates(results, image)

    lip_points = landmark_points["lip"]

    shrink_lip_image = shrink_lip(image, lip_points, mask_padding=25)

    cv2.imshow("Image", shrink_lip_image)
    # cv2.imwrite('contour_image.jpg', contour_image)

    while True:
        key = cv2.waitKey(1)  # 1ms 대기
        if key == ord('q'):  # 'q' 키의 ASCII 코드 확인
            break

    cv2.destroyAllWindows()