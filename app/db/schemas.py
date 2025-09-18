from pydantic import BaseModel
from typing import Optional


# Schema for user creation (request)
class UserCreate(BaseModel):
    email: str
    password: str

# Schema for reading user data (response)
class User(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None