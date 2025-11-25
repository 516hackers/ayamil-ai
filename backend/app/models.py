from typing import Optional
from pydantic import BaseModel, EmailStr


class UserInDB(BaseModel):
_id: Optional[str]
name: str
email: EmailStr
hashed_password: str


class Business(BaseModel):
_id: Optional[str]
user_id: str
text: str
