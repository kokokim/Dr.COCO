import os
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.conversation.memory import ConversationSummaryMemory                                        
import tiktoken
import pandas as pd

# baby.py 파일의 절대 경로
current_file_path = os.path.abspath(__file__)

# 'model' 폴더의 경로 (baby.py의 부모 디렉토리)
model_dir = os.path.dirname(current_file_path)

# 'code' 폴더의 경로 ('model'의 부모 디렉토리)
code_dir = os.path.dirname(model_dir)

# 'DR.COCO' 루트 폴더의 경로 ('code'의 부모 디렉토리)
root_dir = os.path.dirname(code_dir)

# 'data/raw' 폴더로의 상대 경로
raw_data_dir = os.path.join(root_dir, 'data', 'raw')

# 'data/vectordb/baby' 폴더로의 상대 경로
folder_path = os.path.join(root_dir, 'data', 'vectordb', 'baby')

documents_dicts={
    'raisebaby':[],
    'breastfeeding':[],
    'growanddevelopment':[],
    'basicparenting':[],
    'supportsystem':[],
    'babyfood':[]
}

data={
    'user_id': [1, 1, 1, 1, 1, 1, 1],
    'num_daysleep': [4, 1, 2, 3, 1, 3, 2],
    'time_daysleep': [200, 255, 320, 260, 232, 198, 302],
    'time_nightsleep': [600, 540, 563, 688, 582, 592, 608],
    'time_totalsleep': [800, 795, 883, 948, 814, 790, 910],
    'date': ['2024-02-22', '2024-02-23', '2024-02-24', '2024-02-25', '2024-02-26', '2024-02-27', '2024-02-28'],
    'child_age': [3, 3, 3, 3, 3, 3, 3],
    'child_name': ['동동이']*7
}

df=pd.DataFrame(data)

#가장 최근의 수면 데이터
latest_data=df.sort_values(by='date', ascending=False).iloc[0]

def format_minutes(minutes):
    hours=minutes//60
    minutes=minutes%60
    return f"{hours}시간 {minutes}분"

# alert 메시지 생성
formatted_day_sleep = format_minutes(latest_data['time_daysleep'])
formatted_night_sleep = format_minutes(latest_data['time_nightsleep'])
formatted_total_sleep = format_minutes(latest_data['time_totalsleep'])

alert_message = (
    f"어제 {latest_data['child_name']}의 낮잠 시간은 {formatted_day_sleep}, "
    f"낮잠 횟수는 {latest_data['num_daysleep']}회, 밤잠 시간은 {formatted_night_sleep}으로 "
    f"총 수면 시간은 {formatted_total_sleep}입니다."
)

# 챗봇에게 질문 구성
chatbot_question = (
    f"나이가 {latest_data['child_age']} 개월인 {latest_data['child_name']}의 {alert_message} 수면 시간 적당해?"
)

# 문서 로드 및 벡터 DB 생성
def load_documents_and_create_vector_db(folder_path, documents_dict):
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        os.makedirs(folder_path, exist_ok=True)
        for name, category in documents_dict.items():
            loader = PyMuPDFLoader(f'{raw_data_dir}/{name}.pdf')
            docs = loader.load_and_split(text_splitter=splitter)
            documents_dicts[category] = docs

        for category, docs in documents_dicts.items():
            vector_db = FAISS.from_documents(docs, ko)
            vector_db.save_local(f"{folder_path}/{category}_faiss_index")
    
            
# 카테고리 선택 및 DB 로드
def select_category_and_load_db():
    selected_db_path = f'{folder_path}/basicparenting_faiss_index'
    selected_vector_db = FAISS.load_local(selected_db_path, ko)
    return selected_vector_db.as_retriever(search_kwargs={'k': 3})



# 챗봇 모델 및 체인 설정
def setup_chat_model_and_chain(category_retriever):
    prompt_template = PromptTemplate(
        input_variables=['question', 'context', 'chat_history'],
        template=template
    )
    
    chain = ConversationalRetrievalChain.from_llm(
        llm=chat_model,
        retriever=category_retriever,
        memory=memory,
        combine_docs_chain_kwargs={'prompt': prompt_template},
        return_source_documents=True,
    )
    return chain

# 사용자 질문에 대한 응답 생성
def chat_start(chain):
    response=chain(chatbot_question)
    print("이잉", response['answer'])
    return response['answer']


def main():
    load_documents_and_create_vector_db(folder_path, documents_dict)
    sleep_retriever = select_category_and_load_db()
    chain = setup_chat_model_and_chain(sleep_retriever)
    response = chat_start(chain)
    return response


documents_dict = {
    'm육아대백과_신생아키우기': 'raisebaby',
    'm육아대백과_수유': 'breastfeeding',
    'm육아대백과_개월별 성장 발달': 'growanddevelopment',
    'm육아대백과_육아의기초': 'basicparenting',
    'm육아대백과_육아지원제도': 'supportsystem',
    'm육아대백과_이유식': 'babyfood'
}

tokenizer=tiktoken.get_encoding("cl100k_base")
def titoken_len(text):
    tokens=tokenizer.encode(text)
    return len(tokens)

splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50, length_function=titoken_len)
ko = HuggingFaceEmbeddings(model_name='jhgan/ko-sbert-nli', model_kwargs={'device': 'cpu'}, encode_kwargs={'normalize_embeddings': True})
chat_model = ChatOpenAI(temperature=0.1, model_name="gpt-4-turbo-preview")
memory = ConversationSummaryMemory(
    llm=chat_model,
    max_token_limit=80,
    memory_key="chat_history",
    human_prefix="### Friend",
    ai_prefix='### AI',
    output_key='answer',
    return_messages=True
)

template="""
### You are an assistant who helps with analyzing a baby's sleep.
# Answer questions using only the following context: {context}
Please provide a reliable sleep analysis based on the given data. 
The results should be comprised of no more than two paragraphs, and the explanation of the results must be conveyed kindly.
If the analysis indicates that the health condition is not good, recommend visiting a doctor.
{chat_history}
### Friend : {question}
### AI: """.strip()