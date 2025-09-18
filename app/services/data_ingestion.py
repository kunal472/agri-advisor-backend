import httpx
from app.core.config import settings

# A dictionary to map our desired properties to SoilGrids property names
SOIL_PROPERTIES = {
    "ph": "phh2o",
    "organic_carbon": "soc",
    "sand": "sand",
    "silt": "silt",
    "clay": "clay",
}

async def fetch_soil_data(latitude: float, longitude: float) -> dict | None:
    """
    Fetches predictive soil data from SoilGrids API for a given lat/lon.
    """
    properties = ",".join(SOIL_PROPERTIES.values())
    url = (
        "https://rest.soilgrids.org/soilgrids/v2.0/properties/query"
        f"?lon={longitude}&lat={latitude}&property={properties}"
        "&depth=0-5cm&value=mean"
    )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=20.0)
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            data = response.json()

        # Parse the complex SoilGrids response to a simple dictionary
        raw_properties = data.get("properties", {}).get("layers", [])

        parsed_data = {}
        for layer in raw_properties:
            prop_name = layer.get("name")
            # Find our key by looking up the SoilGrids value
            local_key = next((k for k, v in SOIL_PROPERTIES.items() if v == prop_name), None)

            if local_key:
                # SoilGrids values are typically integers, scaled by a factor
                value = layer.get("depths", [{}])[0].get("values", {}).get("mean")
                unit_measure = layer.get("unit_measure")

                # SoilGrids provides pH scaled by 10, organic carbon by 10, and textures by 10
                # For example, a pH of 7.2 is returned as 72.
                if value is not None:
                     # Textures (sand, silt, clay) are g/kg, so no conversion needed
                    if local_key in ["sand", "silt", "clay"]:
                        parsed_data[local_key] = value
                    else: # Convert other properties by dividing by 10
                        parsed_data[local_key] = value / 10.0

        return parsed_data if len(parsed_data) == len(SOIL_PROPERTIES) else None

    except httpx.RequestError as exc:
        print(f"An error occurred while requesting from SoilGrids: {exc}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during soil data parsing: {e}")
        return None
    
async def fetch_weather_forecast(latitude: float, longitude: float) -> dict | None:
    """
    Fetches a 7-day weather forecast from OpenWeatherMap.
    """
    if not settings.OPENWEATHER_API_KEY:
        print("Warning: OPENWEATHER_API_KEY is not set.")
        return None

    # The One Call API provides daily forecasts
    url = (
        "https://api.openweathermap.org/data/3.0/onecall"
        f"?lat={latitude}&lon={longitude}&exclude=current,minutely,hourly,alerts"
        f"&appid={settings.OPENWEATHER_API_KEY}&units=metric"
    )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting from OpenWeatherMap: {exc}")
        return None