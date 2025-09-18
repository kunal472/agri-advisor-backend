from pydantic import BaseModel
from typing import Optional , List


# Schema for user creation (request)
class UserCreate(BaseModel):
    email: str
    password: str

# Schema for reading user data (response)
class User(BaseModel):
    id: int
    email: str
    farms: List['Farm'] = []

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class FarmBase(BaseModel):
    name: str
    latitude: float
    longitude: float

class FarmCreate(FarmBase):
    pass

class Farm(FarmBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True # This allows the model to be created from ORM objects

User.update_forward_refs()