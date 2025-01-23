## 부위 별 좌표 추출 ##

def get_coordinates(results, image):
  landmarks = results.multi_face_landmarks[0].landmark  # 첫 번째 얼굴의 랜드마크

  shape = image.shape
  # 코 영역에 해당하는 랜드마크 인덱스
  landmark_indices = {
  "nose" : [168,245,128,114,217,198,209,49,64,98,97,2,326,327,278,360,420,399,351],
  # "nose" : [217,198,209,49,64,98,2,326,327,278,360,420],
  "left_eye" : [ 133, 173, 157, 158, 159, 160, 161, 246, 33, 130, 7, 163, 144, 145, 153, 154, 155 ],
  "right_eye" : [362,382,381,380,374,373,390,249,359,263,466,388,387,386,385,384,398,],
  "face_contour" : [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109,10,],
  "lip" : [61, 185, 40, 39, 37, 0, 267, 270, 146, 91, 181, 84, 17, 314, 405, 321],
  # "top_lip" : [61, 185, 40, 39, 37, 0, 267, 270],
  # "bottom_lip" : [146, 91, 181, 84, 17, 314, 405, 321],
  }
  # 코 좌표를 저장할 리스트
  landmark_points = {
  "nose" : [],
  "left_eye" : [],
  "right_eye" : [],
  "face_contour" : [],
  "lip" : [],
  }
  # 좌표 추출
  for part, indices in landmark_indices.items():
      for idx in indices:
          landmark = landmarks[idx]
          x = int(landmark.x * shape[1])
          y = int(landmark.y * shape[0])
          landmark_points[part].append((x,y))

  return landmark_points

if __name__ == "__main__":
  
  import cv2
  from contour import get_contour_image
  from landmark import get_landmark

  image = cv2.imread("./25=11_Cartoonize Effect.jpg") 
  contour_image = get_contour_image(image)
  results = get_landmark(contour_image)
  landmark_points = get_coordinates(results, image)
  
  print("Nose Points:", landmark_points["nose"])
  print("Left Eye Points:", landmark_points["left_eye"])
  print("Right Eye Points:", landmark_points["right_eye"])
  print("Face Contour Points:", landmark_points["face_contour"])
  print("lip_points", landmark_points["lip"])