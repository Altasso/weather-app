from sqlalchemy import select, func
from app.models import Search
from app.database import async_session


async def save_search(city: str):
    async with async_session() as session:
        search = Search(city=city)
        session.add(search)
        await session.commit()


async def get_stats():
    async with async_session() as session:
        result = await session.execute(
            select(Search.city, func.count(Search.city)).group_by(Search.city)
        )
        return [{"city": city, "count": count} for city, count in result.all()]
