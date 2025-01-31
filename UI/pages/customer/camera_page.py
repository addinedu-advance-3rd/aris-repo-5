#6단계: 카메라 캡쳐 및 스케치 변환

import streamlit as st
import numpy as np
from PIL import Image
import cv2

# 스케치 변환 함수
def dodgeV2(x, y):
    return cv2.divide(x, 255 - y, scale=256)

def pencilsketch(inp_img):
    img_gray = cv2.cvtColor(inp_img, cv2.COLOR_BGR2GRAY)
    img_invert = cv2.bitwise_not(img_gray)
    img_smoothing = cv2.GaussianBlur(img_invert, (21, 21), sigmaX=0, sigmaY=0)
    final_img = dodgeV2(img_gray, img_smoothing)
    return final_img

# 카메라 캡쳐 페이지
def camera_page():
    st.title("사진 촬영 및 스케치 변환")

    # 세션 상태 초기화
    if "photos" not in st.session_state:
        st.session_state["photos"] = []  # 촬영한 사진 저장 리스트
        st.session_state["selected_photo"] = None  # 선택된 사진
        st.session_state["final_sketch"] = None  # 변환된 스케치 저장

    # 카메라 입력
    image = st.camera_input("Take a photo")

    # 사진 촬영 처리
    if image:
        # 촬영한 사진을 최대 3장까지만 저장
        if len(st.session_state["photos"]) < 3:
            st.session_state["photos"].append(image)
            st.success(f"사진이 저장되었습니다! 현재 {len(st.session_state['photos'])}/3")
        else:
            st.warning("최대 3장의 사진만 촬영할 수 있습니다!")

    # 촬영한 사진 보여주기
    if st.session_state["photos"]:
        st.subheader("촬영된 사진")
        cols = st.columns(3)  # 최대 3장의 사진을 나란히 배치
        for i, photo in enumerate(st.session_state["photos"]):
            with cols[i]:
                st.image(photo, use_column_width=True, caption=f"사진 {i + 1}")
        
        # 선택된 사진 라디오 버튼
        st.session_state["selected_photo"] = st.radio(
            "스케치 변환할 사진을 선택하세요:",
            options=list(range(len(st.session_state["photos"]))),
            format_func=lambda x: f"사진 {x + 1}",
        )

    # 스케치 변환 버튼
    if st.button("스케치 변환하기"):
        if st.session_state["selected_photo"] is not None:
            selected_index = st.session_state["selected_photo"]
            selected_image = st.session_state["photos"][selected_index]

            # PIL Image로 변환
            input_img = Image.open(selected_image)
            # 스케치 변환
            final_sketch = pencilsketch(np.array(input_img))

            # 변환된 스케치 저장
            st.session_state["final_sketch"] = final_sketch

            # 결과 표시
            st.success(f"사진 {selected_index + 1}이(가) 스케치로 변환되었습니다!")
            one, two = st.columns(2)
            with one:
                st.write("**원본 사진**")
                st.image(input_img, use_column_width=True)
            with two:
                st.write("**스케치 사진**")
                st.image(final_sketch, use_column_width=True)

            # 다운로드 버튼
            if st.button("스케치 다운로드"):
                im_pil = Image.fromarray(final_sketch)
                im_pil.save("final_sketch.jpeg")
                st.write("스케치 이미지가 'final_sketch.jpeg'로 저장되었습니다!")
        else:
            st.warning("변환할 사진을 선택하세요!")

    # 아이스크림 제조 시작 버튼
    if st.button("아이스크림 제조 시작"):
        if st.session_state["final_sketch"] is not None:
            st.session_state.page = "result_page"  # 다음 페이지로 이동
            st.rerun()
        else:
            st.warning("스케치 변환을 완료한 후에 진행해주세요!")
