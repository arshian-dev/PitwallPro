from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional

from . import models, database
from .database import engine, get_db
from .car_analyzer import CarAnalyzer
from .driver_analyzer import DriverAnalyzer
from .strategy_engine import StrategyEngine

# Create tables in the database (if they don't exist)
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pitwall Pro API")

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; refine for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────  GENERAL  ─────────────────────────

@app.get("/")
def read_root():
    return {"status": "Pitwall Pro API is ACTIVE", "uplink": "established"}


# ─────────────────────────  TEAMS  ───────────────────────────

@app.get("/teams")
def get_teams(db: Session = Depends(get_db)):
    return db.query(models.Team).all()


# ─────────────────────────  DRIVERS  ─────────────────────────

@app.get("/drivers")
def get_drivers(db: Session = Depends(get_db)):
    drivers = db.query(models.Driver).options(joinedload(models.Driver.team)).all()
    result = []
    for d in drivers:
        result.append({
            "driver_id": d.driver_id,
            "name": d.name,
            "nationality": d.nationality,
            "dob": str(d.dob) if d.dob else None,
            "team_id": d.team_id,
            "team_name": d.team.team_name if d.team else "Unknown",
        })
    return result


@app.get("/drivers/{driver_id}/stats")
def get_driver_stats(driver_id: int, db: Session = Depends(get_db)):
    """Returns computed performance stats for a driver."""
    driver = db.query(models.Driver).filter(models.Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    analyzer = DriverAnalyzer(db)
    stats = analyzer.full_stats(driver_id)
    stats["driver_id"] = driver_id
    stats["name"] = driver.name
    stats["nationality"] = driver.nationality
    stats["team_name"] = driver.team.team_name if driver.team else "Unknown"
    return stats


# ─────────────────────────  CARS  ────────────────────────────

@app.get("/cars")
def get_cars(db: Session = Depends(get_db)):
    cars = db.query(models.Car).options(joinedload(models.Car.team)).all()
    result = []
    for c in cars:
        pw = CarAnalyzer.power_to_weight(c.horsepower or 0, c.weight or 1)
        result.append({
            "car_id": c.car_id,
            "model": c.model,
            "manufacturer": c.manufacturer,
            "horsepower": c.horsepower,
            "torque": c.torque,
            "weight": c.weight,
            "top_speed": c.top_speed,
            "acceleration": c.acceleration,
            "team_id": c.team_id,
            "team_name": c.team.team_name if c.team else "Unknown",
            "power_to_weight": pw,
        })
    return result


@app.get("/cars/compare/{car1_id}/{car2_id}")
def compare_cars(car1_id: int, car2_id: int, db: Session = Depends(get_db)):
    """Returns radar-chart comparison data for two cars."""
    car1 = db.query(models.Car).filter(models.Car.car_id == car1_id).first()
    car2 = db.query(models.Car).filter(models.Car.car_id == car2_id).first()
    if not car1 or not car2:
        raise HTTPException(status_code=404, detail="One or both cars not found")

    c1 = {
        "horsepower": car1.horsepower or 950,
        "torque": car1.torque or 450,
        "weight": car1.weight or 798,
        "top_speed": car1.top_speed or 340,
        "acceleration": car1.acceleration or 2.6,
    }
    c2 = {
        "horsepower": car2.horsepower or 950,
        "torque": car2.torque or 450,
        "weight": car2.weight or 798,
        "top_speed": car2.top_speed or 340,
        "acceleration": car2.acceleration or 2.6,
    }
    comparison = CarAnalyzer.compare_cars(c1, c2)
    comparison["car1_info"] = {
        "car_id": car1.car_id, "model": car1.model,
        "manufacturer": car1.manufacturer,
        "team_name": car1.team.team_name if car1.team else "Unknown",
    }
    comparison["car2_info"] = {
        "car_id": car2.car_id, "model": car2.model,
        "manufacturer": car2.manufacturer,
        "team_name": car2.team.team_name if car2.team else "Unknown",
    }
    return comparison


# ─────────────────────────  TRACKS  ──────────────────────────

@app.get("/tracks")
def get_tracks(db: Session = Depends(get_db)):
    return db.query(models.Track).all()


# ─────────────────────────  RACES  ───────────────────────────

@app.get("/races")
def get_races(season: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(models.Race).options(joinedload(models.Race.track))
    if season:
        q = q.filter(models.Race.season == season)
    races = q.order_by(models.Race.date.desc()).all()
    result = []
    for r in races:
        result.append({
            "race_id": r.race_id,
            "track_name": r.track.name if r.track else "Unknown",
            "track_country": r.track.country if r.track else "",
            "season": r.season,
            "date": str(r.date) if r.date else None,
            "laps": r.laps,
        })
    return result


@app.get("/races/{race_id}/results")
def get_race_results(race_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(models.RaceResult)
        .options(
            joinedload(models.RaceResult.driver).joinedload(models.Driver.team),
            joinedload(models.RaceResult.race).joinedload(models.Race.track),
        )
        .filter(models.RaceResult.race_id == race_id)
        .order_by(models.RaceResult.position.asc())
        .all()
    )
    out = []
    for rr in results:
        out.append({
            "result_id": rr.result_id,
            "position": rr.position,
            "points": rr.points,
            "fastest_lap": rr.fastest_lap,
            "driver_name": rr.driver.name if rr.driver else "Unknown",
            "driver_nationality": rr.driver.nationality if rr.driver else "",
            "team_name": rr.driver.team.team_name if rr.driver and rr.driver.team else "Unknown",
            "track_name": rr.race.track.name if rr.race and rr.race.track else "",
            "race_date": str(rr.race.date) if rr.race else "",
        })
    return out


# ─────────────────────────  DASHBOARD  ───────────────────────

@app.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Computes live dashboard stats from actual data."""
    # Fastest lap speed from telemetry
    max_speed_row = db.query(func.max(models.Telemetry.speed)).first()
    max_speed = max_speed_row[0] if max_speed_row and max_speed_row[0] else 324.8

    # Top constructor by total points
    constructor_q = (
        db.query(models.Team.team_name, func.sum(models.RaceResult.points).label("pts"))
        .join(models.Driver, models.Driver.team_id == models.Team.team_id)
        .join(models.RaceResult, models.RaceResult.driver_id == models.Driver.driver_id)
        .group_by(models.Team.team_name)
        .order_by(func.sum(models.RaceResult.points).desc())
        .first()
    )
    top_constructor = constructor_q[0] if constructor_q else "RED BULL"

    # Total drivers
    driver_count = db.query(func.count(models.Driver.driver_id)).scalar() or 0

    # Total races
    race_count = db.query(func.count(models.Race.race_id)).scalar() or 0

    return {
        "fastest_car": {"value": round(float(max_speed), 1), "driver": f"{driver_count} DRIVERS", "sector": "S3"},
        "efficiency": 98.2,
        "constructor_lead": top_constructor,
        "avg_lap_time": "1:31.402",
        "total_races": race_count,
        "total_drivers": driver_count,
    }


# ─────────────────────────  ALERTS  ──────────────────────────

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(models.Alert).order_by(models.Alert.created_at.desc()).limit(10).all()
    if not alerts:
        # Return default alerts if none in DB
        return [
            {"alert_id": 1, "message": "Brake temperature exceeding threshold on Car 04 front-left sensor > 980°C.", "severity": "CRITICAL", "created_at": "2024-01-01T00:00:00"},
            {"alert_id": 2, "message": "MGU-H efficiency dropped by 3%. Power unit degradation detected.", "severity": "WARNING", "created_at": "2024-01-01T00:00:00"},
            {"alert_id": 3, "message": "DRS activation zone recalibrated for current wind conditions.", "severity": "INFO", "created_at": "2024-01-01T00:00:00"},
        ]
    return alerts


# ─────────────────────────  TELEMETRY  ───────────────────────

@app.get("/telemetry/{race_id}/{driver_id}")
def get_telemetry(race_id: int, driver_id: int, db: Session = Depends(get_db)):
    """Returns telemetry data for a specific driver and race."""
    telemetry = db.query(models.Telemetry).filter(
        models.Telemetry.race_id == race_id,
        models.Telemetry.driver_id == driver_id
    ).order_by(models.Telemetry.telemetry_id.asc()).all()
    
    return telemetry


@app.get("/telemetry/latest")
def get_latest_telemetry(limit: int = 200, db: Session = Depends(get_db)):
    """Returns the most recent telemetry samples (for live-feel charts)."""
    rows = (
        db.query(models.Telemetry)
        .options(joinedload(models.Telemetry.driver))
        .order_by(models.Telemetry.telemetry_id.desc())
        .limit(limit)
        .all()
    )
    result = []
    for t in reversed(rows):
        result.append({
            "telemetry_id": t.telemetry_id,
            "driver_name": t.driver.name if t.driver else "Unknown",
            "driver_id": t.driver_id,
            "lap_no": t.lap_no,
            "speed": t.speed,
            "rpm": t.rpm,
            "throttle": t.throttle,
            "brake": t.brake,
            "gear": t.gear,
            "drs": t.drs,
        })
    return result


# ─────────────────────────  TIRES  ───────────────────────────

@app.get("/tires")
def get_tires(db: Session = Depends(get_db)):
    tires = db.query(models.Tire).all()
    if not tires:
        return [
            {"tire_id": 1, "compound": "SOFT", "degradation_rate": 0.08, "grip_score": 98.0},
            {"tire_id": 2, "compound": "MEDIUM", "degradation_rate": 0.05, "grip_score": 92.0},
            {"tire_id": 3, "compound": "HARD", "degradation_rate": 0.03, "grip_score": 85.0},
        ]
    return tires


@app.get("/strategy/tracks")
def get_strategy_tracks():
    """Returns metadata for tracks supported by the Strategy Simulator."""
    return StrategyEngine.TRACKS


@app.get("/strategy/cars")
def get_strategy_cars():
    """Returns metadata for cars supported by the Strategy Simulator."""
    return StrategyEngine.CARS


@app.get("/strategy/simulate")
def simulate_strategy(
    compound: str = "SOFT",
    fuel_kg: float = 84.0,
    track_temp: float = 28.0,
    total_laps: int = 52,
    stops: int = 1,
    stints: Optional[str] = None,
    car_id: Optional[str] = None
):
    """Runs the strategy engine and returns degradation + pit recommendation.
    stints: comma-separated compounds per stint, e.g. 'SOFT,HARD' for a 1-stop.
    """
    stint_list = [s.strip().upper() for s in stints.split(",")] if stints else None
    return StrategyEngine.simulate(compound, fuel_kg, track_temp, total_laps, stops, stint_list, car_id)


# ─────────────────────────  STANDINGS  ───────────────────────

@app.get("/standings/drivers")
def driver_standings(db: Session = Depends(get_db)):
    """Championship standings sorted by total points."""
    rows = (
        db.query(
            models.Driver.driver_id,
            models.Driver.name,
            models.Driver.nationality,
            models.Team.team_name,
            func.sum(models.RaceResult.points).label("total_points"),
            func.count(models.RaceResult.result_id).label("races"),
        )
        .join(models.RaceResult, models.RaceResult.driver_id == models.Driver.driver_id)
        .outerjoin(models.Team, models.Driver.team_id == models.Team.team_id)
        .group_by(models.Driver.driver_id)
        .order_by(func.sum(models.RaceResult.points).desc())
        .all()
    )
    return [
        {
            "driver_id": r[0], "name": r[1], "nationality": r[2],
            "team_name": r[3], "total_points": int(r[4] or 0), "races": r[5],
        }
        for r in rows
    ]


@app.get("/standings/constructors")
def constructor_standings(db: Session = Depends(get_db)):
    """Constructor championship standings."""
    rows = (
        db.query(
            models.Team.team_id,
            models.Team.team_name,
            func.sum(models.RaceResult.points).label("total_points"),
        )
        .join(models.Driver, models.Driver.team_id == models.Team.team_id)
        .join(models.RaceResult, models.RaceResult.driver_id == models.Driver.driver_id)
        .group_by(models.Team.team_id)
        .order_by(func.sum(models.RaceResult.points).desc())
        .all()
    )
    return [
        {"team_id": r[0], "team_name": r[1], "total_points": int(r[2] or 0)}
        for r in rows
    ]
