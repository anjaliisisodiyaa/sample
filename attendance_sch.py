from pydantic import BaseModel,Field
from typing import Optional,Any
from datetime import date, datetime
from students_sch import ClassEnum
from enum import Enum

# class SubjectEnum(str, Enum):
#   ENGLISH = "english"
#   HINDI = "hindi"
#   SCIENCE = "science"
#   MATHS = "maths"
#   SST = "social science"
#   COMPUTER = "computer"
#   PHYSICS = "physics"
#   CHEMISTRY = "chemistry"
#   BIOLOGY = "biology"
#   ECONOMICS = "economics"
#   ACCOUNTANCY = "accounts"
#   PSCIENCE = "political science"
#   GEO = "geography"
#   SOCIOLOGY = "sociology"
#   HISTORY = "history"

class AttendanceEnum(str,Enum):
  PRESENT = "present"
  ABSENT = "absent"

class AttendanceBase(BaseModel):
  id: int
  grade:  ClassEnum 
  date: Optional[datetime] = None
  attendance: bool = None
  student_id: int =None

  class Config:
    orm_mode = True

class ResponseModelAttendance(BaseModel):
  data: Optional[AttendanceBase] = None
  status: bool = True
  status_code: int = 200
  message: str = "success"

class AttendanceUpdate(BaseModel):
  grade: ClassEnum = None
  date: Optional[datetime] = None
  attendance: bool = None

class AttendanceResponse(BaseModel):
  id: int
  grade: str
  date: Optional[datetime] = None
  attendance: bool
  student_id: int

  class Config:
    orm_mode = True

class ResponseModelAttendance(BaseModel):
  status: bool
  status_code: int
  message: str
  data: Optional[Any]=None

  class Config:
    orm_mode = True

class ResponseModelGrade(BaseModel):
  data: Optional[AttendanceResponse] 
  status: bool
  status_code: int
  message: str
class AttendanceRequest(BaseModel):
    grade: ClassEnum
    date: datetime
    student_id: int