CREATE DATABASE IF NOT EXISTS pitwall_pro;
USE pitwall_pro;

CREATE TABLE teams (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    country VARCHAR(100),
    founded_year INT
);

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'engineer'
);

CREATE TABLE drivers (
    driver_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    nationality VARCHAR(100),
    dob DATE,
    team_id INT,
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

CREATE TABLE cars (
    car_id INT AUTO_INCREMENT PRIMARY KEY,
    model VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(100),
    horsepower INT,
    torque INT,
    weight INT,
    top_speed FLOAT,
    acceleration FLOAT,
    team_id INT,
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

CREATE TABLE tracks (
    track_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100),
    lap_length FLOAT,
    corners INT
);

CREATE TABLE races (
    race_id INT AUTO_INCREMENT PRIMARY KEY,
    track_id INT,
    season INT,
    date DATE,
    laps INT,
    FOREIGN KEY (track_id) REFERENCES tracks(track_id)
);

CREATE TABLE race_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    race_id INT,
    driver_id INT,
    car_id INT,
    position INT,
    points INT,
    fastest_lap VARCHAR(50),
    FOREIGN KEY (race_id) REFERENCES races(race_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id),
    FOREIGN KEY (car_id) REFERENCES cars(car_id)
);

CREATE TABLE telemetry (
    telemetry_id INT AUTO_INCREMENT PRIMARY KEY,
    race_id INT,
    driver_id INT,
    lap_no INT,
    speed FLOAT,
    rpm INT,
    throttle FLOAT,
    brake FLOAT,
    sector1 FLOAT,
    sector2 FLOAT,
    sector3 FLOAT,
    FOREIGN KEY (race_id) REFERENCES races(race_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);

CREATE TABLE tires (
    tire_id INT AUTO_INCREMENT PRIMARY KEY,
    compound VARCHAR(50) NOT NULL,
    degradation_rate FLOAT,
    grip_score FLOAT
);

CREATE TABLE pit_stops (
    pit_id INT AUTO_INCREMENT PRIMARY KEY,
    race_id INT,
    driver_id INT,
    lap INT,
    duration FLOAT,
    tire_id INT,
    FOREIGN KEY (race_id) REFERENCES races(race_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id),
    FOREIGN KEY (tire_id) REFERENCES tires(tire_id)
);

CREATE TABLE alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT NOT NULL,
    severity VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initial Mock Data
INSERT INTO teams (team_name, country, founded_year) VALUES 
('Red Bull Racing', 'Austria', 2005),
('Mercedes-AMG F1', 'Germany', 2010),
('Scuderia Ferrari', 'Italy', 1950);

INSERT INTO drivers (name, nationality, dob, team_id) VALUES 
('Max Verstappen', 'Dutch', '1997-09-30', 1),
('Lewis Hamilton', 'British', '1985-01-07', 2),
('Charles Leclerc', 'Monegasque', '1997-10-16', 3);

INSERT INTO tracks (name, country, lap_length, corners) VALUES 
('Silverstone Circuit', 'UK', 5.891, 18),
('Circuit de Monaco', 'Monaco', 3.337, 19),
('Suzuka International Racing Course', 'Japan', 5.807, 18);
