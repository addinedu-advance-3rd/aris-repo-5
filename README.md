get caricature and path /
│
├── main.py               # 실행 파일
├── modules/              # 기능별 모듈 디렉토리
│   ├── contour.py        # 얼굴 윤곽선 따기
│   ├── landmark.py       # 얼굴 랜드마크 계산
│   ├── coordinate.py     # 부위 별 좌표 추출
│   ├── expand_eye.py     # 눈 확장
│   ├── shrink_lip.py     # 입 축소
│   ├── segment.py        # 얼굴,머리부분만 추출
│   └── path.py           # 스켈레톤화 및 path 추출
│
└── requirements.txt 