from fastapi import UploadFile, File, Depends, HTTPException
from routes.students import AsyncSession
from dependency.get_db import get_db
from models import Students
from sqlalchemy.future import select
import os


async def upload_profile_picture(
    student_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    valid_extensions = {"jpg", "jpeg", "png"}
    file_extension = file.filename.split(".")[-1]
    if file_extension not in valid_extensions:
        raise HTTPException(status_code=400, detail="Invalid file format")

    file_location = f"static/{file.filename}"
    if not os.path.exists("static"):
        os.makedirs("static")

    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    result = await db.execute(select(Students).filter(Students.id == student_id))
    student = result.scalar_one_or_none()

    if student:
        student.profile_picture_url = file_location
        await db.commit()
        return {"message": "Profile picture uploaded successfully.", "profile_picture_url": file_location}
    else:
        raise HTTPException(status_code=404, detail="Student not found")
