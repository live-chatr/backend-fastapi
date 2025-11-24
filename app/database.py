from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env")

print(f"Database URL: {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    echo=True,  # prints SQL statements
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},  # needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
