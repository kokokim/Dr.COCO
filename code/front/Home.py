import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys

st.set_page_config(
    page_title="COCO CHATBOT", 
    page_icon="🤖"
    )

#front 폴더
current_dir = os.path.dirname(os.path.abspath(__file__))
code_dir=os.path.dirname(current_dir)
model_dir=os.path.join(code_dir, 'model')
sys.path.append(model_dir)

import sleep

#front 폴더
script_dir = os.path.dirname(__file__)

#code 폴더
code_dir=os.path.dirname(script_dir)

#root 폴더
root_dir=os.path.dirname(code_dir)

pic_data_dir=os.path.join(root_dir, 'data', 'pic')
coco_image_path = os.path.join(pic_data_dir, 'coco.png')
style_path = os.path.join(script_dir, "style.css")

with open(style_path) as css:
    st.markdown (f'<style>{css.read()}</style>', unsafe_allow_html=True)

alarm_text=""
    
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

#Home
st.markdown(f"""
            <div class="hometitle"> Welcome to COCO CHAT👶🏻 </div>"""
            ,unsafe_allow_html=True)
st.write(" ")

# st.markdown(f"""
#             <div class="imgdiv">
#                 <img class="img", src='{coco_image_path}'>
#             </div>
#             """,
#             unsafe_allow_html=True)
st.image(coco_image_path, width=400)

st.write(" ")
st.markdown(f"""
            <div class="hometext">
                <p class="hheader">Introduce</p>
                <p class="htext"> 육아는 부모가 되는 여정 중 처음으로 마주하는 일입니다.
                 육아생활에 새로운 비전으로 저희는 2가지 챗봇 서비스를 제공합니다.
                 코코챗봇을 통해 부모가 되는 과정을 더 수월하고 편안한 경험이 되셨으면 좋겠습니다.</p>
                <p class="hheader">육아전문가</p>
                <p class="htext"> 육아에 관한 모든 질문에 답변해줍니다. 아이와 발달단계, 목욕, 이유식과 같은
                일상적인 질문부터, 복잡한 부분까지 최신 데이터 기반으로 신뢰할 수 있는 정보를 제공합니다. </p>
                <p class="hheader">제품추천가</p>
                <p class="htext"> 육아 용품을 추천해줍니다. 아이의 연령, 필요, 생활방식을 고려하여 개인화된 제품을 추천합니다.</p>
            </div>"""
            , unsafe_allow_html=True)


def gosleeptext():
    return alarm_text