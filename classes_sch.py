from pydantic import BaseModel
from datetime import time
from typing import List
from students_sch import ClassEnum

class ClassCreate(BaseModel):
  id:int
  standard:ClassEnum

class ClassResponse(BaseModel):
  data: List[ClassCreate]
  status: bool = True
  status_code: int = 200
  message: str = "success"
  