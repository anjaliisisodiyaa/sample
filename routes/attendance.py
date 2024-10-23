from models import Attendance
from attendance_sch import AttendanceBase, AttendanceResponse, ResponseModelGrade,ResponseModelAttendance,AttendanceUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from models import SchoolCalendar
from students_sch import ClassEnum
from datetime import datetime

async def create_attendance_record(db: AsyncSession, attendance: AttendanceBase):
  try:
    db_attendance = Attendance(
      student_id=attendance.student_id,
      grade=attendance.grade,
      date=attendance.date,
      attendance=attendance.attendance
      )

    db.add(db_attendance)
    await db.commit()
    await db.refresh(db_attendance)

    attendance_response = AttendanceResponse(
      id=db_attendance.id,
      grade=db_attendance.grade,
      date=db_attendance.date,
      attendance=db_attendance.attendance,
      student_id=db_attendance.student_id
      )
        
    return ResponseModelAttendance(
      status=True,
      status_code=201,
      message="Attendance record created successfully",
      data=attendance_response
      )
  except Exception as error:
    return ResponseModelAttendance(
      status=False,
      status_code=500,
      message=str(error),
      data=None
      )


async def update_attendance_record(db: AsyncSession, attendance_id: int, update_data: AttendanceUpdate):
    try:
        stmt = select(Attendance).filter(Attendance.id == attendance_id)
        result = await db.execute(stmt)
        db_attendance = result.scalars().first()

        if not db_attendance:
            return ResponseModelAttendance(
                status=False,
                status_code=404,
                message=f"Attendance record with ID {attendance_id} not found",
                data=None
            )

        if update_data.grade is not None:
            db_attendance.grade = update_data.grade
        if update_data.date is not None:
            db_attendance.date = update_data.date
        if update_data.attendance is not None:
            db_attendance.attendance =update_data.attendance

        await db.commit()
        await db.refresh(db_attendance)
        return ResponseModelAttendance(
            status=True,
            status_code=200,
            message="Attendance record updated successfully",
            data=AttendanceResponse(
                id=db_attendance.id,
                grade=db_attendance.grade,
                date=db_attendance.date,
                attendance=db_attendance.attendance,
                student_id=db_attendance.student_id
            )
        )
    except Exception as error:
        return ResponseModelGrade(
            data=None,
            status=False,
            status_code=500,
            message=f"Failed to update attendance: {str(error)}"
        )
    
async def record_attendance(date: datetime, student_id: int, grade: ClassEnum, db: AsyncSession):
    try:
        if date.weekday() == 6:  
            return ResponseModelAttendance(
                data=None,
                status=False,
                status_code=400,  
                message="Attendance cannot be marked on Sundays"
            )
        query = select(SchoolCalendar).filter(SchoolCalendar.date == date)
        result = await db.execute(query)
        holiday = result.scalars().first()

        if holiday:
            return ResponseModelAttendance(
                data=None,
                status=False,
                status_code=400,  
                message="Attendance cannot be marked on holidays"
            )
        
        attendance_query = select(Attendance).filter(
            Attendance.date == date,
            Attendance.student_id == student_id
        )
        attendance_result = await db.execute(attendance_query)
        existing_attendance = attendance_result.scalars().first()

        if existing_attendance:
            return ResponseModelAttendance(
                data=None,
                status=False,
                status_code=400,  
                message="Attendance has already been marked for this day"
            )
        
        attendance = Attendance(date=date, student_id=student_id, grade=grade, attendance=True)

        db.add(attendance)
        await db.commit()
        await db.refresh(attendance)

        return ResponseModelAttendance(
            data={"date": date, "student_id": student_id, "grade": grade},
            status=True,
            status_code=201,
            message="Attendance recorded successfully"
        )
    except Exception as error:
        return ResponseModelAttendance(
            data=None,
            status=False,
            status_code=500,  
            message=str(error)
        )
