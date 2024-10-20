
from fastapi import HTTPException,Depends, FastAPI, Query, status, security
from routes.users import get_user, get_users, create_user, search_user, user_id_details, update_user, delete_user,patch_user
from routes.students import StudentCreate,AsyncSession, create_student, student_id_details, update_student,delete_student,search_student_data
from dependency.get_db import get_db
from middleware import Request 
from students_sch import ResponseData
from routes.users import UserCreate,CreateUser
from routes.students import StudentCreate,CreateStudent, UpdateStudent
from user_sch import UserResponse,UserIdResponse,UserResponseId,TokenData
from students_sch import StudentResponse, StudentResponseId, StudentBase,StudentResponse,StudentResponseData
from typing import Optional,Dict
from fastapi.security import HTTPBasicCredentials,HTTPBasic
from models import Students
from auth import SignUser,signup
from user_sch import ResponseModel
from pydantic import EmailStr
from sqlalchemy import or_
from datetime import timedelta
from security import create_jwt_token, verify_jwt_token,jwt
from sqlalchemy.future import select
from user_sch import Login,ResponseModel
from fastapi.security import OAuth2PasswordBearer
from dependency.get_db import get_db  
from models import User,Grades
from utilis import generate_otp,send_email,validate_otp,hash_password,store_otp
from user_sch import OTPRequest,OTPVerify
from user_sch import PasswordResetRequest,PasswordResetVerify,Role
from security import SECRET_KEY,ALGORITHM
from grades_sch import ResponseModelGrade,GradesBase,UpdateGrade
from routes.grades import create_grade_table,update_grade_table
from grades_sch import GradeResponse, GradeHistoryResponse,ModelGrade
from typing import List
from sqlalchemy.orm import joinedload
from uploads import UploadFile, File,upload_profile_picture
from attendance_sch import ResponseModelAttendance,AttendanceBase,AttendanceResponse
from attendance_sch import AttendanceUpdate,AttendanceRequest
from routes.attendance import update_attendance_record,record_attendance
from models import Attendance
from schoolcalendar_sch import ResponseModelCalendar,SchoolCalendarCreate,SchoolCalendarUpdate
from routes.schoolcalendar import create_school_calendar_record,update_school_calendar_record,delete_school_calendar_record
# from routes.attendance import get_sundays
from datetime import datetime
from models import SchoolCalendar


security = HTTPBasic()

app = FastAPI()

@app.get("/server_is_on")
async def check_server(request:Request):
    return {"status": "ok", "message": "Server is running", "method": request.method}

@app.post('/signup', summary="Create new user", response_model=ResponseModel)
async def signup_user(
    user: SignUser,
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    try:
        response = await signup(user, db)
        return ResponseModel(
            data={
                "first_name": response.first_name,
                "last_name": response.last_name,
                "email": response.email,
                "gender": response.gender,
                "role": response.role,
                "age": response.age,
                "contact_number": response.contact_number
            },
            status=True,
            status_code=200,
            message="User created successfully"
        )
    except Exception as e:
        return ResponseModel(
            data = None,
            status = False,
            status_code = 500,
            message = "An unexpected error occurred"
        )
# ----------------------------------------------------------------

    #     if students:
    #         return ResponseModel(
    #             data=students,
    #             status=True,
    #             status_code=200,
    #             message="Students retrieved successfully"
    #         )
    #     else:
    #         return ResponseModel(
    #             data=None,
    #             status=False,
    #             status_code=404,
    #             message="No students found"
    #         )
        
    # except Exception as error:
    #     return ResponseModel(
    #         data=None,
    #         status=False,
    #         status_code=500,
    #         message=f"An error occurred: {str(error)}"
    #     )


@app.put("/students/{student_id}",response_model=ResponseModel)
async def put_student_endpoint(
    student_id: int,
    student_update: UpdateStudent,
    db: AsyncSession = Depends(get_db)
):
    updated_student = await update_student(db, student_id, student_update)
    if updated_student:
        return updated_student
    else:
        raise HTTPException(status_code=404, detail="Student not found")
    
@app.delete("/students/{student_id}")
async def delete_student_endpoint(
    student_id: int,
    db: AsyncSession = Depends(get_db)
):
    response = await delete_student(db, student_id)
    return response

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def verify_user_credentials(email: str, password: str, db: AsyncSession) -> bool:
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalar_one_or_none()
    if user and user.verify_password(password) and user.role == Role.admin:  
        return {"message":"YOUR USER IS VERIFIED"}
    return {"message":"YOUR USER IS NOT VERIFIED"}

@app.post("/login_users", response_model=ResponseModel)
async def login(user: Login, db: AsyncSession =Depends(get_db)):
    try:    
        if await verify_user_credentials(user.email, user.password, db):
            expires = timedelta(minutes=30) 
            token = create_jwt_token(subject=user.email, expires_delta=expires)
            query = select(User).where(User.email == user.email)

            result = await db.execute(query)
            users = result.scalars().first()

            if not users:
                return ResponseModel(
                    data=None,
                    status=False,
                    status_code=404,
                    message="User not found"
                )
            
            # if users.role != Role.admin:
            #         return ResponseModel(
            #         data=None,
            #         status=False,
            #         status_code=404,
            #         message="Access forbidden: only admins can log in"
            #     )
            
            if not users.status:
                return ResponseModel(
                    data=None,
                    status=False,
                    status_code=403,
                    message="Account is inactive"
                )
            
            dict_data = {
                'access_token':token,
                'token_type': "bearer",
                'first_name':users.first_name,
                'last_name':users.last_name,
                'email':users.email,
                'contact_number':users.contact_number,
                'gender':users.gender,
                'age':users.age,
                'verfication':users.is_email_verified
            }
            
            # if users.role == Role.admin:
            #     return ResponseModel(
            #         data=dict_data,
            #         status=True,
            #         status_code=201,
            #         message="Admin login successfully"
            #     )
            return ResponseModel(
                data=dict_data,
                status=True,
                status_code=201,
                message="Login successfully"
                
            )
        else:
            return ResponseModel(
                data=None,
                status=False,
                status_code=402,
                message="Invalid Credentials"
            )
    except Exception as e :
        return ResponseModel(
            data=None,
            status=False,
            status_code=402,
            message="Email should be registered"
        )        

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = verify_jwt_token(token)
        user = payload.get("sub")
        if user is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return user


@app.get("/current_user")
async def current_user(current_user: str = Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    try:
        query = select(User).where(User.email == current_user)
        result = await db.execute(query)
        user = result.scalars().first()

        user_data = UserResponse(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            contact_number=user.contact_number,
            status=user.status,
            is_email_verify=user.is_email_verified,
            age=user.age,
            gender=user.gender
        )
        return ResponseModel(
            data=user_data,
            status=True,
            status_code=201,  
            message="Token is successfully accessed"
        )
    except Exception as error:
        print(f"Exception occurred: {error}")
        return ResponseModel(
            data=None,
            status=False,
            status_code=500, 
            message=f"Server error occurred {error}"
        )
    
async def admin_required(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: only admins can access this resource"
        )

@app.get("/students", response_model=ResponseModel)
async def get_students(db: AsyncSession = Depends(get_db), admin: bool = Depends(admin_required)):
    query = select(Students)
    result = await db.execute(query)
    students = result.scalars().all()

    return ResponseModel(
        data=students,
        status=True,
        status_code=status.HTTP_200_OK,
        message="Students retrieved successfully"
    )

@app.post("/create_students/")
async def create_student_endpoint(student: StudentBase, db: AsyncSession = Depends(get_db), token:str=Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        result = await db.execute(select(User).filter(User.email == email))
        user = result.scalar_one_or_none()
        if user.role != Role.admin:
            return ResponseModel(
                data=None,
                status=False,
                status_code=403,
                message="Access forbidden: only admins can create students"
            )

        new_student = await create_student(db,student)
        return new_student
    except Exception as e:
        return ResponseModel(
            data = None,
            status = False,
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            message = f"An unexpected error occurred{e}"
        )
    
@app.post("/request-otp")
async def request_otp(otp_request: OTPRequest,db:AsyncSession=Depends(get_db)):
    email = otp_request.email
    try:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
 
        if not user:
            return ResponseModel(
                data=None,
                status=False,
                status_code=404,
                message="Email not registered"
            )
        
        otp = generate_otp()
        store_otp(email, otp) 
        send_email(email, otp)  
        return ResponseModel(
            data=None,
            status=True,
            status_code=200,  
            message="OTP sent to your email"
        )
    except Exception as e:
        print(f"Exception occurred: {e}") 
        return ResponseModel(
            data=None,
            status=False,
            status_code=500,  
            message="Server error occurred"
        )

@app.post("/verify-otp")
async def verify_otp(otp_verify: OTPVerify,db:AsyncSession =Depends(get_db)):
    email = otp_verify.email
    otp = otp_verify.otp
    try:
        if not validate_otp(email, otp):
            return ResponseModel(
                data=None,
                status=False,
                status_code=400,  
                message="Invalid or expired OTP"
            )
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        user = result.scalars().first()

        user_data = UserResponse(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            contact_number=user.contact_number,
            age=user.age,
            gender=user.gender
            )
        return ResponseModel(
            data=user_data,
            status=True,
            status_code=200,  
            message="OTP verified successfully"
        )
    
    except Exception as e:

        print(f"Exception occurred: {e}")  
        return ResponseModel(
            data=None,
            status=False,
            status_code=500,
            message="Server error occurred"
        )

@app.post("/forget-password/")
async def forget_password(request: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    email = request.email
    try:
        user = await db.execute(select(User).where(User.email == email))
        user = user.scalar_one_or_none()
        
        if not user:
            return ResponseModel(
                data=None,
                status=False,
                status_code=404,
                message="Email must be registered"
            )
        
        otp = generate_otp()
        store_otp(email, otp)
        
        send_email(email, otp)

        return ResponseModel(
                data=email,
                status=True,
                status_code=200,  
                message="OTP sent to your email"
            )
    except Exception as e:
        print(f"Exception occurred: {e}")
        return ResponseModel(
            data=None,
            status=False,
            status_code=500, 
            message="Server Error"
        )

@app.post("/reset-password/")
async def reset_password(request: PasswordResetVerify, db: AsyncSession = Depends(get_db)):
    email = request.email
    otp = request.otp
    new_password = request.new_password

    try:
        if not validate_otp(email, otp):
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
        user = await db.execute(select(User).where(User.email == email))
        user = user.scalar_one_or_none()
        
        if not validate_otp(email, otp):
            return ResponseModel(
                data=None,
                status=False,
                status_code=400,  
                message="Invalid or expired OTP"
            )
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            return ResponseModel(
                data=None,
                status=False,
                status_code=404,  
                message="User not found"
            )
        hashed_password = hash_password(new_password)
        user.password = hashed_password
        await db.commit()

        return ResponseModel(
            data=None,
            status=True,
            status_code=200, 
            message="Password updated successfully"
        )
    except Exception as e:
        print(f"Exception occurred: {e}")
        return ResponseModel(
            data=None,
            status=False,
            status_code=500,  
            message="Something went wrong"
        )

@app.get("/is_id_exist", response_model=ResponseModel)
async def is_id_exist(
    email: Optional [EmailStr] = Query(None, min_length=1),
    contact_number: Optional[str] = Query(None, min_length=10, max_length=10),
    db: AsyncSession = Depends(get_db)
):
    try:
        if email and contact_number:
            return ResponseModel(
                data=None,
                status=False,
                status_code=400,
                message="Only one search parameter can be provided at a time."
            )
    
        filters = []
        if email:
            filters.append(User.email == email)

        if contact_number:
            filters.append(User.contact_number == contact_number)

        if not filters:
            return ResponseModel(status=False, status_code=400, message="At least one search parameter must be provided." )

        result = await db.execute(select(User).where(or_(*filters)))
        user = result.scalars().first()

        if user:
            return ResponseModel(
                data = {
                    "exists": True,
                    "user_id": user.id, 
                    "age": user.age, 
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "contact_number": user.contact_number, 
                    "email": user.email, 
                    "gender": user.gender
                },
                message="User Exist"
            )
        else:
            return ResponseModel(status=False, status_code=204, message="No Content")
        
    except Exception as e:
        print(f"Exception occurred: {e}")
        return ResponseModel(status=False, status_code=500, message="Server error occurred")
    
@app.get("/search_students")
async def fetch_student(
    db: AsyncSession = Depends(get_db), 
    search: Optional[str] = None, 
    page: int= Query(0,ge=0),
    gender:Optional[str]=None, 
    page_size: int= Query(10,ge=0), 
    sort_by: Optional[str]= Query("first_name", pattern='^(first_name|email|DOB|standard)$'), 
    sort_order: Optional[str]= Query("asc",pattern='^(asc|desc)$')
    )-> StudentResponseData:
    skip = max(0,(page - 1) * page_size)
    limit = page_size

    student_data, total_student = await search_student_data(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        gender=gender,
        sort_by=sort_by,
        sort_order=sort_order   
    )
    total_pages = (total_student + page_size - 1) // page_size
    if not student_data:
        return StudentResponseData(
            students=[ResponseData(
                data=[],
                status=True,
                status_code=200,
                message="No students found"
            )],
            meta_data={
                'current_page': page,
                'page_size': page_size,
                'total_pages': 0,  
                'total_items': 0
            }
        )
    print(student_data, total_pages)
    return StudentResponseData(
        students= [ResponseData(
            data=student_data,
            status=True,
            status_code=200,
            message="Students retrieved successfully")],
        meta_data={
            'current_page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'total_items': total_student
        }
    )

@app.post("/create_grades",response_model=ResponseModelGrade)
async def create_grade_endpoint(grade: GradesBase, db: AsyncSession = Depends(get_db)):
    try:
        student_grade = await create_grade_table(db, grade)
        return student_grade
    except Exception as error:
        print(f"Exception occurred: {error}")
        return ResponseModel(
            data=None,
            status=False,
            status_code=500,  
            message="Something went wrong"
        )
    
@app.put("/grades/{student_id}", response_model=ResponseModelGrade)
async def update_grade_endpoint(
    student_id: int,
    update_grade: UpdateGrade,
    db: AsyncSession = Depends(get_db)
):
    updated_grade = await update_grade_table(db, student_id, update_grade)
    if updated_grade:
        return updated_grade
    else:
        raise HTTPException(status_code=404, detail="Grade record not found")




@app.delete("/grades/{student_id}", response_model=ResponseModelGrade)
async def delete_grade_endpoint(
    student_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:

        result = await db.execute(select(Grades).filter(Grades.id == student_id))
        db_grade = result.scalar_one_or_none()

        if not db_grade:
            raise HTTPException(status_code=404, detail="Grade record not found")

        await db.delete(db_grade)
        await db.commit()

        return ResponseModelGrade(
            data=None,
            status=True,
            status_code=200,
            message="Grade record deleted successfully"
        )

    except Exception as error:
        return ResponseModelGrade(
            data=None,
            status=False,
            status_code=400,
            message=f"Failed to delete grade: {str(error)}"
        )

from models import Students
@app.get("/grades", response_model=List[GradeResponse])
async def get_all_grades(db: AsyncSession = Depends(get_db)):
    try:

        query = (
            select(Grades)
            .options(joinedload(Grades.student))
        )
        result = await db.execute(query)
        grades = result.scalars().all()

        if not grades:
            return []

        student_grades = {}

        for grade in grades:
            student_id = grade.student.id
            if student_id not in student_grades:
                student_grades[student_id] = {
                    "student": StudentResponse(
                        id=grade.student.id,
                        first_name=grade.student.first_name,
                        last_name=grade.student.last_name,
                        email=grade.student.email,
                        mobile_number=grade.student.mobile_number,
                        standard=grade.student.standard,
                        DOB=grade.student.DOB,
                        gender=grade.student.gender,
                        guardian_relation=grade.student.guardian_relation,
                        guardian_name=grade.student.guardian_name,
                        guardian_mobile_number=grade.student.guardian_mobile_number,
                        enrollment_date=grade.student.enrollment_date,
                        address=grade.student.address,
                        city=grade.student.city,
                        state=grade.student.state,
                        postal_code=grade.student.postal_code,
                        profile_picture_url=grade.student.profile_picture_url,
                    ),
                    "history": []
                }
            student_grades[student_id]["history"].append(
                GradeHistoryResponse(
                    grade=grade.grade,
                    promoted_from=grade.promoted_from,
                    promotion_date=grade.promotion_date,
                    dropout_date=grade.dropout_date,
                    status=grade.status,
                    remarks=grade.remarks,
                    created_at=grade.created_at,
                    updated_at=grade.updated_at
                )
            )
        response = [
            GradeResponse(
                id=student_id,
                student=data["student"],
                history=data["history"],
                meta_data=ModelGrade(
                    status=True,
                    status_code=201,
                    message="Data fetched successfully"
                )
            )
            for student_id, data in student_grades.items()
        ]
        return response
    except Exception as error:
        return ResponseModelGrade(
            data=None,
            status=False,
            status_code=404,
            message=str(error)
        )

@app.post("/students/{student_id}/profile_picture_url")
async def upload_pic(student_id: int, file: UploadFile = File(), db:AsyncSession =Depends(get_db)):
    upload_profile = await upload_profile_picture(student_id, file, db)
    return upload_profile

@app.get("/students/{student_id}/history", response_model=List[GradeHistoryResponse])
async def get_student_history(student_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = select(Students).filter(Students.id == student_id)
        result = await db.execute(query)
        student = result.scalars().first()
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        

        query = select(Grades).filter(Grades.student_id == student_id)
        result = await db.execute(query)
        history = result.scalars().all()
        
        if not history:
            raise HTTPException(status_code=404, detail="No history found for the student")
        

        history_responses = [
            GradeHistoryResponse(
                grade=entry.grade,
                promoted_from=entry.promoted_from,
                promotion_date=entry.promotion_date,
                dropout_date=entry.dropout_date,
                status=entry.status,
                remarks=entry.remarks,
                created_at=entry.created_at,
                updated_at=entry.updated_at
            ) for entry in history
        ]
        return history_responses        
    except Exception as error:
        return error
    
@app.post("/attendance/", response_model=ResponseModelAttendance)
async def create_attendance(attendance: AttendanceBase, db: AsyncSession = Depends(get_db)):
    try:
        new_attendance = Attendance(
            grade=attendance.grade,
            date=attendance.date,
            attendance=attendance.attendance,
            student_id=attendance.student_id
        )
        db.add(new_attendance)
        await db.commit()
        await db.refresh(new_attendance)

        return ResponseModelAttendance(
            status=True,
            status_code=201,
            message="Attendance record created successfully",
            data=AttendanceResponse(
                id=new_attendance.id,
                grade=new_attendance.grade,
                date=new_attendance.date,
                attendance=new_attendance.attendance,
                student_id=new_attendance.student_id
            )
        )
    except Exception as error:
   
        return ResponseModelAttendance(
            status=False,
            status_code=500,
            message=str(error),
            data=None
        )

@app.put("/attendance/{attendance_id}", response_model=ResponseModelAttendance)
async def update_attendance_endpoint(
    attendance_id: int,
    update_data: AttendanceUpdate,
    db: AsyncSession = Depends(get_db)
):
    updated_attendance = await update_attendance_record(db, attendance_id, update_data)
    if updated_attendance:
        return updated_attendance
    else:
        return ResponseModel(
            data=None,
            status=True,
            status_code=404,
            message="not found"
        )
@app.delete("/attendance/{attendance_id}", response_model=ResponseModelGrade)
async def delete_attendance_endpoint(
    attendance_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(Attendance).filter(Attendance.id == attendance_id)
        result = await db.execute(stmt)
        db_attendance = result.scalars().first()

        if not db_attendance:
            raise HTTPException(status_code=404, detail="Attendance record not found")

        await db.delete(db_attendance)
        await db.commit()

        return ResponseModelGrade(
            data=None,
            status=True,
            status_code=200,
            message="Attendance record deleted successfully"
        )

    except Exception as error:
        return ResponseModelGrade(
            data=None,
            status=False,
            status_code=400,
            message=f"Failed to delete attendance: {str(error)}"
        )

@app.post("/school-calendar/", response_model=ResponseModelCalendar)
async def create_school_calendar(
    record: SchoolCalendarCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        response = await create_school_calendar_record(db, record)
        return response
    except Exception as error:
        return ResponseModelCalendar(
            data=None,
            status=False,
            status_code=400,
            message=str(error)
        )
    
@app.put("/school-calendar/{sr_no}", response_model=ResponseModelCalendar)
async def update_school_calendar(
    sr_no: int,
    update_data: SchoolCalendarUpdate,
    db: AsyncSession = Depends(get_db)
):
    try:
        response = await update_school_calendar_record(db, sr_no, update_data)
        return response
    except Exception as error:
        return ResponseModelCalendar(
            data=None,
            status=False,
            status_code=500,
            message=str(error)
        )
    
@app.delete("/school-calendar/{sr_no}", response_model=ResponseModelCalendar)
async def delete_school_calendar(
    sr_no: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        response = await delete_school_calendar_record(db, sr_no)
        
        return ResponseModelCalendar(
            data=None,
            status=True,
            status_code=200,
            message="Record deleted successfully"
        )
    except HTTPException as error:
        return ResponseModelCalendar(
            data=None,
            status=False,
            status_code=error.status_code,
            message=error.detail
        )
    except Exception as error:
        return ResponseModelCalendar(
            data=None,
            status=False,
            status_code=500,
            message=f"Failed to delete record: {str(error)}"
        )

@app.post("/attendance/record/", response_model=ResponseModelAttendance)
async def api_record_attendance(
    request: AttendanceRequest,
    db: AsyncSession = Depends(get_db)
):
    response = await record_attendance(request.date, request.student_id, request.grade, db)
    return response
from students_sch import ClassEnum

@app.get("/attendance/report/")
async def get_attendance_report(
    student_id: int,
    grade: ClassEnum,
    start: str,
    end: str,
    # total_days: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        
        query = select(Attendance).filter(
                Attendance.student_id == student_id,
                Attendance.grade == grade,
                Attendance.date.between(start_date, end_date)
            )
        result = await db.execute(query)
        records = result.scalars().all()
        
        total_attended = sum(1 for record in records if record.attendance)
        total_days_in_period = (end_date - start_date).days + 1

        total_leave_days = total_days_in_period - total_attended
        attendance_data = [
            {
                "date": record.date.strftime('%Y-%m-%d'),
                # "grade": record.grade,
                "attendance": record.attendance
            }
            for record in records
        ]
        
        return {
            "student_id": student_id,
            "grade": grade,
            "total_days_in_period": total_days_in_period,
            "total_days_attended": total_attended,
            "total_leave_days": total_leave_days,
            "records": attendance_data
        }
    
    except Exception as error:
        return ResponseModelAttendance(
            data=None,
            status=False,
            status_code=404,
            message=str(error)
        )
from new_models import Timetable
from timetable_sch import TimetableCreate,TimetableResponseData
from teachers_sch import TeacherCreate,TeacherResponse
from classes_sch import ClassCreate, ClassResponse

@app.post("/teachers")
async def add_teachers(teacher_data: TeacherCreate, db: AsyncSession = Depends(get_db)):
    new_data = TeacherCreate(
        id=teacher_data.id,
        first_name=teacher_data.first_name,
        last_name=teacher_data.last_name
    )
    db.add(new_data)
    await db.commit()
    await db.refresh(new_data)
    return TeacherResponse(
        data=new_data,
        status=True,
        status_code=200,
        message="Teacher details are saved"
    )
@app.post("/classes")
async def add_classes(class_data: ClassCreate, db: AsyncSession = Depends(get_db)):
    new_classes = ClassCreate(
        id=class_data.id,
        standard=class_data.standard
    )
    db.add(new_classes)
    await db.commit()
    await db.refresh(new_classes)
    return ClassResponse(
        data=new_classes,
        status=True,
        status_code=200,
        message="Classes are listed"
    )

@app.post("/timetable")
async def add_timetable_entry(timetable_data: TimetableCreate, db: AsyncSession = Depends(get_db)):
    new_timetable = Timetable(
        day_of_week=timetable_data.day_of_week,
        start_time=timetable_data.start_time,
        end_time=timetable_data.end_time,
        subject=timetable_data.subject,
        teacher_id=timetable_data.teacher_id,
        class_id=timetable_data.class_id,
        room_number=timetable_data.room_number
    )
    
    db.add(new_timetable)
    await db.commit()
    await db.refresh(new_timetable)
    return TimetableResponseData(
        data=new_timetable,
        status=True,
        status_code=200,
        message="TimeTable is created."
    )