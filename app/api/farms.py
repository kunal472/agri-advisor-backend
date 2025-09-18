from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import schemas, models
from app.db.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/api/farms", tags=["Farms"])

@router.post("/", response_model=schemas.Farm, status_code=status.HTTP_201_CREATED)
def create_farm_for_user(
    farm: schemas.FarmCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Create a new farm for the currently logged-in user.
    """
    # Create the new farm instance, linking it to the current user
    new_farm = models.Farm(**farm.dict(), owner_id=current_user.id)
    db.add(new_farm)
    db.commit()
    db.refresh(new_farm)

    # --- DATA INGESTION TRIGGER ---
    # In a real-world scenario, you would trigger the SoilGrids data fetch here.
    # For now, we will print a message as a placeholder.
    print(f"-> Triggering SoilGrids fetch for farm {new_farm.id} at ({new_farm.latitude}, {new_farm.longitude})")

    return new_farm


@router.get("/", response_model=List[schemas.Farm])
def read_user_farms(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Retrieve all farms owned by the currently logged-in user.
    """
    return current_user.farms