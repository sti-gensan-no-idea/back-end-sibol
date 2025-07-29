from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.controllers.chat_controller import ChatController
from app.models.user import User
from app.services.auth_service import get_current_user
from app.schemas.chat import ChatroomCreate, ChatroomResponse, MessageCreate, MessageReaction, MessageResponse

router = APIRouter(prefix="/api/v1/chats", tags=["chats"])

@router.post("/chatrooms", response_model=ChatroomResponse, summary="Create a chatroom")
async def create_chatroom(chatroom: ChatroomCreate, db: Session = Depends(get_db), 
                         current_user: User = Depends(get_current_user)):
    return ChatController.create_chatroom(db, chatroom.name, current_user)

@router.get("/chatrooms", response_model=list[ChatroomResponse], summary="Get all chatrooms")
async def get_chatrooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), 
                       current_user: User = Depends(get_current_user)):
    return ChatController.get_chatrooms(db, skip, limit)

@router.post("/chatrooms/{chatroom_id}/messages", response_model=MessageResponse, summary="Send a message")
async def create_message(chatroom_id: int, message: MessageCreate, db: Session = Depends(get_db), 
                        current_user: User = Depends(get_current_user)):
    return ChatController.create_message(db, chatroom_id, message.content, current_user)

@router.post("/messages/{message_id}/reactions", response_model=MessageResponse, summary="Add a reaction to a message")
async def add_reaction(message_id: int, reaction: MessageReaction, db: Session = Depends(get_db), 
                       current_user: User = Depends(get_current_user)):
    return ChatController.add_reaction(db, message_id, reaction.emoji, current_user)

@router.get("/chatrooms/{chatroom_id}/messages", response_model=list[MessageResponse], summary="Get messages in a chatroom")
async def get_messages(chatroom_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), 
                      current_user: User = Depends(get_current_user)):
    return ChatController.get_messages(db, chatroom_id, skip, limit)