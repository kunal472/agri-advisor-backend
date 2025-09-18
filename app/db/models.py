from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    farms = relationship("Farm", back_populates="owner")


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    soil_data = relationship("SoilData", back_populates="farm", uselist=False)
    recommendations = relationship("Recommendation", back_populates="farm")
    owner = relationship("User", back_populates="farms")

class SoilData(Base):
    __tablename__ = "soil_data"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), unique=True)
    ph = Column(Float)
    organic_carbon = Column(Float) # In dg/kg (decigrams per kilogram)
    sand = Column(Float) # In g/kg (grams per kilogram)
    silt = Column(Float) # In g/kg
    clay = Column(Float) # In g/kg

    farm = relationship("Farm", back_populates="soil_data")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    recommendation_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    farm = relationship("Farm", back_populates="recommendations")

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String, index=True, nullable=False)
    market_name = Column(String, index=True) # e.g., "Nashik"
    price = Column(Float, nullable=False) # Price per quintal
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

