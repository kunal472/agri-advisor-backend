from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from app.db import models, schemas
from app.db.database import get_db
from app.core.security import get_current_user
from app.services.data_ingestion import fetch_weather_forecast


from app.services.ml_service import prediction_service

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.get("/{farm_id}")
async def generate_recommendation(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
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
    if not weather_data or not weather_data.get("daily"):
        raise HTTPException(status_code=503, detail="Could not retrieve valid weather data.")

    # 3. Prepare the 'live_features' dictionary for the model
    # Process weather data to get averages over the next week
    daily_forecasts = weather_data["daily"][:7]
    avg_temp = sum(day['temp']['day'] for day in daily_forecasts) / len(daily_forecasts)
    avg_humidity = sum(day['humidity'] for day in daily_forecasts) / len(daily_forecasts)
    total_rainfall = sum(day.get('rain', 0) for day in daily_forecasts)
    
    # Map the collected data to the feature names your model expects
    live_features = {
        'topsoil_phh2o': soil_data.ph,
        'avg_temp_celsius': avg_temp,
        'avg_humidity_percent': avg_humidity,
        'total_rainfall_mm': total_rainfall,
        # Placeholders for now, as SoilGrids free tier doesn't easily provide N, P, K
        'topsoil_nitrogen': 95, 
        'P_placeholder': 55,
        'K_placeholder': 45,
    }

    # 4. Run the ML Model
    try:
        final_recommendations = prediction_service.get_final_recommendations(live_features)
        
        # Sort recommendations by estimated profit
        sorted_recommendations = sorted(
            final_recommendations, 
            key=lambda x: x['estimated_profit_rs_per_hectare'], 
            reverse=True
        )
        return sorted_recommendations

    except Exception as e:
        # Catch potential errors from the model prediction step
        print(f"Error during model prediction: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during recommendation generation.")


# The POST and GET history endpoints remain the same
# You might want to update the schema to accept a JSON payload for saving
@router.post("/save", response_model=schemas.Recommendation)
def save_recommendation(
    rec_data: schemas.RecommendationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    farm = db.query(models.Farm).filter(models.Farm.id == rec_data.farm_id).first()
    if not farm or farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Farm not accessible")

    # Convert dictionary/list recommendations to a JSON string for storage
    rec_text = json.dumps(rec_data.recommendation_text)
    
    new_rec = models.Recommendation(
        farm_id=rec_data.farm_id,
        recommendation_text=rec_text
    )
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
    
    recommendations = (
        db.query(models.Recommendation)
        .join(models.Farm)
        .filter(models.Farm.owner_id == user_id)
        .all()
    )
    return recommendations