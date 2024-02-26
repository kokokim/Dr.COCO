# 카테고리별 vectordb 생성 후 불러오기

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
from langchain.memory import ConversationSummaryBufferMemory

os.environ['OPENAI_API_KEY'] == st.secrets["OPENAI_API_KEY"]
os.environ["TOKENIZERS_PARALLELISM"] == st.secrets["TOKENIZERS_PARALLELISM"]


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
def select_category_and_load_db(category):
    selected_db_path = f'{folder_path}/{category}_faiss_index'
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
def chat_start(query, chain):
    if query == "그만":
        return "채팅을 종료합니다."
    response = chain(query)
    
    return response['answer']


# 메인 함수: 사용자가 선택한 카테고리에 따라 챗봇을 설정하고 실행
def main(category, query):
    # baby_info_save
    load_documents_and_create_vector_db(folder_path, documents_dict)
    category_retriever = select_category_and_load_db(category)
    chain = setup_chat_model_and_chain(category_retriever)
    response = chat_start(query, chain)
    return response
    
    
# 전역 변수 및 인스턴스 생성
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
chat_model = ChatOpenAI(temperature=0.1, model_name="gpt-3.5-turbo")
memory = ConversationSummaryMemory(
    llm=chat_model,
    max_token_limit=80,
    memory_key="chat_history",
    human_prefix="### Friend",
    ai_prefix='### AI',
    output_key='answer',
    return_messages=True
)
memory.save_context(
    {"input": "아이의 이름은 김동동이야."},
    {"answer": "당신의 아이의 이름은 김동동이군요! 예쁜 이름입니다."}
)
memory.save_context(
    {"input" : "아이의 성별은 남자아이야."},
    {"answer":"당신의 아이의 성별은 남자아이이군요!"}
)
memory.save_context(
    {"input":"아이가 태어난 날은 2023년 12월 25일이야."},
    {"answer" : "당신의 아이는 2023년 12월 25일에 태어났군요. 지금은 2024년 2월 25일로 아기는 3개월이 되었어요."}
)

template="""
### You are an assistant who helps parents with parenting. 
# Answer questions using only the following context. If you don't know the answer, say you don't know and do not make it up: {context}
Answer questions in a helpful manner and engage in conversation while doing so. 
If asked about greetings, respond in a conversational way, but if you don't know the exact answer, say you don't know.
{chat_history}
### Friend : {question}
### AI: """.strip()
