# Import required libraries
import sys
import os

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

import baby

import streamlit as st
from openai import OpenAI
from PIL import Image # 위에서 선언 후 사용해야한다.

client = OpenAI()

# Load environment variables
st.set_page_config(page_title="COCO CHATBOT", page_icon="")
st.title("COCO CHATBOT")
st.text("안녕하세요. 코코박사입니다. 원하시는 질문의 카테고리를 선택해주세요")
option=st.selectbox(
    "원하는 질문의 카테고리는?",
    ("신생아", "수유", "성장 및 발달", "육아", "지원제도", "이유식"),
    index=None,
    placeholder="Category...",
)
st.write('You selected:', option)
st.divider()

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
if prompt := st.chat_input("답변을 입력해주세요"): # Prompt for user input and save to chat history
    if option:
        st.session_state.page1_messages.append({"role": "user", "content": prompt}) #prompt에 답변 저장
    else:
        st.warning(' 카테고리를 선택해주세요', icon="⚠️")
        st.info('카테고리를 선택해주세요', icon='⚠️')
        # 🤖🚨🔥⚠️
        
for message in st.session_state.page1_messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        
def generate_img(answer):
    enhanced_prompt = f"{answer} The setting is after the year 2000, featuring Korean people, with no text included, and the image type should look like a real photograph."
    response=client.images.generate(
        model="dall-e-3",
                prompt=enhanced_prompt,  # 답변을 기반으로 프롬프트 설정
                size="1024x1024",
                quality="standard",
                n=1,
    )
    image_url=response.data[0].url
    return image_url
        
# 쿼리를 채팅 엔진에 전달하고 응답을 표시
if st.session_state.page1_messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = baby.main(categories.get(option), prompt)
            st.write(response)
            img=generate_img(response)
            st.image(img)
            message = {"role": "assistant", "content": response}
            st.session_state.page1_messages.append(message) # Add response to message history
            

