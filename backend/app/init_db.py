from sqlalchemy import create_engine, text
from .database import engine, Base
from . import models

def initialize_database():
    # Connect to the MySQL server without specifying a database
    root_url = "mysql+mysqlconnector://root@localhost:3307/"
    root_engine = create_engine(root_url)
    
    with root_engine.connect() as conn:
        print("Checking for database 'pitwall_pro'...")
        conn.execute(text("CREATE DATABASE IF NOT EXISTS pitwall_pro"))
        print("Database 'pitwall_pro' ensured.")
    
    # Now that the DB exists, create tables using SQLAlchemy models
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    print("Initialization complete!")

if __name__ == "__main__":
    initialize_database()
