from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Using the Aiven database by default
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://avnadmin:<YOUR_PASSWORD>@pitwall-mysql-pitwall-pro.d.aivencloud.com:14925/defaultdb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
