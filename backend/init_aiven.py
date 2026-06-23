import os
import sys

# Load environment variables (e.g. from .env file at the root)
try:
    from dotenv import load_dotenv
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(root_dir, '.env'))
except ImportError:
    pass

if not os.environ.get("DATABASE_URL"):
    print("Error: DATABASE_URL environment variable is not set.")
    print("Please set it or ensure your .env file is present.")
    sys.exit(1)

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
