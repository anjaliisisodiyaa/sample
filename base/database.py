from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()

# Get MySQL database configuration from environment variables
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "sisodiya77anju")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "testsqldb")
MYSQL_PORT = os.getenv("MYSQL_PORT", 3306)


SQLALCHEMY_DATABASE_URL = (
    f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

Base = declarative_base()
try:
    async def get_engine():
      
      return create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
    print("Engine is created")

    async def get_session(engine):
     
      return sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print(True,"Sessionmaker is created")
except Exception as e :
      print("Something went wrong!",e)

# Create the async engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)


# Create the sessionmaker
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)
