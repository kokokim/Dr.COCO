# Import required libraries
# import test

import sys
sys.path.append('/mnt/c/KIMSEONAH/Test_Study/Chatbot/Dr.COCO/model')
import product

from dotenv import load_dotenv
import streamlit as st
from streamlit_chat import message


# Load environment variables
load_dotenv()

# 세션 상태 변수 초기화
st.set_page_config(page_title="COCO PRODUCTBOT")
st.title("COCO PRODUCTBOT")
st.text("안녕하세요. 코코 제품추천챗봇입니다. 원하시는 질문을 입력해주세요.")
# st.text("현재 추천가능한 상품은 젖병, 유모차, 로션 입니다.")
st.divider()
    
if "page2_messages" not in st.session_state: # Initialize the chat message history
    st.session_state.page2_messages = [
        {"role": "assistant", 
         "content": """안녕하세요. 코코박사입니다. 무엇을 찾으시나요?"""}
    ]

# 사용자 입력 프롬프트 및 메시지 기록 표시
if prompt := st.chat_input("답변을 입력해주세요"): # Prompt for user input and save to chat history
    st.session_state.page2_messages.append({"role": "user", "content": prompt}) #prompt에 답변 저장
        
for message in st.session_state.page2_messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        
# 쿼리를 채팅 엔진에 전달하고 응답을 표시
if st.session_state.page2_messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = product.main(prompt)
            st.write(response)
            message = {"role": "assistant", "content": response}
            st.session_state.page2_messages.append(message) # Add response to message history