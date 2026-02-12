from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    phone: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    phone: str

class Token(BaseModel):
    access_token: str
    token_type: str

class FamilyCreate(BaseModel):
    name: str

class FamilyResponse(BaseModel):
    id: str
    name: str

class MessageResponse(BaseModel):
    role: str
    content: str

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    location: str

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None

class ItemResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    location: str
    family_id: str
    added_by: str
    created_at: str

class ChatRequest(BaseModel):
    message: Optional[str]

class ChatResponse(BaseModel):
    message: Optional[str]