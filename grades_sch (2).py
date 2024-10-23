from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import date,datetime
from students_sch import ClassEnum,StudentStatus, StudentResponse

class GradesBase(BaseModel):
  student_name: str = Field(min_length=3, max_length=500)
  student_id: int = Field(ge=0, le=1000000)
  grade: ClassEnum = Field(min_length=3, max_length=50)
  promoted_from: ClassEnum = Field(min_length=3, max_length=50)
  promotion_date: date
  dropout_date: Optional[date]=None
  status: StudentStatus = Field(min_length=3, max_length=50)
  remarks: str = Field(min_length=3, max_length=500)
  created_at: datetime =None
  updated_at: datetime= None

  class Config:
    from_attributes = True  

class CreateGradeTable(GradesBase):
  id:int

class ResponseModelGrade(BaseModel):
  data: Optional[Any] =None
  status: bool = True
  status_code: int = 200
  message: str = "success"

class UpdateGrade(BaseModel):
  student_name: Optional[str]=None
  student_id: Optional[int]=None
  grade: Optional[ClassEnum]=None
  promoted_from: Optional[ClassEnum]=None
  promotion_date: Optional[date] =None
  status: Optional[StudentStatus]=None
  dropout_date: Optional[date]=None
  remarks: Optional[str]=None
  created_at: Optional[datetime]=None
  updated_at: Optional[datetime]=None
  


class GradeHistoryResponse(BaseModel):
  grade: str
  promoted_from: str
  promotion_date: Optional[date]
  dropout_date: Optional[date]
  status: str
  remarks: Optional[str]
  created_at: Optional[datetime]
  updated_at:Optional[datetime]

  class Config:
        orm_mode = True

class ModelGrade(BaseModel):
  status: bool = True
  status_code: int = 200
  message: str = "success"

class GradeResponse(BaseModel):
  id: int
  student: StudentResponse
  history: List[GradeHistoryResponse]
  meta_data: ModelGrade

  class Config:
      orm_mode = True