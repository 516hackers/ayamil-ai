from pydantic import BaseModel, EmailStr
from typing import Optional


class SignupIn(BaseModel):
name: str
email: EmailStr
password: str


class LoginIn(BaseModel):
email: EmailStr
password: str


class BusinessTrainIn(BaseModel):
user_id: str
business_text: str


class ChatIn(BaseModel):
user_id: str
message: str
context: Optional[str] = None
