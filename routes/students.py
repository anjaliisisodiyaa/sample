from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Students
from fastapi import HTTPException
from students_sch import StudentCreate, StudentOut, StudentBase, CreateStudent, ResponseModel,UpdateStudent
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import asc, desc, func,or_


async def create_student(db: AsyncSession , student: StudentBase):
    try:
        db_student = Students(
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            standard=student.standard,
            mobile_number=student.mobile_number,  
            DOB=student.DOB,
            gender=student.gender,  
            guardian_relation=student.guardian_relation,
            guardian_name=student.guardian_name,
            guardian_mobile_number=student.guardian_mobile_number,  
            enrollment_date=student.enrollment_date,
            address=student.address,
            city=student.city,
            state=student.state,
            postal_code=student.postal_code,  
            profile_picture_url=student.profile_picture_url
        )

        db.add(db_student)
        await db.commit()
        await db.refresh(db_student)
        print(db_student)
        # return db_student
        return ResponseModel(
            data={
                "roll_number": db_student.id,
                "first_name":db_student.first_name,
                "last_name": db_student.last_name,
                "standard":db_student.standard,
                "email":db_student.email,
                "mobile_number":db_student.mobile_number,
                "DOB":db_student.DOB,
                "gender":db_student.gender,
                "guardian_relation":db_student.guardian_relation,
                "guardian_name":db_student.guardian_name,
                "guardian_mobile_number":db_student.guardian_mobile_number,
                "enrollment_date":db_student.enrollment_date,
                "address":db_student.address,
                "city":db_student.city,
                "state":db_student.state,
                "postal_code": db_student.postal_code,
                "profile_picture_url":db_student.profile_picture_url                
            },
            status=True,
            status_code=200,
            message="Student is registered"
        )
    except Exception as e:
        # await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------
# from students_sch import ResponseData
# async def get_student_by_id(db: AsyncSession, skip: int = 0, limit: int = 10):
#     try:
#         result = await db.execute(select(Students).offset(skip).limit(limit))
#         students = result.scalars().all()

#         return ResponseData(
#             data=[StudentOut.from_orm(student) for student in students],
#             status=True,
#             status_code=200,
#             message="Students retrieved successfully"
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

async def update_student(db: AsyncSession, student_id: int, student_update: UpdateStudent) -> ResponseModel:
    try:
        result = await db.execute(select(Students).filter(Students.id == student_id))
        db_student = result.scalar_one_or_none()
        if db_student:
            if student_update.first_name is not None:
                db_student.first_name = student_update.first_name
            if student_update.last_name is not None:
                db_student.last_name = student_update.last_name
            if student_update.email is not None:
                db_student.email = student_update.email
            if student_update.standard is not None:
                db_student.standard = student_update.standard
            if student_update.mobile_number is not None:
                db_student.mobile_number = student_update.mobile_number
            if student_update.guardian_mobile_number is not None:
                db_student.guardian_mobile_number = student_update.guardian_mobile_number
            if student_update.DOB is not None:
                db_student.DOB = student_update.DOB
            if student_update.guardian_relation is not None:
                db_student.guardian_relation = student_update.guardian_relation
            if student_update.guardian_name is not None:
                db_student.guardian_name = student_update.guardian_name
            if student_update.city is not None:
                db_student.city = student_update.city
            if student_update.postal_code is not None:
                db_student.postal_code = student_update.postal_code
            if student_update.address is not None:
                db_student.address = student_update.address
            if student_update.state is not None:
                db_student.state = student_update.state     
            if student_update.profile_picture_url is not None:
                db_student.profile_picture_url = student_update.profile_picture_url


            await db.commit()
            await db.refresh(db_student)
            return ResponseModel(
                data=StudentOut.from_orm(db_student),
                status=True,
                status_code=200,
                message="Student updated successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Student not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_student(db: AsyncSession, student_id: int) -> ResponseModel:
    try:
        result = await db.execute(select(Students).filter(Students.id == student_id))
        db_student = result.scalar_one_or_none()

        if db_student:
            await db.delete(db_student)
            await db.commit()
            return ResponseModel(
                data={"student_id": student_id},
                status=True,
                status_code=200,
                message="Student deleted successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Student not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
# async def patch_student(db: AsyncSession, student_id: int, student_update: CreateStudent) -> Optional[Dict[str, Any]]:
#     try:
#         result = await db.execute(select(Students).filter(Students.id == student_id))
#         db_student = result.scalar_one_or_none()

#         if db_student:
#             if student_update.students_name is not None:
#                 db_student.students_name = student_update.students_name
#             if student_update.email is not None:
#                 db_student.email = student_update.email
#             if student_update.roll_number is not None:
#                 db_student.roll_number = student_update.roll_number
#             if student_update.contact_number is not None:
#                 db_student.contact_number = student_update.contact_number
#             if student_update.DOB is not None:
#                 db_student.DOB = student_update.DOB
#             if student_update.sponse_relation is not None:
#                 db_student.sponse_relation = student_update.sponse_relation
#             if student_update.sponse_name is not None:
#                 db_student.sponse_name = student_update.sponse_name
#             if student_update.sponse_number is not None:
#                 db_student.sponse_number = student_update.sponse_number

#             await db.commit()
#             await db.refresh(db_student)
#             return {"message": "Student updated successfully", "student": StudentOut.from_orm(db_student)}
#         else:
#             raise HTTPException(status_code=404, detail="Student not found")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


async def student_id_details(db: AsyncSession, id_constraint: int):
    result = await db.execute(select(Students).filter(Students.id == id_constraint))
    student = result.scalar_one_or_none()
    return student

async def search_student_data(
        db:AsyncSession,
        skip: int=0,
        limit: int=10,
        search: Optional[str] = None,
        gender: Optional[str] = None,
        sort_by: Optional[str] = "first_name",
        sort_order: Optional[str] = "asc"
)-> Tuple[List[Dict[str,Any]],int]:
    try:
        base_query = select(Students)
        if search:
            base_query = base_query.where(
                Students.first_name.ilike(f'%{search}%') |
                Students.email.ilike(f'%{search}%') |
                Students.DOB.ilike(f'%{search}%') |
                Students.standard.ilike(f'%{search}%') 

            )
        if gender:
            base_query = base_query.where(Students.gender == gender)
            

        count_query = select(func.count().label('total_count')).select_from(Students)

        if search:
            count_query = count_query.where(
                Students.first_name.ilike(f'%{search}%') |
                Students.email.ilike(f'%{search}%')|
                Students.DOB.ilike(f'%{search}%')|
                Students.standard.ilike(f'%{search}%')

            )
        if gender:
            count_query = count_query.where(Students.gender == gender)

        count_result = await db.execute(count_query)
        total_items = count_result.scalar()
        paginated_query = base_query.offset(skip).limit(limit)

        if sort_by:
            if sort_by == "first_name":
                paginated_query = paginated_query.order_by(asc(Students.first_name) if sort_order == 'asc' else  desc (Students.first_name))
            elif sort_by == "email":
                paginated_query = paginated_query.order_by(asc(Students.email) if sort_order == 'asc' else desc (Students.email))
            elif sort_by == "DOB":
                paginated_query = paginated_query.order_by(asc(Students.DOB) if sort_order == 'asc' else desc (Students.DOB))
            elif sort_by == "standard":
                paginated_query = paginated_query.order_by(asc(Students.standard) if sort_order == 'asc' else desc (Students.standard))
            
        result = await db.execute(paginated_query)
        students = result.scalars().all()
        students_details = [student.__dict__ for student in students]
        print(students_details)
        return students_details,total_items
    
    # except Exception as error:
    #     print(error)
    #     raise

    except Exception as error:
        return ResponseModel(
            data=None,
            status=False,
            status_code=500,
            message=f"An error occurred: {str(error)}"
        )
    