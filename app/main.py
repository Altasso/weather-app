import httpx
import uuid
from typing import List
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from urllib.parse import quote, unquote

from app.crud import save_search, get_stats
from app.database import create_tables
from app.routers import weather
from app.redis_client import r
from app.schemas import HistoryResponse, CityStat

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.include_router(weather.router)


@app.on_event("startup")
async def on_startup():
    await create_tables()


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request, city: str = None):
    if city is None:
        last_city = unquote(request.cookies.get("last_city", ""))

        return templates.TemplateResponse("form.html",{
            "request": request,
            "last_city": last_city
        })

    forecast = await get_weather(city)

    user_id = request.cookies.get("user_id")
    new_user_id = False
    if not user_id:
        user_id = str(uuid.uuid4())

        new_user_id = True

    redis_key = f"user:{user_id}:history"

    r.lpush(redis_key, city)
    r.ltrim(redis_key, 0, 9)
    history = r.lrange(redis_key, 0, 9)

    response = templates.TemplateResponse(
        "weather.html",
        {
            "request": request,
            "city": city,
            "forecast": forecast,
            "history": history,
        }
    )
    response.set_cookie("last_city", quote(city))
    if new_user_id:
        response.set_cookie("user_id", user_id)
    print(f"[{user_id}] history:", history)
    return response


@app.post("/weather", response_class=HTMLResponse)
async def show_weather(request: Request, city: str = Form(...)):
    forecast = await get_weather(city)

    user_id = request.cookies.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())

    redis_key = f"user:{user_id}:history"
    r.lpush(redis_key, city)
    r.ltrim(redis_key, 0, 9)
    history = r.lrange(redis_key, 0, 9)

    response = templates.TemplateResponse("weather.html", {
        "request": request,
        "city": city,
        "forecast": forecast,
        "history": history,
    })

    response.set_cookie("last_city", quote(city))
    response.set_cookie("user_id", user_id)
    await save_search(city)

    return response


async def get_weather(city: str) -> str:
    geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json"

    async with httpx.AsyncClient() as client:
        geo_response = await client.get(geocode_url)
        geo_data = geo_response.json()

        if "results" not in geo_data or len(geo_data["results"]) == 0:
            return f"Город '{city}' не найден"

        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current_weather=true"
        )

        weather_response = await client.get(weather_url)
        weather_data = weather_response.json()

        if "current_weather" not in weather_data:
            return "Не удалось получить прогноз"

        temp = weather_data["current_weather"]["temperature"]
        wind = weather_data["current_weather"]["windspeed"]

        return f"Температура: {temp}°C, Ветер: {wind} км/ч"


@app.get("/history", response_model=HistoryResponse)
async def get_history(request: Request):
    user_id = request.cookies.get("user_id")
    print("USER_ID in /history:", user_id)
    if not user_id:
        return {"history": []}

    redis_key = f"user:{user_id}:history"
    history = r.lrange(redis_key, 0, 9)
    print(f"KEY: {redis_key}, VALUES: {history}")
    return {"history": history}

@app.get("/api/stats", response_class=JSONResponse, response_model=List[CityStat])
async def stats():
    stats = await get_stats()
    return stats
