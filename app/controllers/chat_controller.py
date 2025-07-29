from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.chat import Chatroom, Message
from app.models.user import User

class ChatController:
    @staticmethod
    def create_chatroom(db: Session, name: str, user: User):
        chatroom = Chatroom(name=name)
        db.add(chatroom)
        db.commit()
        db.refresh(chatroom)
        return chatroom

    @staticmethod
    def get_chatrooms(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Chatroom).offset(skip).limit(limit).all()

    @staticmethod
    def create_message(db: Session, chatroom_id: int, content: str, user: User):
        chatroom = db.query(Chatroom).filter(Chatroom.id == chatroom_id).first()
        if not chatroom:
            raise HTTPException(status_code=404, detail="Chatroom not found")
        message = Message(chatroom_id=chatroom_id, user_id=user.id, content=content)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def add_reaction(db: Session, message_id: int, emoji: str, user: User):
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        reactions = message.reactions or {}
        if emoji not in reactions:
            reactions[emoji] = []
        if user.id not in reactions[emoji]:
            reactions[emoji].append(user.id)
        message.reactions = reactions
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_messages(db: Session, chatroom_id: int, skip: int = 0, limit: int = 100):
        chatroom = db.query(Chatroom).filter(Chatroom.id == chatroom_id).first()
        if not chatroom:
            raise HTTPException(status_code=404, detail="Chatroom not found")
        return db.query(Message).filter(Message.chatroom_id == chatroom_id).offset(skip).limit(limit).all()