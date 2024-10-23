from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Depends
from typing import Optional,List
from models import SchoolCalendar
from schoolcalendar_sch import SchoolCalendarCreate,SchoolCalendarResponse,SchoolCalendarUpdate,ResponseModelCalendar
from datetime import datetime

async def create_school_calendar_record(db: AsyncSession, record: SchoolCalendarCreate):
    try:
        db_record = SchoolCalendar(
            date=record.date,
            holiday=record.holiday
        )
        db.add(db_record)
        await db.commit()
        await db.refresh(db_record)
        school_calendar = SchoolCalendarResponse(
            sr_no=db_record.sr_no,
            date=db_record.date,
            holiday=db_record.holiday
        )
        return ResponseModelCalendar(
            data=school_calendar,
            status=True,
            status_code=201,
            message="school calendar is successfully created"
        )
    except Exception as error:
        return ResponseModelCalendar(
            data=None,
            status=True,
            status_code=404,
            message=str(error)
        )


async def update_school_calendar_record(db: AsyncSession, sr_no: int, update_data: SchoolCalendarUpdate):
    try:
        stmt = select(SchoolCalendar).filter(SchoolCalendar.sr_no == sr_no)
        result = await db.execute(stmt)
        db_record = result.scalars().first()

        if not db_record:
            return ResponseModelCalendar(
                status=False,
                status_code=404,
                message=f"Attendance record with ID  not found",
                data=None
            )
        if update_data.date is not None:
            db_record.date = update_data.date
        if update_data.holiday is not None:
            db_record.holiday = update_data.holiday

        await db.commit()
        await db.refresh(db_record)
        
        updated_record = SchoolCalendarResponse(
            sr_no=db_record.sr_no,
            date=db_record.date,
            holiday=db_record.holiday
        )
        return ResponseModelCalendar(
            data=updated_record,
            status=True,
            status_code=200,
            message="Holiday record updated successfully"
        )
    except HTTPException as e:
        raise e 
    except Exception as error:
        return ResponseModelCalendar(
            data=None,
            status=False,
            status_code=400,
            message=f"Failed to update school calendar record: {str(error)}"
        )


async def delete_school_calendar_record(db: AsyncSession, sr_no: int):
    try:
        stmt = select(SchoolCalendar).filter(SchoolCalendar.sr_no == sr_no)
        result = await db.execute(stmt)
        db_record = result.scalars().first()

        if not db_record:
            raise HTTPException(status_code=404, detail="Record not found")

        await db.delete(db_record)
        await db.commit()
        return {"message": "Record deleted successfully"}
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"Failed to delete record: {str(error)}")
    
