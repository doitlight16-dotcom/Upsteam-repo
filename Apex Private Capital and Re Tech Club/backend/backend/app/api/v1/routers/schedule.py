from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/schedule", tags=["Schedule"])

class SessionModel(BaseModel):
    id: str
    date: str
    startTime: str
    endTime: str
    title: str
    speakerName: str
    speakerRole: str | None = None
    location: str

# Mock-данные пока БД пустая
MOCK_SCHEDULE = [
  {
    "id": "session-1",
    "date": "2026-11-04",
    "startTime": "08:00",
    "endTime": "09:00",
    "title": "Регистрация и welcome-кофе для делегации КМГ",
    "speakerName": "Организационный комитет",
    "location": "Павильон КМГ, ADNEC Centre",
  },
  {
    "id": "session-2",
    "date": "2026-11-04",
    "startTime": "09:30",
    "endTime": "10:15",
    "title": "Стратегия цифровой трансформации КМГ: Industrial AI в нефтегазе",
    "speakerName": "Нуржан Салимов",
    "speakerRole": "VP Digital Transformation, КМГ",
    "location": "Главная сцена, Hall 14",
  }
]

@router.get("/", response_model=List[SessionModel])
async def get_schedule():
    """
    Returns the ADIPEC schedule. 
    In the future, this will be fetched from PostgreSQL.
    """
    return MOCK_SCHEDULE
