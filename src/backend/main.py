from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Chat, Message
from pydantic import BaseModel
from typing import List
from datetime import datetime

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

@app.post("/chats/{chat_id}/messages/", response_model=MessageInDB)
def create_message_for_chat(
        chat_id: int, message: MessageCreate, db: Session = Depends(get_db)):
    db_message = Message(**message.dict(), chat_id=chat_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Simulando resposta do chatbot
    chatbot_message = Message(content=f"Echo: {message.content}", user=CHATBOT_NAME, chat_id=chat_id)
    db.add(chatbot_message)
    db.commit()
    db.refresh(chatbot_message)
    
    return db_message

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
