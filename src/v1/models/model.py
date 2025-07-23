import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.v1.configs.database import Base



class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), index=True)
    password = Column(String(255), index=True)

    documents = relationship("Document", back_populates="owner")
    chat_history = relationship("History", back_populates="owner")
    conversations = relationship("ChatConversation", back_populates="owner")


class Document(Base):
    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    document_name = Column(String(50), index=True)
    document_type = Column(String(50), index=True)
    document_size = Column(Integer, index=True)
    file_path = Column(String(255))
    created_at = Column(
        String(50),
        default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        index=True,
    )
    owner = relationship("User", back_populates="documents")


class History(Base):
    __tablename__ = "chat_history"

    room_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    question = Column(String(255), index=True)
    answer = Column(String(255), index=True)

    owner = relationship("User", back_populates="chat_history")


class ChatConversation(Base):
    __tablename__ = "chat_conversation"

    conversation_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    session_id = Column(String(250), index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="conversations")
    messages = relationship("ChatMessage", back_populates="conversation")

class ChatMessage(Base):
    __tablename__ = "chat_message"

    message_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversation.conversation_id"), index=True)
    user_question = Column(String(255), index=True)
    ai_answer = Column(String(255), index=True)
    document_id = Column(Integer, ForeignKey("documents.document_id"), index=True)
    page = Column(Integer, index=True)
    document_name = Column(String(250), index=True)
    document_content = Column(String(1000), index=True)
    created_at = Column(
        String(50),
        default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        index=True,
    )

    conversation = relationship("ChatConversation", back_populates="messages")
