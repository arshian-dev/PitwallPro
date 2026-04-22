from .database import SessionLocal
from . import models
from .telemetry_service import FastF1Service
from datetime import datetime

def seed_monaco_telemetry():
    db = SessionLocal()
    print("Starting FastF1 Telemetry Seeding (2024 Monaco Q)...")
    
    # 1. Ensure Track and Race exist for Monaco 2024
    track_name = "Circuit de Monaco"
    db_track = db.query(models.Track).filter(models.Track.name == track_name).first()
    if not db_track:
        db_track = models.Track(name=track_name, country="Monaco")
        db.add(db_track)
        db.commit()
        db.refresh(db_track)

    # Note: Monaco 2024 Qualy was May 25, 2024
    race_date = datetime(2024, 5, 25).date()
    db_race = db.query(models.Race).filter(models.Race.track_id == db_track.track_id, models.Race.date == race_date).first()
    if not db_race:
        db_race = models.Race(
            track_id=db_track.track_id,
            season=2024,
            date=race_date,
            laps=0
        )
        db.add(db_race)
        db.commit()
        db.refresh(db_race)

    # 2. Seed telemetry for Charles Leclerc (LEC) and Max Verstappen (VER)
    drivers_to_seed = ['LEC', 'VER']
    
    for driver_code in drivers_to_seed:
        print(f"Fetching telemetry for {driver_code}...")
        
        # Find or create driver in DB
        # Mapping code to name for demo purposes
        name_map = {'LEC': 'Charles Leclerc', 'VER': 'Max Verstappen'}
        driver_name = name_map.get(driver_code, driver_code)
        
        db_driver = db.query(models.Driver).filter(models.Driver.name == driver_name).first()
        if not db_driver:
            db_driver = models.Driver(name=driver_name, nationality='Unknown')
            db.add(db_driver)
            db.commit()
            db.refresh(db_driver)

        # Get telemetry samples
        telemetry_data = FastF1Service.get_session_telemetry(2024, 'Monaco', 'Q', driver_code)
        
        if not telemetry_data:
            print(f"No telemetry found for {driver_code}")
            continue

        print(f"Inserting {len(telemetry_data)} telemetry samples for {driver_code}...")
        
        # Slice for efficiency (FastF1 is high frequency, we'll take every 10th sample for demo)
        for i, sample in enumerate(telemetry_data):
            if i % 10 != 0: continue
            
            db_telemetry = models.Telemetry(
                race_id=db_race.race_id,
                driver_id=db_driver.driver_id,
                lap_no=sample['lap_no'],
                speed=sample['speed'],
                rpm=sample['rpm'],
                gear=sample['gear'],
                throttle=sample['throttle'],
                brake=sample['brake'],
                drs=sample['drs']
            )
            db.add(db_telemetry)
        
        db.commit()
        print(f"Seeded {driver_code} successfully.")

    print("Telemetry seeding completed!")
    db.close()

if __name__ == "__main__":
    seed_monaco_telemetry()
