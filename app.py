import streamlit as st
import random
import time
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 초기화
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="인터랙티브 구구단 마스터",
    page_icon="🔢",
    layout="wide"
)

# 세션 상태(Session State) 변수 초기화
if 'mode' not in st.session_state:
    st.session_state.mode = '학습 모드'
if 'num1' not in st.session_state:
    st.session_state.num1 = random.randint(2, 9)
if 'num2' not in st.session_state:
    st.session_state.num2 = random.randint(1, 9)
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'feedback' not in st.session_state:
    st.session_state.feedback = None

def generate_new_question(selected_dan=None):
    """새로운 문제를 생성하는 함수"""
    if selected_dan and selected_dan != "전체 (2~9단)":
        st.session_state.num1 = int(selected_dan.replace("단", ""))
    else:
        st.session_state.num1 = random.randint(2, 9)
    st.session_state.num2 = random.randint(1, 9)
    st.session_state.start_time = time.time()

# -----------------------------------------------------------------------------
# 2. 사이드바 (설정 및 모드 선택)
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ 설정 및 모드")
mode = st.sidebar.radio("학습 모드를 선택하세요:", ["학습 모드 (탐색)", "퀴즈 모드 (전동)"])

selected_dan = st.sidebar.selectbox(
    "연습할 단을 선택하세요:",
    ["전체 (2~9단)"] + [f"{i}단" for i in range(2, 10)]
)

if st.sidebar.button("점수 초기화"):
    st.session_state.score = 0
    st.session_state.total_questions = 0
    st.session_state.streak = 0
    st.session_state.feedback = None
    st.rerun()

# -----------------------------------------------------------------------------
# 3. 메인 화면
# -----------------------------------------------------------------------------
st.title("🔢 인터랙티브 구구단 마스터")
st.caption("수학적 시각화와 게임화 요소로 즐겁게 익히는 구구단!")

if mode == "학습 모드 (탐색)":
    st.header("🎨 시각적 개념 학습")
    st.write("곱셈은 **'같은 수의 반복된 더하기'**입니다. 시각화 그래프를 통해 곱셈의 개념을 이해해 보세요.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        dan = st.slider("단 선택", 2, 9, 3)
        multiplier = st.slider("곱하는 수 선택", 1, 9, 4)
        
        result = dan * multiplier
        st.metric(label=f"결과: {dan} × {multiplier}", value=f"= {result}")
        
        # 수식 분해 설명
        addition_str = " + ".join([str(dan)] * multiplier)
        st.info(f"💡 **수학적 의미:** {dan}을(를) {multiplier}번 더한 값입니다.\n\n`{addition_str} = {result}`")

    with col2:
        # 시각화: 묶음 크기 시각화 (Plotly)
        data = {"그룹": [f"묶음 {i+1}" for i in range(multiplier)], "개수": [dan] * multiplier}
        fig = px.bar(
            data, x="그룹", y="개수", 
            title=f"{dan}개씩 {multiplier}개 묶음",
            text="개수",
            color_discrete_sequence=['#4CAF50']
        )
        fig.update_layout(yaxis=dict(range=[0, 10]))
        st.plotly_chart(fig, use_container_width=True)

else:
    # 퀴즈 모드
    st.header("⚡ 구구단 챌린지 퀴즈")
    
    # 상단 대시보드 (통계)
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    col_stat1.metric("총 푼 문제", f"{st.session_state.total_questions} 문제")
    accuracy = (st.session_state.score / st.session_state.total_questions * 100) if st.session_state.total_questions > 0 else 0
    col_stat2.metric("정답률", f"{accuracy:.1f}%")
    col_stat3.metric("🔥 연속 정답 (Combo)", f"{st.session_state.streak} 회")
    
    st.divider()

    # 문제 표시
    n1, n2 = st.session_state.num1, st.session_state.num2
    st.subheader(f"❓ 문제:  {n1}  ×  {n2}  =  ?")
    
    # 정답 입력 폼
    with st.form(key='quiz_form', clear_on_submit=True):
        user_input = st.number_input("정답을 입력하고 Enter를 누르세요:", step=1, value=None, format="%d")
        submit_button = st.form_submit_button(label='제출하기')

    if submit_button:
        if user_input is not None:
            elapsed_time = round(time.time() - st.session_state.start_time, 2)
            correct_answer = n1 * n2
            st.session_state.total_questions += 1
            
            if user_input == correct_answer:
                st.session_state.score += 1
                st.session_state.streak += 1
                st.session_state.feedback = ("correct", f"🎉 **정답입니다!** ({elapsed_time}초 소요)")
            else:
                st.session_state.streak = 0
                st.session_state.feedback = ("wrong", f"❌ **아쉽네요!** {n1} × {n2} = {correct_answer} 입니다.")
            
            # 다음 문제 생성
            generate_new_question(selected_dan)
            st.rerun()
        else:
            st.warning("숫자를 입력해 주세요!")

    # 피드백 출력
    if st.session_state.feedback:
        status, msg = st.session_state.feedback
        if status == "correct":
            st.success(msg)
            if st.session_state.streak >= 3:
                st.balloons()
        else:
            st.error(msg)
