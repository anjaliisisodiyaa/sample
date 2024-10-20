from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from base.database import Base
from sqlalchemy import Enum as SqlEnum, func
from enum import Enum
from students_sch import ClassEnum

class SubjectEnum(str, Enum):
    english="English"
    hindi="Hindi"
    maths="Maths"
    science="Science"
    sst="SST"
    computer="Computer"
    
class WeekEnum(str, Enum):
    monday="Monday"
    tuesday="Tuesday"
    wednesday="Wednesday"
    thursday="Thursday"
    friday="Friday"
    saturday="Saturday"
    sunday="Sunday"

class Timetable(Base):
    __tablename__ = "timetable"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(SqlEnum(WeekEnum), nullable=False)  
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    subject = Column(SqlEnum(SubjectEnum), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    room_number = Column(String(100), nullable=True)
    
    teacher = relationship("Teachers", back_populates="timetables")
    class_info = relationship("Classes", back_populates="timetables")

class Teachers(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    
    timetables = relationship("Timetable", back_populates="teacher")

class Classes(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    standard = Column(SqlEnum(ClassEnum), nullable=False)
    
    timetables = relationship("Timetable", back_populates="class_info")
