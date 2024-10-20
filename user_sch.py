from pydantic import BaseModel, EmailStr, Field
from typing import List,Optional, Any
from enum import Enum


class Role(str, Enum):
    admin = "Admin"
    student = "Student"
    hod = "HOD"
    principal = "Principal"

class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool


    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    first_name: str
    last_name: str
    email: str
    contact_number: int


class UserIdResponse(BaseModel):
    users_ids : List[int]
    users : List[UserCreate]

class UserResponseId(BaseModel):
    id: int
    name: str
    email : EmailStr

    class Config:
        from_attributes = True

class CreateUser(UserBase):
    username: Optional[str] = None
    email: Optional[str] = None

class UserOut(UserBase):
    is_active: bool


class TokenData(BaseModel):
    username:str
    password:str

class AuthenticationResponse(BaseModel):
    status: str
    message: str


class SignUser(BaseModel):
    first_name: str = Field(min_length=3, max_length=100)
    last_name: str = Field(min_length=3, max_length=100)
    email: EmailStr = Field(min_length=3, max_length=100)
    contact_number: int = Field(ge=1000000000, le=9999999999) 
    password: str = Field(min_length=8, max_length=16)
    gender: GenderEnum = Field(min_length=3, max_length=50)
    age: int = Field(ge=2, le=99)  
    role: Role = Field(min_length=3, max_length=50)
    
class SignUserResponse(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    contact_number: int
    gender: GenderEnum
    age: int
    role: Role

    class Config:
        from_attributes = True

class Login(BaseModel):
    email: EmailStr
    password: str


class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str



class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetVerify(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


class ResponseModel(BaseModel):
    data: Optional[Any] = None
    status: bool = True
    status_code: int = 200
    message: str = "success"


