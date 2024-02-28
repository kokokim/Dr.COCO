# Import required libraries
import sys
import os
import time
import streamlit as st
from openai import OpenAI
import json

# st.set_page_config(
#     page_title="COCO CHATBOT", 
#     page_icon="🤖"
#     )

# 현재 스크립트의 디렉토리 (pages 폴더)
current_dir = os.path.dirname(os.path.abspath(__file__))

# pages 폴더의 상위 폴더 (front 폴더)로 이동
app_dir = os.path.dirname(current_dir)

# app 폴더의 상위 폴더 (code 폴더)로 이동
code_dir = os.path.dirname(app_dir)

# model 폴더의 절대 경로를 구성
model_dir = os.path.join(code_dir, 'model')

# sys.path에 model 폴더의 경로 추가
sys.path.append(model_dir)
sys.path.append(app_dir)

import baby
import sleep
import Home

os.environ['OPENAI_API_KEY'] = st.secrets["OPENAI_API_KEY"]
os.environ["TOKENIZERS_PARALLELISM"] = st.secrets["TOKENIZERS_PARALLELISM"]

client = OpenAI()
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
            <div class="babytitle">COCO CHATBOT🤖</div>
            <p class="babytext"> 안녕하세요. 코코박사입니다. 원하시는 질문의 카테고리를 선택해주세요.</p>
            """,
            unsafe_allow_html=True)
option=st.selectbox(
    "카테고리 선택창",
    ("신생아", "수유", "성장 및 발달", "육아", "지원제도", "이유식"),
    index=None,
    placeholder="Category...",
)

# 카테고리 매핑
categories = {
    "신생아": "raisebaby",
    "수유": "breastfeeding",
    "성장 및 발달": "growanddevelopment",
    "육아": "basicparenting",
    "지원제도": "supportsystem",
    "이유식": "babyfood"
}
    
if "page1_messages" not in st.session_state: # Initialize the chat message history
    st.session_state.page1_messages = [
        {"role": "assistant", 
        "content": """안녕하세요. 코코박사입니다. 무엇이 궁금하신가요?"""}
    ]

# 사용자 입력 프롬프트 및 메시지 기록 표시
if prompt := st.chat_input("질문을 입력해주세요"): # Prompt for user input and save to chat history
    if option:
        st.session_state.page1_messages.append({"role": "user", "content": prompt}) #prompt에 답변 저장
    else:
        st.warning('카테고리를 선택해주세요', icon="⚠️")


for message in st.session_state.page1_messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

        
def stream_data(data):
    for word in data.split():
        yield word + " "
        time.sleep(0.07)
    
def generate_img(answer):
    enhanced_prompt = f"""{answer}
                    Create an illustration depicting a warm and intimate family atmosphere.
                    The image should capture a happy Korean family or a baby. The characters should be dressed in casual attire, each with a soft smile.
                    The color palette should be gentle and warm, contributing to an overall sense of warmth and happiness.
                    """ 

    response=client.images.generate(
        model="dall-e-3",
                prompt=enhanced_prompt,  # 답변을 기반으로 프롬프트 설정
                size="1024x1024",
                quality="standard",
                n=1,
    )
    image_url=response.data[0].url
    return image_url

def save_data(image_url, question, answer, filename="picture.json"):
    # 파일이 존재하면 기존 데이터를 불러오고, 그렇지 않으면 빈 리스트를 생성
    if os.path.exists(filename):
        with open(filename, "r") as file:
            try:
                data = json.load(file)
                # 불러온 데이터가 딕셔너리 타입이면 리스트로 변환
                if isinstance(data, dict):
                    data = [data]
            except json.JSONDecodeError:  # 파일이 비어있는 경우
                data = []
    else:
        data = []
    
    # 새로운 데이터 추가
    new_entry = {
        "image_url": image_url,
        "metadata": {
            "question": question,
            "answer": answer
        }
    }
    data.append(new_entry)  # 이 부분에서 오류가 발생했었습니다
    
    # 파일에 업데이트된 데이터 저장
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
        
def load_data(filename="picture.json"):
    with open(filename, "r") as file:
        data=json.load(file)
    return data
        
# 쿼리를 채팅 엔진에 전달하고 응답을 표시
if st.session_state.page1_messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = baby.main(categories.get(option), prompt)
            st.write_stream(stream_data(response))
            img=generate_img(response)
            img_url=img
            st.image(img)
            save_data(img, prompt, response)
            print(load_data())
            message = {"role": "assistant", "content": response}
            st.session_state.page1_messages.append(message) # Add response to message history
            
