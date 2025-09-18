from datetime import datetime
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

class SoilData(BaseModel):
    ph: float
    organic_carbon: float
    sand: float
    silt: float
    clay: float

    class Config:
        orm_mode = True

class FarmBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    
class FarmCreate(FarmBase):
    pass

class Farm(FarmBase):
    id: int
    owner_id: int
    soil_data: SoilData | None = None

    class Config:
        orm_mode = True # This allows the model to be created from ORM objects

class RecommendationBase(BaseModel):
    recommendation_text: str

class RecommendationCreate(RecommendationBase):
    farm_id: int

class Recommendation(RecommendationBase):
    id: int
    farm_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class MarketData(BaseModel):
    crop_name: str
    market_name: str
    price: float
    last_updated: datetime

    class Config:
        orm_mode = True

class ChatbotQuery(BaseModel):
    question: str
    language_code: str = "en-IN"

class ChatbotResponse(BaseModel):
    answer: str

Farm.update_forward_refs()