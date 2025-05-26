import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.crud import save_search, get_stats
from app.database import create_tables

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
async def on_startup():
    await create_tables()


@app.get("/", response_class=HTMLResponse)
async def form_page(request: Request):
    last_city = request.cookies.get("last_city", "")

    return templates.TemplateResponse("form.html",
                                      {"request": request, "last_city": last_city})


@app.post("/weather", response_class=HTMLResponse)
async def show_weather(request: Request, city: str = Form(...)):
    forecast = await get_weather(city)

    response = templates.TemplateResponse("weather.html", {
        "request": request,
        "city": city,
        "forecast": forecast
    })

    response.set_cookie("last_city", city)
    await save_search(city)

    return response


async def get_weather(city: str):
    geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json"

    async with httpx.AsyncClient() as client:
        geo_response = await client.get(geocode_url)
        geo_data = geo_response.json()

        if "results" not in geo_data or len(geo_data["results"]) == 0:
            return f"Город '{city}' не найден"

        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longtitude"]

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

@app.get("/api/stats", response_class=JSONResponse)
async def stats():
    stats = await get_stats()
    return stats