# 여러 카테고리 선택 시 해당 카테고리db 합친 후 답변 생성하기 (사용x)

import sys
sys.path.append('/mnt/c/KIMSEONAH/Test_Study/Chatbot')

from langchain.chat_models import ChatOpenAI
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
import mysql.connector
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.conversation.memory import ConversationSummaryMemory                                        
import tiktoken
from openai import OpenAI

client = OpenAI()

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
            loader = PyMuPDFLoader(f'/mnt/c/KIMSEONAH/Test_Study/Chatbot/chatbot-starter/data/raw/{name}.pdf')
            docs = loader.load_and_split(text_splitter=splitter)
            documents_dicts[category] = docs

        for category, docs in documents_dicts.items():
            vector_db = FAISS.from_documents(docs, ko)
            vector_db.save_local(f"{folder_path}/{category}_faiss_index")


# 카테고리 선택 및 DB 로드
def select_category_and_load_db(categories):
    retrievers=[]
    for category in categories:
        selected_db_path = f'{folder_path}/{category}_faiss_index'
        if os.path.exists(selected_db_path):
            selected_vector_db = FAISS.load_local(selected_db_path, ko)
            retrievers.append(selected_vector_db.as_retriever())
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
    answer = chain(query)
    return answer['answer']


# 메인 함수: 사용자가 선택한 카테고리에 따라 챗봇을 설정하고 실행
def main(category, query):
    load_documents_and_create_vector_db(folder_path, documents_dict)
    category_retriever = select_category_and_load_db(category)
    chain = setup_chat_model_and_chain(category_retriever)
    response = chat_start(query, chain)
    return response
    
    
# 전역 변수 및 인스턴스 생성
folder_path = "/mnt/c/KIMSEONAH/Test_Study/Chatbot/chatbot-starter/data/vectordb/"
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

template="""
### You are an assistant who helps parents with parenting. 
# Answer questions using only the following context. If you don't know the answer, say you don't know and do not make it up: {context}
Answer questions in a helpful manner and engage in conversation while doing so. 
If asked about greetings, respond in a conversational way, but if you don't know the exact answer, say you don't know.
{chat_history}
### Friend : {question}
### AI: """.strip()


# category = "raisebaby"  # 카테고리 선택 예시
# query = "아기가 밤에 자주 깨요. 어떻게 해야 하나요?"  # 사용자 질문 예시
# main(category, query)