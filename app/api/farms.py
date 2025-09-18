from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import schemas, models
from app.db.database import get_db
from app.core.security import get_current_user
from app.services.data_ingestion import fetch_soil_data
router = APIRouter(prefix="/api/farms", tags=["Farms"])

@router.post("/", response_model=schemas.Farm, status_code=status.HTTP_201_CREATED)
async def create_farm_for_user( # Make the function async
    farm: schemas.FarmCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    new_farm = models.Farm(**farm.dict(), owner_id=current_user.id)
    db.add(new_farm)
    db.commit()
    db.refresh(new_farm)

    # --- LIVE DATA INGESTION ---
    soil_properties = await fetch_soil_data(new_farm.latitude, new_farm.longitude)

    if soil_properties:
        new_soil_data = models.SoilData(**soil_properties, farm_id=new_farm.id)
        db.add(new_soil_data)
        db.commit()
        db.refresh(new_farm) # Refresh the farm to load the new soil data relationship
    else:
        print(f"Warning: Could not fetch soil data for farm {new_farm.id}.")

    return new_farm


@router.get("/", response_model=List[schemas.Farm])
def read_user_farms(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return current_user.farms