from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship
from .database import Base

class Team(Base):
    __tablename__ = "teams"
    team_id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String(100), nullable=False)
    country = Column(String(100))
    founded_year = Column(Integer)
    
    drivers = relationship("Driver", back_populates="team")
    cars = relationship("Car", back_populates="team")

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="engineer")

class Driver(Base):
    __tablename__ = "drivers"
    driver_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    nationality = Column(String(100))
    dob = Column(Date)
    team_id = Column(Integer, ForeignKey("teams.team_id"))
    
    team = relationship("Team", back_populates="drivers")
    race_results = relationship("RaceResult", back_populates="driver")
    telemetry = relationship("Telemetry", back_populates="driver")
    pit_stops = relationship("PitStop", back_populates="driver")

class Car(Base):
    __tablename__ = "cars"
    car_id = Column(Integer, primary_key=True, index=True)
    model = Column(String(100), nullable=False)
    manufacturer = Column(String(100))
    horsepower = Column(Integer)
    torque = Column(Integer)
    weight = Column(Integer)
    top_speed = Column(Float)
    acceleration = Column(Float)
    team_id = Column(Integer, ForeignKey("teams.team_id"))
    
    team = relationship("Team", back_populates="cars")
    race_results = relationship("RaceResult", back_populates="car")

class Track(Base):
    __tablename__ = "tracks"
    track_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    country = Column(String(100))
    lap_length = Column(Float)
    corners = Column(Integer)
    
    races = relationship("Race", back_populates="track")

class Race(Base):
    __tablename__ = "races"
    race_id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.track_id"))
    season = Column(Integer)
    date = Column(Date)
    laps = Column(Integer)
    
    track = relationship("Track", back_populates="races")
    race_results = relationship("RaceResult", back_populates="race")
    telemetry = relationship("Telemetry", back_populates="race")
    pit_stops = relationship("PitStop", back_populates="race")

class RaceResult(Base):
    __tablename__ = "race_results"
    result_id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.race_id"))
    driver_id = Column(Integer, ForeignKey("drivers.driver_id"))
    car_id = Column(Integer, ForeignKey("cars.car_id"))
    position = Column(Integer)
    points = Column(Integer)
    fastest_lap = Column(String(50))
    
    race = relationship("Race", back_populates="race_results")
    driver = relationship("Driver", back_populates="race_results")
    car = relationship("Car", back_populates="race_results")

class Telemetry(Base):
    __tablename__ = "telemetry"
    telemetry_id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.race_id"))
    driver_id = Column(Integer, ForeignKey("drivers.driver_id"))
    lap_no = Column(Integer)
    speed = Column(Float)
    rpm = Column(Integer)
    throttle = Column(Float)
    brake = Column(Float)
    sector1 = Column(Float)
    sector2 = Column(Float)
    sector3 = Column(Float)
    gear = Column(Integer)
    drs = Column(Integer)
    
    race = relationship("Race", back_populates="telemetry")
    driver = relationship("Driver", back_populates="telemetry")

class Tire(Base):
    __tablename__ = "tires"
    tire_id = Column(Integer, primary_key=True, index=True)
    compound = Column(String(50), nullable=False)
    degradation_rate = Column(Float)
    grip_score = Column(Float)

class PitStop(Base):
    __tablename__ = "pit_stops"
    pit_id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.race_id"))
    driver_id = Column(Integer, ForeignKey("drivers.driver_id"))
    lap = Column(Integer)
    duration = Column(Float)
    tire_id = Column(Integer, ForeignKey("tires.tire_id"))

    race = relationship("Race", back_populates="pit_stops")
    driver = relationship("Driver", back_populates="pit_stops")
    tire = relationship("Tire")

class Alert(Base):
    __tablename__ = "alerts"
    alert_id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    severity = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())
