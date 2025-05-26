import httpx

GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"

async def get_coordinates_by_city(city: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(GEOCODING_API, params={"name": city, "count": 1})
        print("Geocoding response:", response.text)
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            return None

        result = data["results"][0]
        return result["latitude"], result["longitude"]

async def get_weather(latitude: float, longitude: float):
    async with httpx.AsyncClient as client:
        response = await client.get(WEATHER_API, params={
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True
        })
        print("Weather response:", response.text)
        response.raise_for_status()
        return response.json().get("current_weather")