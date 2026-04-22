import requests
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models
from datetime import datetime

def seed_from_ergast():
    db = SessionLocal()
    print("Connecting to Ergast API...")
    url = "https://api.jolpi.ca/ergast/f1/2023/results.json?limit=1000"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        races_data = data['MRData']['RaceTable']['Races']
        print(f"Found {len(races_data)} races. Seeding started...")

        for r in races_data:
            # 1. Handle Track
            track_name = r['Circuit']['circuitName']
            country = r['Circuit']['Location']['country']
            
            db_track = db.query(models.Track).filter(models.Track.name == track_name).first()
            if not db_track:
                db_track = models.Track(name=track_name, country=country)
                db.add(db_track)
                db.commit()
                db.refresh(db_track)

            # 2. Handle Race
            race_date = datetime.strptime(r['date'], '%Y-%m-%d').date()
            db_race = db.query(models.Race).filter(models.Race.track_id == db_track.track_id, models.Race.date == race_date).first()
            if not db_race:
                db_race = models.Race(
                    track_id=db_track.track_id,
                    season=int(r['season']),
                    date=race_date,
                    laps=0 # Will update if available in results
                )
                db.add(db_race)
                db.commit()
                db.refresh(db_race)

            # 3. Handle Results
            for res in r['Results']:
                # Team
                team_name = res['Constructor']['name']
                db_team = db.query(models.Team).filter(models.Team.team_name == team_name).first()
                if not db_team:
                    db_team = models.Team(team_name=team_name, country=res['Constructor'].get('nationality'))
                    db.add(db_team)
                    db.commit()
                    db.refresh(db_team)

                # Driver
                driver_name = f"{res['Driver']['givenName']} {res['Driver']['familyName']}"
                db_driver = db.query(models.Driver).filter(models.Driver.name == driver_name).first()
                if not db_driver:
                    db_driver = models.Driver(
                        name=driver_name,
                        nationality=res['Driver']['nationality'],
                        dob=datetime.strptime(res['Driver']['dateOfBirth'], '%Y-%m-%d').date(),
                        team_id=db_team.team_id
                    )
                    db.add(db_driver)
                    db.commit()
                    db.refresh(db_driver)
                
                # Update driver's team just in case
                db_driver.team_id = db_team.team_id

                # Race Result
                db_result = db.query(models.RaceResult).filter(
                    models.RaceResult.race_id == db_race.race_id,
                    models.RaceResult.driver_id == db_driver.driver_id
                ).first()
                
                if not db_result:
                    db_result = models.RaceResult(
                        race_id=db_race.race_id,
                        driver_id=db_driver.driver_id,
                        position=int(res['position']),
                        points=int(float(res['points'])),
                        fastest_lap=res.get('FastestLap', {}).get('Time', {}).get('time')
                    )
                    db.add(db_result)

            db.commit()
            print(f"Seeded: {r['raceName']}")

        # ── Seed Cars ────────────────────────────────────────────
        print("\nSeeding car data...")
        car_data = [
            {"model": "RB19",   "manufacturer": "Red Bull",    "team": "Red Bull",            "hp": 1000, "tq": 500, "wt": 798, "ts": 360.0, "acc": 2.4},
            {"model": "W14",    "manufacturer": "Mercedes",    "team": "Mercedes",            "hp": 980,  "tq": 480, "wt": 798, "ts": 355.0, "acc": 2.5},
            {"model": "SF-23",  "manufacturer": "Ferrari",     "team": "Ferrari",             "hp": 990,  "tq": 490, "wt": 798, "ts": 358.0, "acc": 2.5},
            {"model": "MCL60",  "manufacturer": "McLaren",     "team": "McLaren",             "hp": 970,  "tq": 470, "wt": 798, "ts": 352.0, "acc": 2.6},
            {"model": "AMR23",  "manufacturer": "Aston Martin","team": "Aston Martin",        "hp": 975,  "tq": 475, "wt": 798, "ts": 354.0, "acc": 2.5},
            {"model": "A523",   "manufacturer": "Renault",     "team": "Alpine",              "hp": 960,  "tq": 460, "wt": 798, "ts": 348.0, "acc": 2.7},
            {"model": "C43",    "manufacturer": "Alfa Romeo",  "team": "Alfa Romeo",          "hp": 955,  "tq": 455, "wt": 798, "ts": 345.0, "acc": 2.7},
            {"model": "AT04",   "manufacturer": "Alpha Tauri", "team": "AlphaTauri",          "hp": 960,  "tq": 460, "wt": 798, "ts": 347.0, "acc": 2.7},
            {"model": "FW45",   "manufacturer": "Williams",    "team": "Williams",            "hp": 950,  "tq": 450, "wt": 798, "ts": 344.0, "acc": 2.8},
            {"model": "VF-23",  "manufacturer": "Haas",        "team": "Haas",                "hp": 945,  "tq": 445, "wt": 798, "ts": 342.0, "acc": 2.8},
        ]
        for cd in car_data:
            team = db.query(models.Team).filter(models.Team.team_name.like(f"%{cd['team']}%")).first()
            team_id = team.team_id if team else None
            existing = db.query(models.Car).filter(models.Car.model == cd["model"]).first()
            if not existing:
                car = models.Car(
                    model=cd["model"], manufacturer=cd["manufacturer"],
                    horsepower=cd["hp"], torque=cd["tq"], weight=cd["wt"],
                    top_speed=cd["ts"], acceleration=cd["acc"], team_id=team_id,
                )
                db.add(car)
        db.commit()
        print("Car data seeded.")

        # ── Seed Tires ───────────────────────────────────────────
        print("Seeding tire data...")
        tire_data = [
            {"compound": "SOFT",   "degradation_rate": 0.08, "grip_score": 98.0},
            {"compound": "MEDIUM", "degradation_rate": 0.05, "grip_score": 92.0},
            {"compound": "HARD",   "degradation_rate": 0.03, "grip_score": 85.0},
            {"compound": "INTERMEDIATE", "degradation_rate": 0.04, "grip_score": 88.0},
            {"compound": "WET",    "degradation_rate": 0.03, "grip_score": 82.0},
        ]
        for td in tire_data:
            existing = db.query(models.Tire).filter(models.Tire.compound == td["compound"]).first()
            if not existing:
                db.add(models.Tire(**td))
        db.commit()
        print("Tire data seeded.")

        # ── Seed Alerts ──────────────────────────────────────────
        print("Seeding alerts...")
        alert_data = [
            {"message": "Brake temperature exceeding threshold on Car 04 front-left sensor > 980°C.", "severity": "CRITICAL"},
            {"message": "MGU-H efficiency dropped by 3%. Power unit degradation detected.", "severity": "WARNING"},
            {"message": "DRS activation zone recalibrated for current wind conditions.", "severity": "INFO"},
            {"message": "Rear wing flutter detected at 340+ km/h. Structural integrity check required.", "severity": "WARNING"},
            {"message": "Fuel flow rate anomaly on Car 16. FIA limit: 100 kg/h.", "severity": "CRITICAL"},
        ]
        for ad in alert_data:
            existing = db.query(models.Alert).filter(models.Alert.message == ad["message"]).first()
            if not existing:
                db.add(models.Alert(**ad))
        db.commit()
        print("Alert data seeded.")

        print("\n[OK] Full seeding completed successfully!")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_from_ergast()
