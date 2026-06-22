import os
import sys

# Set Aiven Database URL
os.environ["DATABASE_URL"] = "mysql+mysqlconnector://avnadmin:<YOUR_PASSWORD>@pitwall-mysql-pitwall-pro.d.aivencloud.com:14925/defaultdb"

# Import after setting the environment variable
from app.database import engine, Base
import app.models
import app.seed

print("Creating database tables on Aiven...")
try:
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
except Exception as e:
    print(f"Error creating tables: {e}")
    sys.exit(1)

print("\nStarting basic seeding process (Drivers, Teams, Cars, Tracks)...")
try:
    app.seed.seed_from_ergast()
    print("Basic seeding complete!")
except Exception as e:
    print(f"Error during seeding: {e}")

print("\nNote: Telemetry seeding is skipped to save time. Your app is now ready to use!")
