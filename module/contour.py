## 이미지 경계선 검출 ##

import cv2
import numpy as np
from skimage.morphology import skeletonize
from .segment import get_segment_face_image

def simplify_skeleton(skeleton, dilate_iterations=1, erode_iterations=1, kernel_size=2):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)

    # 팽창으로 선 연결 (dilate_iterations 조절 가능)
    simplified = skeleton.astype(np.uint8)
    for _ in range(dilate_iterations):
        simplified = cv2.dilate(simplified, kernel)

    # 침식으로 선을 단순화 (erode_iterations 조절 가능)
    for _ in range(erode_iterations):
        simplified = cv2.erode(simplified, kernel)

    # 다시 스켈레톤화
    simplified = skeletonize(simplified > 0)
    return simplified

def get_contour_image(image, hair_mask, face_mask):

    # 외곽선 검출 
    contours_hair, _ = cv2.findContours(hair_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_face, _ = cv2.findContours(face_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    combined_contours = contours_hair + contours_face

    # 검은 배경 생성
    contour_image = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)

    # 외곽선 그리기
    cv2.drawContours(contour_image, combined_contours, -1, 255, 1)

    # 원본 이미지를 복사해서 얼굴 영역만 남기기
    face_mask_3ch = np.stack([face_mask, face_mask, face_mask], axis=-1)
    face_image = image.copy()
    face_image[face_mask_3ch == 0] = 0

    # 얼굴 블러 처리
    blurred = cv2.GaussianBlur(face_image, (3,3), 1.5)

    # 얼굴 엣지
    blurred_gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

    # 코 인식을 위한 명암 극대화
    cv2.imwrite('blurred_gray_before.jpg', blurred_gray)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4,4))
    blurred_gray = clahe.apply(blurred_gray)
    cv2.imwrite('blurred_gray.jpg', blurred_gray)

    edges = cv2.Canny(blurred_gray, 100, 200)

    # 외곽선 + 얼굴 엣지
    contour_image = cv2.bitwise_or(contour_image, edges)

    # 스켈레톤 처리
    skeleton = skeletonize(contour_image // 255) * 255
    simple_skeleton = simplify_skeleton(skeleton)
    contour_image = (simple_skeleton * 255).astype(np.uint8)

    cv2.imwrite('canny_img.jpg', contour_image)

    return contour_image

if __name__ == "__main__":

    image = cv2.imread("./image/25=11_Cartoonize Effect.jpg")
    segment_face_image, hair_mask, face_mask = get_segment_face_image(image)
    contour_image = get_contour_image(segment_face_image, hair_mask, face_mask)

    cv2.imshow("Image", contour_image)
    # cv2.imwrite('contour_image.jpg', contour_image)

    while True:
        key = cv2.waitKey(1)  # 1ms 대기
        if key == ord('q'):  # 'q' 키의 ASCII 코드 확인
            break

    cv2.destroyAllWindows()