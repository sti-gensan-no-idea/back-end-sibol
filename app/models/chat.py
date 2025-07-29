from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime

class Chatroom(Base):
    __tablename__ = "chatrooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("Message", back_populates="chatroom")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chatroom_id = Column(Integer, ForeignKey("chatrooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    reactions = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    chatroom = relationship("Chatroom", back_populates="messages")
    user = relationship("User")