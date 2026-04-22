import numpy as np

def calculate_tire_degradation(compound: str, track_temp: float, laps: int):
    """
    Simulates tire degradation based on compound type and track temperature.
    Returns a list of grip percentages per lap.
    """
    # Base rates
    degrad_rates = {
        "SOFT": 0.08,
        "MEDIUM": 0.05,
        "HARD": 0.03
    }
    
    base_rate = degrad_rates.get(compound.upper(), 0.05)
    
    # Temperature multiplier (higher temp = more wear)
    temp_multiplier = 1.0 + (max(0, track_temp - 25) * 0.02)
    
    grip_profile = []
    current_grip = 1.0
    
    for lap in range(laps):
        # Non-linear wear simulation
        wear = base_rate * temp_multiplier * (1 + (lap * 0.01))
        current_grip = max(0.1, current_grip - wear)
        grip_profile.append({"lap": lap + 1, "grip": round(current_grip * 100, 2)})
        
    return grip_profile
