# models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey,Boolean, Date, BigInteger, DateTime
from sqlalchemy import Enum as SqlEnum, func
from user_sch import GenderEnum, Role
from base.database import Base
from datetime import datetime
from students_sch import ClassEnum, StudentStatus, Enum
# from enum import Enum
from attendance_sch import  AttendanceEnum
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String(50), index=True)
    last_name = Column(String(50), index=True)
    email = Column(String(100), unique=True, index=True)
    contact_number = Column(BigInteger, unique=True)  
    status = Column(Boolean, default=True)
    password = Column(String(100),index=True)
    is_email_verified = Column(Boolean,default=True)
    gender = Column(SqlEnum(GenderEnum), nullable=False,index=True)
    age = Column(Integer, index=True)
    is_deleted = Column(Boolean, default=False)
    role = Column(SqlEnum(Role), nullable=False, index=True)
    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password)

    def set_password(self, plain_password: str) -> None:
        self.password = pwd_context.hash(plain_password)


class Students(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(500), index=True, nullable=False)
    last_name = Column(String(500), index=True, nullable=False) 
    standard =Column(SqlEnum(ClassEnum), nullable=False, index=True)   
    gender = Column(String(10), nullable=True)
    email = Column(String(500), index=True, nullable=False)
    mobile_number = Column(BigInteger, index=True, nullable=False)
    DOB = Column(Date, index=True, nullable=False)
    enrollment_date = Column(Date, nullable=True)
    guardian_relation = Column(String(50), index=True, nullable=True)
    guardian_name = Column(String(100), index=True, nullable=True)
    guardian_mobile_number = Column(BigInteger, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(Integer, nullable=True)
    profile_picture_url = Column(String(500), nullable=True)

    grades = relationship("Grades", back_populates="student")
    attendances = relationship("Attendance", back_populates="student")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    grade = Column(SqlEnum(ClassEnum), nullable=False, index=True)
    date = Column(DateTime, server_default=func.now()) 
    attendance = Column(Boolean,default=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    student = relationship("Students", back_populates="attendances")


class Grades(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(500), index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    grade = Column(SqlEnum(ClassEnum), nullable=False, index=True)
    promoted_from = Column(SqlEnum(ClassEnum), nullable=False, index=True)
    promotion_date = Column(Date, nullable=True)
    dropout_date = Column(Date, nullable=True)  
    status = Column(SqlEnum(StudentStatus), nullable=False, index=True, default="Active") 
    remarks = Column(String(255), nullable=True) 
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())

    student = relationship("Students", back_populates="grades")

class SchoolCalendar(Base):
    __tablename__ = "schoolcalendar"

    sr_no = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    holiday = Column(String(500), index=True, nullable=False)
     

