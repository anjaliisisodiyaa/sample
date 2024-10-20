
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from sqlalchemy.future import select
from user_sch import SignUser,SignUserResponse, Role
from utilis import hash_password,send_welcome_email
from dependency.get_db import get_db


async def signup(user: SignUser, db: AsyncSession) -> SignUserResponse:
    try:
        # Check if user with the given email already exists
        email_query = select(User).filter(User.email == user.email)
        result = await db.execute(email_query)
        email_db_user = result.scalar_one_or_none()

        if email_db_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
        contact_query = select(User).filter(User.contact_number == user.contact_number)
        contact_result = await db.execute(contact_query)
        contact_user = contact_result.scalar_one_or_none()
        
        if contact_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Contact number is already registered."
            )

        hashed_password = hash_password(user.password)

        user_data = User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=hashed_password,
            contact_number=user.contact_number,
            gender=user.gender,
            role=user.role,
            age=user.age
        )

        db.add(user_data)
        await db.commit()
        await db.refresh(user_data)

        # Send the welcome email
        send_welcome_email(user.email, user.first_name)

        return SignUserResponse(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            contact_number=user_data.contact_number,
            gender=user_data.gender,
            age=user_data.age,
            role=user_data.role
        )
    
    except HTTPException as http_exc:
        raise http_exc
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")

