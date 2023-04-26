from pydantic import BaseModel, EmailStr
from datetime import date

class Lead(BaseModel):
    id: int
    created_at: date | None = None
    email: EmailStr
    full_name: str
    country: str

    class Config:
        orm_mode = True

class CreateLead(BaseModel):
    email: EmailStr
    full_name: str
    country: str

    class Config:
        orm_mode = True
