#7-1단계: 캐리커쳐 진행 시 픽업대기 안내

import streamlit as st

def result_page():
    st.title("아이스크림 제조 시작 🎉")

    if "final_sketch" in st.session_state:
        st.image(st.session_state["final_sketch"], caption="최종 선택한 스케치", use_column_width=True)
        st.write("아이스크림 제조를 시작합니다! 🚀")
    else:
        st.warning("스케치 변환된 이미지가 없습니다. 이전 단계로 돌아가세요.")
        if st.button("돌아가기"):
            st.session_state.page = "camera_page"
            st.rerun()
    
    # 처음으로 돌아가기 버튼
    if st.button("처음으로 돌아가기"):
        # 세션 상태 초기화
        st.session_state["photos"] = []  # 촬영한 사진 리스트 초기화
        st.session_state["selected_photo"] = None  # 선택된 사진 초기화
        st.session_state["final_sketch"] = None  # 변환된 스케치 초기화
        st.session_state.page = None  # start_page로 돌아가기
        st.rerun()
