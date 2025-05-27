from fastapi import APIRouter, HTTPException
from app.services.weather import get_coordinates_by_city, get_weather

router = APIRouter()


@router.get("/weather")
async def get_weather_by_city(city: str):
    coords = await get_coordinates_by_city(city)
    if not coords:
        raise HTTPException(status_code=404, detail="City not found")

    lat, lon = coords
    weather_data = await get_weather(lat, lon)
    if not weather_data:
        raise HTTPException(status_code=500, detail="Could not fetch weather data")

    return {
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "weather": weather_data,
    }
