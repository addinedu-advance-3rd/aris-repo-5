## 이미지에서 얼굴만 분류 ##

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0: 모든 메시지, 3: 에러만
os.environ['GLOG_minloglevel'] = '3'
import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions
import cv2
import numpy as np


def get_segment_face_image(image):
    # 이미지 세그멘테이션 모델 설정
    options = vision.ImageSegmenterOptions(
        base_options=BaseOptions(model_asset_path="./module/model/selfie_multiclass_256x256.tflite"),
        output_category_mask=True, # 분류(category) 마스크를 출력할지 여부를 결정하는 옵션
        running_mode=vision.RunningMode.IMAGE)
    segmenter = vision.ImageSegmenter.create_from_options(options)

    # 이미지 변환(mediapipe용)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_rgb = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

    # 세그멘테이션 결과
    segmentation_result = segmenter.segment(image_rgb)
    print("segmentation_result:", segmentation_result)
    category_mask = segmentation_result.category_mask # 클래스 분류
    confidence_masks = segmentation_result.confidence_masks # 특정 클래스로 분류될 확률

    # 머리카락 + 얼굴 분류
    #confidence_masks_np_bg = confidence_masks[0].numpy_view()
    confidence_masks_np_hair = confidence_masks[1].numpy_view()
    #confidence_masks_np_body_skin = confidence_masks[2].numpy_view()
    confidence_masks_np_face_skin = confidence_masks[3].numpy_view()
    #confidence_masks_np_clothes = confidence_masks[4].numpy_view()
    #confidence_masks_np_others = confidence_masks[5].numpy_view()

    # 머리카락 + 얼굴 threshold로 마스크화 (예: 0.5 이상을 해당 영역으로 본다고 가정)
    hair_mask = (confidence_masks_np_hair > 0.5).astype(np.uint8)
    face_mask = (confidence_masks_np_face_skin > 0.5).astype(np.uint8)

    # 두 마스크를 합치기
    hair_face_mask = hair_mask | face_mask  # shape: 원본 이미지 (height, width)

    # 마스크를 3채널로 확장(흑백 -> 컬러, 아래 연산 수행하기 위해 변환)
    hair_face_mask_3ch = np.stack([hair_face_mask, hair_face_mask, hair_face_mask], axis=-1)

    # 원본 이미지를 복사해서 머리카락+얼굴 영역만 남기기
    segment_face_image = image.copy()
    segment_face_image[hair_face_mask_3ch == 0] = 0

    return segment_face_image, hair_mask, face_mask


if __name__ == "__main__":
    image = cv2.imread("/home/addinedu/aris/image copy 2.png")
    segment_face_image = get_segment_face_image(image)

    cv2.imshow("Image", segment_face_image)
    # cv2.imwrite('segment_face_image.jpg', segment_face_image)

    while True:
        key = cv2.waitKey(1)  # 1ms 대기
        if key == ord('q'):  # 'q' 키의 ASCII 코드 확인
            break

    cv2.destroyAllWindows()
