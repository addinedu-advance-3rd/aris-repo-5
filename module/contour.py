## 외곽선 그리기 ##
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions
import cv2
import numpy as np

def get_contour_image(image):
    # Especificar la configuración del ImageSegmenter
    options = vision.ImageSegmenterOptions(
        base_options=BaseOptions(model_asset_path="./module/selfie_multiclass_256x256.tflite"),
        output_category_mask=True,
        running_mode=vision.RunningMode.IMAGE)
    segmenter = vision.ImageSegmenter.create_from_options(options)

    # Leer la imagen de entrada
    # image = cv2.imread("/home/addinedu/dev_ws/25=11.jpg")
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_rgb = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

    # Obtener los resultados del segmentador
    segmentation_result = segmenter.segment(image_rgb)
    print("segmentation_result:", segmentation_result)
    category_mask = segmentation_result.category_mask
    confidence_masks = segmentation_result.confidence_masks

    # Convertir las máscaras en arrays de numpy
    # CONFIDENCE MASKS
    confidence_masks_np_bg = confidence_masks[0].numpy_view()
    confidence_masks_np_hair = confidence_masks[1].numpy_view()
    confidence_masks_np_body_skin = confidence_masks[2].numpy_view()
    confidence_masks_np_face_skin = confidence_masks[3].numpy_view()
    confidence_masks_np_clothes = confidence_masks[4].numpy_view()
    confidence_masks_np_others = confidence_masks[5].numpy_view()

    # CATEGORY MASK
    category_mask_np = category_mask.numpy_view()

    #print(category_mask_np.shape)
    category_mask_bgr = cv2.cvtColor(category_mask_np, cv2.COLOR_GRAY2BGR)

    #print(category_mask_bgr.shape)
    category_mask_bgr[np.where(category_mask_np == 0)] = (255, 0, 0) # Azul: Fondo
    category_mask_bgr[np.where(category_mask_np == 1)] = (0, 255, 0) # Verde: Cabello
    category_mask_bgr[np.where(category_mask_np == 2)] = (0, 0, 255) # Rojo: Piel del cuerpo
    category_mask_bgr[np.where(category_mask_np == 3)] = (255, 255, 0) # Cian: Piel de la cara
    category_mask_bgr[np.where(category_mask_np == 4)] = (255, 0, 255) # Rosa: Ropa
    category_mask_bgr[np.where(category_mask_np == 5)] = (0, 255, 255) # Amarillo: Otros

    # hair와 face_skin만 threshold로 마스크화 (예: 0.5 이상을 해당 영역으로 본다고 가정)
    hair_mask = (confidence_masks_np_hair > 0.5).astype(np.uint8)
    face_mask = (confidence_masks_np_face_skin > 0.5).astype(np.uint8)

    # 두 마스크를 합쳐서(OR 연산) "머리카락 + 얼굴피부" 영역만 살리기
    combined_mask = hair_mask | face_mask  # shape: (height, width)

    # 마스크를 3채널로 확장
    combined_mask_3ch = np.stack([combined_mask, combined_mask, combined_mask], axis=-1)

    # 원본 이미지를 복사해서 머리카락+얼굴 영역만 남기기
    contour_image = image.copy()
    contour_image[combined_mask_3ch == 0] = 0  # 마스크가 0인 부분(머리카락, 얼굴 아닌 부분)은 검정색 처리
    edges = cv2.Canny(contour_image, 100, 200)
    

    # # 외곽선 검출
    # contours_hair, _ = cv2.findContours(hair_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # contours_face, _ = cv2.findContours(face_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # combined_contours = contours_hair + contours_face
    # # 검은 배경 생성 (외곽선만 보이게)
    # contour_image = np.zeros_like(image)

    # # 외곽선 그리기 (하얀색)
    # cv2.drawContours(contour_image, combined_contours, -1, (255, 255, 255), 1)

    return contour_image 


##시각화 테스트##
if __name__ == "__main__":
    image = cv2.imread("./module/25=11_Cartoonize Effect.jpg")
    contour_image = get_contour_image(image)

    cv2.imshow("Image", contour_image)
    # cv2.imwrite('contour_image.jpg', contour_image)

    while True:
        key = cv2.waitKey(1)  # 1ms 대기
        if key == ord('q'):  # 'q' 키의 ASCII 코드 확인
            break

    # 창 닫기
    cv2.destroyAllWindows()