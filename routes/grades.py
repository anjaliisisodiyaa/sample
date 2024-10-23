from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Grades
from fastapi import HTTPException
from grades_sch import GradesBase,ResponseModelGrade,UpdateGrade
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import asc, desc, func,or_


async def create_grade_table(db: AsyncSession , student: GradesBase):
  try:
    db_student = Grades(
      student_id=student.student_id,
      student_name=student.student_name,
      grade=student.grade,
      promotion_date=student.promotion_date,
      promoted_from=student.promoted_from,  
      dropout_date=student.dropout_date,
      status=student.status,  
      remarks=student.remarks,
      created_at=student.created_at,
      updated_at=student.updated_at
    )
    db.add(db_student)
    await db.commit()
    await db.refresh(db_student)
    print(db_student)
    return ResponseModelGrade(
      data={
        "id": db_student.id,
        "student_id":db_student.student_id,
        "student_name": db_student.student_name,
        "grade":db_student.grade,
        "promoted_from":db_student.promoted_from,
        "promotion_date":db_student.promotion_date,
        "dropout_date":db_student.dropout_date,
        "status":db_student.status,
        "remarks":db_student.remarks,
        "created_at":db_student.created_at,
        "updated_at":db_student.updated_at
    },
    status=True,
    status_code=200,
    message="Student is registered"
        )
  except Exception as error:
    return ResponseModelGrade(
      data=None,
      status=False,
      status_code=404,
      message=str(error)
    )
  
async def update_grade_table(db: AsyncSession, student_id: int, update_student: UpdateGrade):
    try:
      
        result = await db.execute(select(Grades).filter(Grades.id == student_id))
        db_student = result.scalar_one_or_none()

        if not db_student:
            return ResponseModelGrade(
                data=None,
                status=False,
                status_code=404,
                message=f"Grade record with ID {student_id} not found"
            )
        if update_student.student_name is not None:
            db_student.student_name = update_student.student_name
        if update_student.student_id is not None:
            db_student.student_id = update_student.student_id
        if update_student.grade is not None:
            db_student.grade = update_student.grade
        if update_student.promoted_from is not None:
            db_student.promoted_from = update_student.promoted_from
        if update_student.promotion_date is not None:
            db_student.promotion_date = update_student.promotion_date
        if update_student.dropout_date is not None:
            db_student.dropout_date = update_student.dropout_date
        if update_student.status is not None:
            db_student.status = update_student.status
        if update_student.remarks is not None:
            db_student.remarks = update_student.remarks
        if update_student.created_at is not None:
            db_student.created_at = update_student.created_at
        if update_student.updated_at is not None:
            db_student.updated_at = update_student.updated_at

        await db.commit()
        await db.refresh(db_student)

        return ResponseModelGrade(
            data={
                "id": db_student.id,
                "student_id": db_student.student_id,
                "student_name": db_student.student_name,
                "grade": db_student.grade,
                "promoted_from": db_student.promoted_from,
                "promotion_date": db_student.promotion_date,
                "dropout_date": db_student.dropout_date,
                "status": db_student.status,
                "remarks":db_student.remarks,
                "created_at":db_student.created_at,
                "updated_at":db_student.updated_at
            },
            status=True,
            status_code=200,
            message="Student grade updated successfully"
        )

    except Exception as error:
        return ResponseModelGrade(
            data=None,
            status=False,
            status_code=400,
            message=f"Failed to update grade: {str(error)}"
        )
