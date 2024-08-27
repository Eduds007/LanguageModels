from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Chat, Message
from pydantic import BaseModel
from typing import List
from datetime import datetime
import requests
import time
import json

DPR_URL = "http://localhost:5000/query"


DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuração do CORS para permitir todas as origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir qualquer origem
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)

CHATBOT_ID = "001"
CHATBOT_NAME = "Chatbot"

# Pydantic models
class MessageBase(BaseModel):
    content: str
    user: str

class MessageCreate(MessageBase):
    pass

class MessageInDB(MessageBase):
    id: int
    chat_id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class ChatBase(BaseModel):
    name: str

class ChatCreate(ChatBase):
    pass

class ChatInDB(ChatBase):
    id: int
    messages: List[MessageInDB] = []

    class Config:
        orm_mode = True

# Dependência para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/chats/", response_model=ChatInDB)
def create_chat(chat: ChatCreate, db: Session = Depends(get_db)):
    db_chat = Chat(name=chat.name)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

@app.get("/chats/{chat_id}", response_model=ChatInDB)
def read_chat(chat_id: int, db: Session = Depends(get_db)):
    db_chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if db_chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return db_chat




@app.get("/chats/", response_model=List[ChatInDB])
def read_chats(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    chats = db.query(Chat).offset(skip).limit(limit).all()
    return chats

@app.delete("/chats/{chat_id}/messages/")
def delete_messages(chat_id: int, db: Session = Depends(get_db)):
    db.query(Message).filter(Message.chat_id == chat_id).delete()
    db.commit()
    return {"detail": "Messages deleted"}

@app.delete("/chats/{chat_id}/")
def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    db.query(Message).filter(Message.chat_id == chat_id).delete()
    db.query(Chat).filter(Chat.id == chat_id).delete()
    db.commit()
    return {"detail": "Chat and its messages deleted"}


def send_query_to_dpr(query: str):
    try:
        # Faz a requisição inicial, mas espera a resposta, que pode demoarar 1 minuto
        response = requests.post(DPR_URL, json={"query": query}, timeout=60)
        if response.status_code == 200:
            return response.json()  # Retorna a resposta completa
        else:
            return {"error": "Failed to retrieve data from DPR"}
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred: {str(e)}"}



@app.post("/chats/{chat_id}/messages/", response_model=MessageInDB)
def create_message_for_chat(chat_id: int, message: MessageCreate, db: Session = Depends(get_db)):
    # Adiciona a mensagem do usuário no banco de dados
    db_message = Message(**message.dict(), chat_id=chat_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    # Envia a mensagem para o DPR e recebe a resposta
    dpr_response = send_query_to_dpr(message.content)
    # Verifica se houve erro na resposta do DPR
    if "error" in dpr_response:
        chatbot_message_content = "Desculpe, não consegui processar sua pergunta."
    else:
        content_list = json.loads(dpr_response['content'])

        # Acessar o 'answer' do primeiro item
        answer = content_list[0]['answer']
        chatbot_message_content = answer


    # Adiciona a resposta do chatbot ao banco de dados
    chatbot_message = Message(content=chatbot_message_content, user=CHATBOT_NAME, chat_id=chat_id)
    db.add(chatbot_message)
    db.commit()
    db.refresh(chatbot_message)

    return chatbot_message

@app.get("/chats/{chat_id}/messages/", response_model=List[MessageInDB])
def get_messages(chat_id: int, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(Message.chat_id == chat_id).all()
    return messages
