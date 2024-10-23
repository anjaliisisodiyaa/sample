from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, List, Any, Dict
from datetime import date
from enum import Enum

class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"

class Guardian(str, Enum):
    father = "Father"
    mother = "Mother"
    guardians = "GrandParents"
    other = "other"

class ClassEnum(str, Enum):
    first = "First"
    second = "Second"
    third = "Third"
    forth = "4th"
    fifth = "5th"
    sixth = "6th"
    seventh = "7th"
    eighth = "8th"
    ninth = "9th"
    tenth = "10th"
    eleventh = "11th"
    twelfth = "12th"

class StudentStatus(str, Enum):
    ACTIVE = "active"
    DROPPED = "dropped"
    COMPLETED = "completed"


class StudentBase(BaseModel):
    first_name: str = Field(min_length=3, max_length=500)
    last_name: str = Field(min_length=3, max_length=500)
    email: EmailStr = Field(min_length=3, max_length=500)
    mobile_number: int = Field(ge=1000000000, le=9999999999) 
    standard: ClassEnum = Field(min_length=3, max_length=50)
    DOB: date
    gender: GenderEnum = Field(min_length=3, max_length=50) 
    guardian_relation: Guardian = Field(min_length=3, max_length=10)
    guardian_name: str = Field(min_length=3, max_length=100)
    guardian_mobile_number: int = Field(ge=1000000000, le=9999999999)
    enrollment_date: date
    address: str = Field(min_length=5, max_length=255)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=100)
    postal_code: int = Field(ge=100000, le=999999)  
    profile_picture_url: str 

    class Config:
        from_attributes = True          

class StudentCreate(StudentBase):
    id:int

class StudentOut(StudentBase):
    id: int

    class Config:
        from_attributes = True
        
class UpdateStudent(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    mobile_number: Optional[int] = None
    standard: ClassEnum = None
    DOB: Optional[date] = None
    gender: Optional[str] = None
    guardian_relation: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_mobile_number: Optional[int] = None
    enrollment_date: Optional[date] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    profile_picture_url: Optional[str] = None



class StudentResponseId(BaseModel):
    id: int
    students_name: str
    email: Optional[str] = None
    roll_number: int
    contact_number: str
    DOB: Optional[int] = None
    guardian_relation: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_mobile_number: Optional[str] = None

    class Config:
        from_attributes = True

class CreateStudent(StudentBase):
    id: Optional[int] = None
    students_name: Optional[str] = None
    email: Optional[str] = None
    roll_number: Optional[int] = None
    contact_number: Optional[str] = None
    DOB: Optional[int] = None
    guardian_relation: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_mobile_number: Optional[str] = None

class ResponseModel(BaseModel):
    data: Optional[Any] =None
    status: bool = True
    status_code: int = 200
    message: str = "success"

class ResponseData(BaseModel):
    data: List[StudentCreate]
    status: bool = True
    status_code: int = 200
    message: str = "success"


class PaginationMetadata(BaseModel):
    total_count: int
    total_pages: int
    current_page: int
    page_size: int


    class Config:
        orm_mode = True

class StudentResponseData(BaseModel):
    students: List [ResponseData]
    meta_data: Dict[str,Any] 

class PaginatedStudentResponse(BaseModel):
    data: List[StudentResponseData]
    metadata: PaginationMetadata
    
class StudentResponse(StudentCreate):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    mobile_number: int
    standard: ClassEnum
    DOB: date
    gender: GenderEnum
    guardian_relation: Guardian
    guardian_name: str
    guardian_mobile_number: int
    enrollment_date: date
    address: str
    city: str
    state: str
    postal_code: int
    profile_picture_url: str