import cv2
import numpy as np
import argparse

def extract_black_outline(input_path, output_path):
    """
    이미지에서 검은색 외곽선만 정확하게 추출하는 함수
    """
    # 이미지 로드
    image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise Exception(f"이미지를 불러올 수 없습니다: {input_path}")
    
    # BGRA 이미지를 BGR로 변환
    if image.shape[-1] == 4:
        # 알파 채널이 있는 경우 흰색 배경으로 합성
        alpha = image[:,:,3] / 255.0
        image = image[:,:,:3]
        white_background = np.ones_like(image) * 255
        image = (alpha[:,:,np.newaxis] * image + (1-alpha[:,:,np.newaxis]) * white_background).astype(np.uint8)
    
    # BGR을 HSV로 변환
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # 검은색 마스크 생성 (명도가 매우 낮은 픽셀)
    black_mask = cv2.inRange(hsv, (0, 0, 0), (180, 255, 30))
    
    # 결과 이미지 생성 (검은 배경에 흰색 선)
    result = np.zeros_like(black_mask)
    result[black_mask > 0] = 255
    
    # 노이즈 제거
    kernel = np.ones((2,2), np.uint8)
    result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)
    
    # 결과 저장
    cv2.imwrite(output_path, result)
    return result

def main():
    parser = argparse.ArgumentParser(description='이미지의 검은색 외곽선 추출')
    parser.add_argument('--input', type=str, required=True, help='입력 이미지 경로')
    parser.add_argument('--output', type=str, required=True, help='출력 이미지 경로')
    
    args = parser.parse_args()
    
    try:
        extract_black_outline(args.input, args.output)
        print(f"변환 완료: {args.output}")
    except Exception as e:
        print(f"에러 발생: {str(e)}")

if __name__ == "__main__":
    main()