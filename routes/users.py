from sqlalchemy.ext.asyncio import AsyncSession
from user_sch import UserCreate,CreateUser
# from sqlalchemy.orm import selectinload
from models import User
from fastapi import HTTPException,Depends,status
from sqlalchemy import asc,desc,func
from sqlalchemy.future import select
# import logging
from typing import Optional, List, Dict, Any, Tuple
from user_sch import UserResponseId
# import bcrypt
# from fastapi.security import HTTPBasicCredentials



async def create_user(db: AsyncSession, user: UserCreate):

    # logger.info("Create user got called")
    try:
        new_user = User(
            username=user.username,
            email=user.email,
            password=user.password
        )
        # logging.info(user)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return {"status": "ok", "message": "Server is running", "user": new_user}
        # return db_user

    except Exception as e:
        raise

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 10):
    try:
        result = await db.execute(select(User).offset(skip).limit(limit))
        users = result.scalars().all()
        return users
    except Exception as e:
        raise
    
async def get_user(db: AsyncSession, user_id: int):
    try: 
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return user
    except Exception as e:
        raise

async def update_user(db:AsyncSession, user_id:int, user = CreateUser) -> User:
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        db_user = result.scalar_one_or_none()
        if db_user:
            # Update the fields if provided
            if user.username is not None:
                db_user.username = user.username
            if user.email is not None:
                db_user.email = user.email


            await db.commit()
            await db.refresh(db_user)
            return db_user
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_user(db: AsyncSession, user_id: int) -> Optional[dict]:
    try:
        # Fetch the user to be deleted
        result = await db.execute(select(User).where(User.id == user_id))
        db_user = result.scalar_one_or_none()

        if db_user:
            # Delete the user
            await db.delete(db_user)
            await db.commit()
            return {"message": "User deleted successfully"}
        else:
            # If user is not found, raise an HTTPException
            raise HTTPException(status_code=404, detail="User not found")

    except Exception as e:
        # Handle exceptions and raise HTTPException with an appropriate error message
        raise HTTPException(status_code=500, detail=str(e))
        
async def patch_user(db: AsyncSession, user_id: int, user_update: CreateUser) -> Optional[dict]:
    try:
        # Fetch the user to be updated
        result = await db.execute(select(User).where(User.id == user_id))
        db_user = result.scalar_one_or_none()

        if db_user:
            # Update the fields if provided
            if user_update.username is not None:
                db_user.username = user_update.username
            if user_update.email is not None:
                db_user.email = user_update.email


            # Commit the transaction
            await db.commit()
            await db.refresh(db_user)
            return {"message": "User updated successfully", "user": {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email,

            }}
        else:
            # If the user is not found, raise an HTTPException
            raise HTTPException(status_code=404, detail="User not found")

    except Exception as e:
        # Handle exceptions and raise HTTPException with an appropriate error message
        raise HTTPException(status_code=500, detail=str(e))        

async def search_user(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    search_key: Optional[str] = None,
    # username_contains: Optional[str] = None,
    # email_contains: Optional[str] = None,
    sort_by: Optional[str] = 'username',
    sort_order: Optional[str] = 'asc'
) -> Tuple[List[Dict[str, Any]], int]:

    try:
        # Base query with filter and count
        base_query = select(User)

        if search_key:
            base_query = base_query.where(
                User.username.ilike(f'%{search_key}%') |
                User.email.ilike(f'%{search_key}%')
            )
        # else:
        #     if username_contains:
        #         base_query = base_query.where(User.username.ilike(f'%{username_contains}%'))
            
        #     if :
        #         base_query = base_query.where(User.email.ilike(f'%{email_contains}%'))

        # Count query
        count_query = select(func.count().label('total_count')).select_from(User)
        if search_key:
            count_query = count_query.where(
                User.username.ilike(f'%{search_key}%') |
                User.email.ilike(f'%{search_key}%')
            )
        # else:
        #     if username_contains:
        #         count_query = count_query.where(User.username.ilike(f'%{username_contains}%'))
            
        #     if email_contains:
        #         count_query = count_query.where(User.email.ilike(f'%{email_contains}%'))

        count_result = await db.execute(count_query)
        total_users = count_result.scalar()

        # Paginated results query
        paginated_query = base_query.offset(skip).limit(limit)
        
        # Apply sorting
        if sort_by:
            if sort_by == 'username':
                paginated_query = paginated_query.order_by(asc(User.username) if sort_order == 'asc' else desc(User.username))
            elif sort_by == 'email':
                paginated_query = paginated_query.order_by(asc(User.email) if sort_order == 'asc' else desc(User.email))
        
        result = await db.execute(paginated_query)
        users = result.scalars().all()
        
        # Convert results to a list of dictionaries
        users_list = [user.__dict__ for user in users]

        return users_list, total_users

    except Exception as e:
        print(f"Exception occurred: {e}")
        raise

async def user_id(
        db :AsyncSession ,
        skip: int = 0,
        limit: int = 10,
        # sort_by: Optional[str] = 'username',
        # sort_order: Optional[str] = 'asc',
        id_constraint: Optional[int]=None
        )->List[int]:
        query = select(User.id)
        if id_constraint is not None:
            query = query.where(User.id == id_constraint)
    
        result = await db.execute(query)
        users_ids = result.scalars().all()  # This should be a list of integers
    
        return users_ids

from user_sch import SignUserResponse
# ====================================================================

async def user_id_details( db: AsyncSession, id_constraint: int) ->SignUserResponse:
    
    query = select(User).where(User.id == id_constraint)
  
    result = await db.execute(query)
    users = result.scalars().first()
    print("All the ")
    print(users)
    print(type(users))
    dict_data = {
        'id':users.id,
        'gender':users.gender,
        'email':users.email

    }
    print(dict_data)

    return UserResponseId(**dict_data)


# ===============================================================
# =================================================================
# def hash_password(password: str) -> TokenData:
#     # Generate a salt and hash the password
#     return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# async def login_request(db: AsyncSession, username: str, password: str) -> dict:
#     # Retrieve the user by username
#     query = select(User).where(User.username == username,User.password==password)
#     result = await db.execute(query)
#     user = result.scalar_one_or_none()

#     # Check if the user exists and verify the password
#     if user is None:
#         raise HTTPException(status_code=401, detail="Incorrect username or password")
#     try:
#         # Verify the password
#         if not verify_password(password, user.password):
#             # Password does not match
#             raise HTTPException(status_code=401, detail="Incorrect username or password")
#     except ValueError as e:
#         # Handle invalid salt or hash errors
#         raise HTTPException(status_code=500, detail="Internal server error: Invalid password format")


#     # Return success message
#     return {"Verification": "You are verified and logged in successfully"}    
    # ==========================================
    # user_details = []
    # data_to_append = UserResponseId(
    #         id=users.id,
    #         name=users.username,
    #         email=users.email,
    #         password=users.password
    #     )
    # print(data_to_append)
    # print(type(data_to_append))
    # user_details.append(data_to_append)
    # return user_details
    # =================================
    # for user in users:
    #     print("All the user")
    #     print(type(user))
    #     print(user)
    #     data_to_append = UserResponseId(
    #             id=user.id,
    #             name=user.username,
    #             email=user.email,
    #             password=user.password
    #         )
    #     print(data_to_append)
    #     print(type(data_to_append))
    #     user_details.append(data_to_append)
    

    # Convert SQLAlchemy models to Pydantic models
    # return user_details
    # =============================================
# from jose import JWTError
# import jwt

# SECRET_KEY = "mahadevharhar47"
# ALGORITHM = "HS256"


# def hash_password(password: str) -> str:
#     return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# def create_token(data:dict):
#     to_encode = data.copy()
#     encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
#     return encoded_jwt

# async def login_token(db:AsyncSession,username:str, password:str)-> dict:
#     result = await db.execute(select(User).filter(User.username == username))
#     user = result.scalar_one_or_none()

#     if user is None or not verify_password(password, user.password):
#         raise HTTPException(
#                 status_code=401,
#                 detail="Incorrect username or password",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#     access_token = create_token(data={"username": user.username,"password":user.password})
    # return {"access_token": access_token, "token_type": "bearer"}

# ======================================================================

# async def get_user_by_username(db: AsyncSession, username: str) -> Optional[TokenData]:
#     query = select(User).filter(User.username == username)
#     result = await db.execute(query)
#     return result.scalars().first()


# async def authenticate_user(db: AsyncSession, credentials: HTTPBasicCredentials) -> TokenData:
#     user = await get_user_by_username(db, credentials.username)
#     if user is None or not verify_password(credentials.password, user.password):
#         print(f"Failed login attempt for {credentials.username}")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Basic"},
#         )
    
#     return TokenData(username=user.username)
# ============================================================================



# async def search_user(
#     db: AsyncSession,
#     skip: int = 0,
#     limit: int = 10,
#     search_key: Optional[str] = None,
#     # username_contains: Optional[str] = None,
#     # email_contains: Optional[str] = None,
#     sort_by: Optional[str] = 'first_name',
#     sort_order: Optional[str] = 'asc'
# ) -> Tuple[List[Dict[str, Any]], int]:

#     try:
#         # Base query with filter and count
#         base_query = select(User)

#         if search_key:
#             base_query = base_query.where(
#                 User.first_name.ilike(f'%{search_key}%') |
#                 User.email.ilike(f'%{search_key}%')
#             )
#         # else:
#         #     if username_contains:
#         #         base_query = base_query.where(User.username.ilike(f'%{username_contains}%'))
            
#         #     if :
#         #         base_query = base_query.where(User.email.ilike(f'%{email_contains}%'))

#         # Count query
#         count_query = select(func.count().label('total_count')).select_from(User)
#         if search_key:
#             count_query = count_query.where(
#                 User.first_name.ilike(f'%{search_key}%') |
#                 User.email.ilike(f'%{search_key}%')
#             )
#         # else:
#         #     if username_contains:
#         #         count_query = count_query.where(User.username.ilike(f'%{username_contains}%'))
            
#         #     if email_contains:
#         #         count_query = count_query.where(User.email.ilike(f'%{email_contains}%'))

#         count_result = await db.execute(count_query)
#         total_users = count_result.scalar()

#         # Paginated results query
#         paginated_query = base_query.offset(skip).limit(limit)
        
#         # Apply sorting
#         if sort_by:
#             if sort_by == 'username':
#                 paginated_query = paginated_query.order_by(asc(User.username) if sort_order == 'asc' else desc(User.username))
#             elif sort_by == 'email':
#                 paginated_query = paginated_query.order_by(asc(User.email) if sort_order == 'asc' else desc(User.email))
        
#         result = await db.execute(paginated_query)
#         users = result.scalars().all()
        
#         # Convert results to a list of dictionaries
#         users_list = [user.__dict__ for user in users]

#         return users_list, total_users

#     except Exception as e:
#         print(f"Exception occurred: {e}")
#         raise
# -----------------------------------------------------------------------

async def search_user(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    search_key: Optional[str] = None,
    sort_by: Optional[str] = 'first_name',
    sort_order: Optional[str] = 'asc'
) -> Tuple[List[Dict[str, Any]], int]:

    try:
        # Base query with optional search across multiple fields
        base_query = select(User)

        if search_key:
            search_pattern = f"%{search_key}%"
            base_query = base_query.where(
                User.first_name.ilike(search_pattern) |
                User.last_name.ilike(search_pattern) |
                User.email.ilike(search_pattern) |
                User.contact_number.ilike(search_pattern)
            )

        # Count query to get the total number of results
        count_query = select(func.count().label('total_count')).select_from(User)

        if search_key:
            count_query = count_query.where(
                User.first_name.ilike(search_pattern) |
                User.last_name.ilike(search_pattern) |
                User.email.ilike(search_pattern) |
                User.contact_number.ilike(search_pattern)
            )

        count_result = await db.execute(count_query)
        total_users = count_result.scalar()

        # Sorting logic based on sort_by and sort_order
        if sort_by == 'email':
            sort_column = User.email
        elif sort_by == 'age':
            sort_column = User.age
        else:
            sort_column = User.first_name  # Default sort by first_name

        sort_order_func = asc if sort_order == 'asc' else desc
        base_query = base_query.order_by(sort_order_func(sort_column))

        # Paginate query
        paginated_query = base_query.offset(skip).limit(limit)
        result = await db.execute(paginated_query)
        users = result.scalars().all()

        # Convert results to a list of dictionaries
        users_list = [
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "contact_number": user.contact_number,
                "status": user.status,
                "is_email_verified": user.is_email_verified,
                "gender": user.gender.name,  # Enum handling
                "age": user.age
            }
            for user in users
        ]

        return users_list, total_users

    except Exception as e:
        print(f"Exception occurred: {e}")
        raise