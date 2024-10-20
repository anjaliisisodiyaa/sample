from pydantic import BaseModel
from datetime import time
from typing import List

class TeacherCreate(BaseModel):
  id: int
  first_name:str
  last_name:str

  class Config:
    from_attributes = True      


class TeacherResponse(BaseModel):
    data: List[TeacherCreate]
    status: bool = True
    status_code: int = 200
    message: str = "success"
