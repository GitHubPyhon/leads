from pydantic import BaseModel, EmailStr
from datetime import date


class TaskResponse(BaseModel):
    status: str
    args: dict[str, date]


class Lead(BaseModel):
    id: int
    created_at: date
    full_name: str
    email: EmailStr
    country_id: str
