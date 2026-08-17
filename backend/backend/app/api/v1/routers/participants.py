from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/participants", tags=["Participants"])

class ParticipantModel(BaseModel):
    id: str
    fullName: str
    role: str
    bio: str
    telegramUsername: str | None = None
    telegramUserId: int | None = None

MOCK_PARTICIPANTS = [
  {
    "id": "p-1",
    "fullName": "Нуржан Салимов",
    "role": "VP Digital Transformation, КМГ",
    "bio": "Руководит стратегией цифровой трансформации КазМунайГаз. 15 лет в нефтегазовой отрасли.",
    "telegramUsername": "n_salimov",
  },
  {
    "id": "p-4",
    "fullName": "Sultan Al-Mansoori",
    "role": "VP Partnerships, ADNOC",
    "bio": "Стратегические партнёрства ADNOC с международными NOC.",
    "telegramUsername": "sultan_adnoc",
  }
]

@router.get("/", response_model=List[ParticipantModel])
async def get_participants():
    """
    Returns ADIPEC participants.
    In the future, this will be fetched from PostgreSQL.
    """
    return MOCK_PARTICIPANTS
