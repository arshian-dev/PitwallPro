import sys
import os

# Add the parent directory to sys.path so we can import from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.init_db import initialize_database
from app.seed import seed_from_ergast
from app.seed_telemetry import seed_monaco_telemetry

def run_full_setup():
    print("🚀 Starting PitwallPro Project Initialization...")
    
    print("\n--- 1. Initializing Database Structure ---")
    initialize_database()
    
    print("\n--- 2. Seeding Historical F1 Data (Ergast API) ---")
    seed_from_ergast()
    
    print("\n--- 3. Seeding Telemetry Data (FastF1 API) ---")
    print("Note: This may take a moment to download cache files...")
    seed_monaco_telemetry()
    
    print("\n✅ Project successfully initialized and seeded!")
    print("You can now run 'uvicorn app.main:app --reload' to start the backend.")

if __name__ == "__main__":
    run_full_setup()
