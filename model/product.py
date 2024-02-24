# 카테고리별 vectordb 생성 후 불러오기

import os
from dotenv import load_dotenv
load_dotenv()

openai_key=os.environ.get("OPENAI_API_KEY")
os.environ['OPENAI_API_KEY'] = openai_key
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
sys.path.append('/mnt/c/KIMSEONAH/Test_Study/Chatbot')

from langchain.chat_models import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
import mysql.connector
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.chains.conversation.memory import ConversationSummaryMemory                                        
import tiktoken


# 문서 로드 및 벡터 DB 생성
def load_documents_and_create_vector_db(folder_path):
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        os.makedirs(folder_path, exist_ok=True)
        loader = CSVLoader('/mnt/c/KIMSEONAH/Test_Study/Chatbot/Dr.COCO/data/raw/product_file.csv')
        csv_data=loader.load()
        print(csv_data)

        csv_vector_db = FAISS.from_documents(csv_data, ko)
        csv_vector_db.save_local(folder_path)


# 카테고리 선택 및 DB 로드
def load_csv_db():
    new_csv_vector_db = FAISS.load_local(folder_path, ko)
    return new_csv_vector_db.as_retriever(search_kwargs={'k': 3})


# 챗봇 모델 및 체인 설정
def setup_chat_model_and_chain(csv_retriever):
    prompt_template = PromptTemplate(
        input_variables=['question', 'context', 'chat_history'],
        template=template
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=chat_model,
        retriever=csv_retriever,
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
def main(query):
    load_documents_and_create_vector_db(folder_path)
    csv_retriever = load_csv_db()
    chain = setup_chat_model_and_chain(csv_retriever)
    response = chat_start(query, chain)
    return response
    
    
# 전역 변수 및 인스턴스 생성
folder_path = "/mnt/c/KIMSEONAH/Test_Study/Chatbot/Dr.COCO/data/vectordb/product"

tokenizer=tiktoken.get_encoding("cl100k_base")
def titoken_len(text):
    tokens=tokenizer.encode(text)
    return len(tokens)

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
### You are an assistant who recommends products to parents. 
# Answer questions using only the following context. If you don't know the answer, say you don't know and do not make it up: {context}
Respond to questions in a helpful manner and engage in conversation. When asked about greetings, respond in a conversational way, and recommend products that parents might be interested in, but if you don't know the exact answer, say you don't know.
If the product the user wants is not in vectordb, say it is not available.
{chat_history}
### Friend : {question}
### AI: """.strip()