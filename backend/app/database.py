from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Using the port 3307 as specified by the user or an environment variable for production
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://root@localhost:3307/pitwall_pro")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
