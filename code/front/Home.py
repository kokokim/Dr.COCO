import streamlit as st

st.set_page_config(
    page_title="COCO CHATBOT",
    page_icon="👶🏻",
)   
with open("style.css") as css:
    st.markdown (f'<style>{css.read()}</style>', unsafe_allow_html=True)

    st.sidebar.text("Dr.COCO는 부모의 잠깐의 휴식을 \n최우선 가치로 생각합니다.")

    st.write("# Welcome to COCO CHAT👶🏻")
    st.write(" ")

    st.image('../../data/pic/coco.png', width=400)

    st.write(" ")
    st.text(
        "# Introduce\n"
        "육아는 부모가 되는 여정 중 처음으로 마주하는 일입니다.\n"
        "육아생활에 새로운 비전으로 저희는 2가지 챗봇 서비스를 제공합니다. \n"
        "코코챗봇을 통해 부모가 되는 과정을 더 수월하고 편안한 경험이 되셨으면 좋겠습니다.\n\n"
        "# FIRST 육아전문가 \n"
        "육아에 관한 모든 질문에 답변해줍니다. 아이와 발달단계, 목욕, 이유식과 같은"
        "일상적인 질문부터, 복잡한 부분까지 최신 데이터 기반으로 신뢰할 수 있는 정보를 제공합니다. \n\n"
        "# SECOND 제품추천가 \n"
        "육아 용품을 추천해줍니다. 아이의 연령, 필요, 생활방식을 고려하여 개인화된 제품을 추천합니다.\n"
        
    )
