import os
import sys
import streamlit as st

# 현재 스크립트의 디렉토리 (pages 폴더)
current_dir = os.path.dirname(os.path.abspath(__file__))

# pages 폴더의 상위 폴더 (app 폴더)로 이동
app_dir = os.path.dirname(current_dir)

# app 폴더의 상위 폴더 (code 폴더)로 이동
code_dir = os.path.dirname(app_dir)

# model 폴더의 절대 경로를 구성
model_dir = os.path.join(code_dir, 'model')

# sys.path에 model 폴더의 경로 추가
sys.path.append(model_dir)
sys.path.append(app_dir)

import product
import sleep
import Home

os.environ['OPENAI_API_KEY'] = st.secrets["OPENAI_API_KEY"]
os.environ["TOKENIZERS_PARALLELISM"] = st.secrets["TOKENIZERS_PARALLELISM"]

# st.set_page_config(
#     page_title="COCO CHATBOT", 
#     page_icon="🤖"
#     )
alarm_text=Home.gosleeptext()

script_dir = os.path.dirname(__file__)
style_path = os.path.join(script_dir, "../style.css")

with open(style_path) as css:
    st.markdown (f'<style>{css.read()}</style>', unsafe_allow_html=True)
    
#사이드바
st.sidebar.markdown(f"""
                    <div class="sleepreport">🌙어제의 동동이 수면레포트🌙</div>
                    """, unsafe_allow_html=True)
st.sidebar.write("")

if alarm_text:
    st.sidebar.markdown(f"""
    <div class="sleeptext"> {alarm_text} </div>""",
    unsafe_allow_html=True
    )
else:
    alarm_text+=sleep.main()
    st.sidebar.markdown(f"""
    <div class="sleeptext"> {alarm_text} </div>""",
    unsafe_allow_html=True
    )
    
st.sidebar.divider()
st.sidebar.markdown(f"""
                   <div class="lasttext">Dr.COCO는 부모의 짧은 휴식을 최우선 가치로 생각하고 모든 물음에 대해 신뢰로 응답하겠습니다.</div>""", unsafe_allow_html=True)


st.markdown(f"""
            <div class="producttitle">COCO PRODUCTBOT🍼</div>
            <p class="producttext"> 코코 제품추천챗봇입니다. 원하시는 질문을 입력해주세요.</p>
            """,
            unsafe_allow_html=True
            )
# st.text("현재 추천가능한 상품은 젖병, 유모차, 로션 입니다.")
    
if "page2_messages" not in st.session_state: # Initialize the chat message history
    st.session_state.page2_messages = [
        {"role": "assistant", 
        "content": """안녕하세요. 코코박사입니다. 무엇을 찾으시나요?"""}
    ]

# 사용자 입력 프롬프트 및 메시지 기록 표시
if prompt := st.chat_input("질문을 입력해주세요"): # Prompt for user input and save to chat history
    st.session_state.page2_messages.append({"role": "user", "content": prompt}) #prompt에 답변 저장
        
for message in st.session_state.page2_messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        
# 쿼리를 채팅 엔진에 전달하고 응답을 표시
if st.session_state.page2_messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = product.main(prompt)
            # response="ahahaha"
            st.write(response)
            message = {"role": "assistant", "content": response}
            st.session_state.page2_messages.append(message) # Add response to message history