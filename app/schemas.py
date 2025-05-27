from pydantic import BaseModel
from typing import List


class HistoryResponse(BaseModel):
    history: List[str]


class CityStat(BaseModel):
    city: str
    count: int
