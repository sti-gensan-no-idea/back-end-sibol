# app/views/chat_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.controllers.chat_controller import ChatController
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.ai_service import AIService
from app.schemas.chat import ChatroomCreate, ChatroomResponse, MessageCreate, MessageReaction, MessageResponse
from pydantic import BaseModel
from typing import List
import requests
import os

router = APIRouter(prefix="/api/v1/chats", tags=["Chats"])

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@router.post("/chatrooms", response_model=ChatroomResponse, summary="Create a chatroom")
async def create_chatroom(chatroom: ChatroomCreate, db: Session = Depends(get_db), 
                         current_user: User = Depends(get_current_user)):
    """Create a new chatroom for the authenticated user."""
    return ChatController.create_chatroom(db, chatroom.name, current_user)

@router.get("/chatrooms", response_model=list[ChatroomResponse], summary="Get all chatrooms")
async def get_chatrooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), 
                       current_user: User = Depends(get_current_user)):
    """Retrieve a list of chatrooms with pagination."""
    return ChatController.get_chatrooms(db, skip, limit)

@router.post("/chatrooms/{chatroom_id}/messages", response_model=MessageResponse, summary="Send a message")
async def create_message(chatroom_id: int, message: MessageCreate, db: Session = Depends(get_db), 
                        current_user: User = Depends(get_current_user)):
    """Send a message to a specific chatroom."""
    return ChatController.create_message(db, chatroom_id, message.content, current_user)

@router.post("/messages/{message_id}/reactions", response_model=MessageResponse, summary="Add a reaction to a message")
async def add_reaction(message_id: int, reaction: MessageReaction, db: Session = Depends(get_db), 
                       current_user: User = Depends(get_current_user)):
    """Add an emoji reaction to a message."""
    return ChatController.add_reaction(db, message_id, reaction.emoji, current_user)

@router.get("/chatrooms/{chatroom_id}/messages", response_model=list[MessageResponse], summary="Get messages in a chatroom")
async def get_messages(chatroom_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), 
                      current_user: User = Depends(get_current_user)):
    """Retrieve messages in a specific chatroom with pagination."""
    return ChatController.get_messages(db, chatroom_id, skip, limit)

@router.post("/completions", summary="Chat Completions with AI", response_model=dict)
async def chat_completions(request: ChatRequest, db: Session = Depends(get_db), 
                          current_user: User = Depends(get_current_user)):
    """Handle AI-driven chat completions for real estate queries using fine-tuned gpt-oss-20b."""
    ai_service = AIService()
    try:
        user_query = next((msg.content for msg in request.messages if msg.role == "user"), "")
        property_info = ai_service.query_properties(user_query)
        model_path = "gpt-oss-20b-finetuned" if os.path.exists("gpt-oss-20b-finetuned") else "openai/gpt-oss-20b"
        host = "http://127.0.0.1:8002" if os.getenv("ENV") == "local" else "http://localhost:8002"

        response = requests.post(
            f"{host}/v1/chat/completions",
            json={
                "model": model_path,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a real estate assistant for aTuna, a real estate website in General Santos City, Philippines. "
                            "Provide accurate, friendly responses about properties (prices in PHP, e.g., ₱2.5M–₱5M), addressing local concerns "
                            "like haunted status (assume none are haunted), flood risk (assume low unless specified), or pet-friendliness (assume yes unless specified). "
                            "Use Filipino-friendly language (e.g., 'Mabuhay!'). Reference General Santos City neighborhoods (e.g., Rizal St, Quezon Ave). "
                            "Keep responses concise. Reasoning: medium. Use this property data if relevant:\n" + property_info
                        )
                    },
                    *request.messages
                ],
                "max_tokens": 150,
                "temperature": 0.7,
                "stream": False
            },
            headers={"Authorization": f"Bearer {os.getenv('HUGGINGFACE_TOKEN')}"}
        )
        response.raise_for_status()
        ai_response = response.json()

        # Save the AI response as a message in the database
        chatroom_id = ChatController.get_or_create_default_chatroom(db, current_user.id)
        ai_message = MessageCreate(content=ai_response["choices"][0]["message"]["content"].strip())
        ChatController.create_message(db, chatroom_id, ai_message.content, current_user, is_ai=True)

        return ai_response
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with AI model: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")