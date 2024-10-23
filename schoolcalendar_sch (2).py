from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class SchoolCalendarBase(BaseModel):
    # sr_no: int
    date: date
    holiday: str = Field(min_length=3, max_length=500)

    class Config:
        orm_mode = True

class ResponseModelCalendar(BaseModel):
    data: int = None
    status: bool = True
    status_code: int = 200
    message: str = "success"

    class Config:
        orm_mode = True


class SchoolCalendarCreate(SchoolCalendarBase):
    pass

class SchoolCalendarUpdate(BaseModel):   
    date: date | None
    holiday: Optional[str] = None

    class Config:
        orm_mode = True

class SchoolCalendarResponse(SchoolCalendarBase):
    sr_no: int

    class Config:
        orm_mode = True

