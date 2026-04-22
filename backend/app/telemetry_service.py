import fastf1
import pandas as pd
from typing import List, Dict, Optional
import os

# Create cache directory if it doesn't exist
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

fastf1.Cache.enable_cache(CACHE_DIR)

class FastF1Service:
    @staticmethod
    def get_session_telemetry(year: int, location: str, session_type: str, driver_code: str) -> List[Dict]:
        """
        Fetches telemetry for a specific driver's fastest lap in a session.
        Returns a list of dicts suitable for the database or API.
        """
        try:
            session = fastf1.get_session(year, location, session_type)
            session.load()
            
            # Find the driver's fastest lap
            laps = session.laps.pick_driver(driver_code)
            fastest_lap = laps.pick_fastest()
            
            if fastest_lap is None:
                return []

            # Get telemetry
            telemetry = fastest_lap.get_telemetry()
            
            # Map FastF1 columns to our schema
            # Speed, RPM, nGear, Throttle, Brake, DRS, Time
            results = []
            for _, row in telemetry.iterrows():
                results.append({
                    "lap_no": int(fastest_lap['LapNumber']),
                    "speed": float(row['Speed']),
                    "rpm": int(row['RPM']),
                    "gear": int(row['nGear']),
                    "throttle": float(row['Throttle']),
                    "brake": float(row['Brake']),
                    "drs": int(row['DRS']),
                    "timestamp": str(row['Time']) # Relative time
                })
            
            return results
        except Exception as e:
            print(f"FastF1 Error: {e}")
            return []

    @staticmethod
    def get_session_info(year: int, location: str, session_type: str):
        """Returns basic session info."""
        session = fastf1.get_session(year, location, session_type)
        session.load(telemetry=False, weather=False)
        return {
            "event_name": session.event['EventName'],
            "session_name": session.name,
            "date": session.date.strftime('%Y-%m-%d')
        }
