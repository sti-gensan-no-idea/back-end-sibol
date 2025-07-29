from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class ChatroomCreate(BaseModel):
    name: str

class ChatroomResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str

class MessageReaction(BaseModel):
    emoji: str

class MessageResponse(BaseModel):
    id: int
    chatroom_id: int
    user_id: int
    content: str
    reactions: Dict[str, List[int]]
    created_at: datetime

    class Config:
        from_attributes = True