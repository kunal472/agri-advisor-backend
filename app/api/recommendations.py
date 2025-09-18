from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import models, schemas
from app.db.database import get_db
from app.core.security import get_current_user
from app.services.data_ingestion import fetch_weather_forecast

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.get("/{farm_id}", response_model=schemas.RecommendationBase)
async def generate_recommendation(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    farm = db.query(models.Farm).filter(models.Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    if farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this farm")

    # 1. Get Stored Soil Data
    soil_data = farm.soil_data
    if not soil_data:
        raise HTTPException(
            status_code=404, detail="Soil data not found for this farm. Cannot generate recommendation."
        )

    # 2. Get Live Weather Data
    weather_data = await fetch_weather_forecast(farm.latitude, farm.longitude)

    # 3. (Future) Get Market Data
    # market_data = db.query(...).all()

    # 4. Run the "ML Model" (Placeholder Logic)
    # This is where your actual ML model pipeline would be called.
    # For now, we'll use simple rule-based logic.
    recommendation_text = f"Analysis for {farm.name}:\n"
    recommendation_text += f"- Soil pH is {soil_data.ph}. "

    if weather_data and weather_data.get("daily"):
        # Check for rain in the next 3 days
        rain_coming = any(day.get("pop", 0) > 0.6 for day in weather_data["daily"][:3])
        if rain_coming:
            recommendation_text += "Rain is expected in the next 3 days. Consider delaying irrigation."
        else:
            recommendation_text += "No significant rain expected soon. Monitor soil moisture."
    else:
        recommendation_text += "Could not fetch weather data."

    return schemas.RecommendationBase(recommendation_text=recommendation_text)

@router.post("/save", response_model=schemas.Recommendation)
def save_recommendation(
    rec_data: schemas.RecommendationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    farm = db.query(models.Farm).filter(models.Farm.id == rec_data.farm_id).first()
    if not farm or farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Farm not accessible")

    new_rec = models.Recommendation(**rec_data.dict())
    db.add(new_rec)
    db.commit()
    db.refresh(new_rec)
    return new_rec


@router.get("/history/{user_id}", response_model=List[schemas.Recommendation])
def get_recommendation_history(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Query recommendations by joining through the farms table
    recommendations = (
        db.query(models.Recommendation)
        .join(models.Farm)
        .filter(models.Farm.owner_id == user_id)
        .all()
    )
    return recommendations