# In app/services/market_data_job.py
import httpx
from sqlalchemy.orm import Session

from app.db import models

# NOTE: You would need to find the specific API endpoint and resource ID from data.gov.in
# This URL is a placeholder example.
DATA_GOV_API_URL = "https://api.data.gov.in/resource/some-resource-id"
DATA_GOV_API_KEY = "your_data_gov_api_key"

def fetch_and_store_market_data(db: Session):
    """
    Fetches market data and updates the database.
    This function would be called by a scheduler.
    """
    print("-> Running scheduled job: Fetching market price data...")
    # params = {"api-key": DATA_GOV_API_KEY, "format": "json", "filters[market]": "Nashik"}

    try:
        # response = httpx.get(DATA_GOV_API_URL, params=params)
        # response.raise_for_status()
        # records = response.json().get('records', [])

        # --- Placeholder Data ---
        # Since the live API requires specific setup, we'll use mock data.
        records = [
            {"commodity": "Wheat", "market": "Nashik", "modal_price": "2350"},
            {"commodity": "Onion", "market": "Nashik", "modal_price": "1800"},
        ]
        # --- End Placeholder ---

        for record in records:
            crop_name = record.get("commodity")
            price = float(record.get("modal_price"))

            # Check if the crop already exists and update it, or create a new entry
            db_crop = db.query(models.MarketData).filter(models.MarketData.crop_name == crop_name).first()
            if db_crop:
                db_crop.price = price
            else:
                new_crop = models.MarketData(
                    crop_name=crop_name,
                    market_name=record.get("market"),
                    price=price
                )
                db.add(new_crop)

        db.commit()
        print("-> Market price data updated successfully.")

    except httpx.RequestError as exc:
        print(f"Error fetching market data: {exc}")
    except Exception as e:
        print(f"An error occurred while processing market data: {e}")
        db.rollback()