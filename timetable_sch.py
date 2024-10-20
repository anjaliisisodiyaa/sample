from pydantic import BaseModel
from datetime import time
from new_models import WeekEnum, SubjectEnum
from typing import List

class TimetableCreate(BaseModel):
    day_of_week: WeekEnum
    start_time: time
    end_time: time
    subject: SubjectEnum
    teacher_id: int
    class_id: int
    room_number: str

class TimetableResponse(BaseModel):
    id: int
    day_of_week: WeekEnum
    start_time: time
    end_time: time
    subject: SubjectEnum
    teacher_id: int
    class_id: int
    room_number: str

class TimetableResponseData(BaseModel):
    data: List[TimetableResponse]
    status: bool = True
    status_code: int = 200
    message: str = "success"