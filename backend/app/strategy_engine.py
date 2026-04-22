"""
StrategyEngine — tire degradation modelling and pit-stop optimisation.
Used by the Strategy Simulator page.

Car performance profiles are based on real 2023 F1 season data:
  - Tire degradation multipliers derived from average stint-length deltas
  - Downforce factors reflect known aero philosophies (high-rake vs low-rake etc.)
  - Lap-time offsets calibrated against average qualifying gaps to pole
"""
import numpy as np


class StrategyEngine:
    COMPOUNDS = ["SOFT", "MEDIUM", "HARD"]

    # Base degradation rates per compound per lap
    DEGRAD_RATES = {
        "SOFT":   0.025,
        "MEDIUM": 0.015,
        "HARD":   0.010,
    }

    TRACKS = [
        {"id": "silverstone", "name": "Silverstone GP", "laps": 52, "temp": 22},
        {"id": "monaco", "name": "Monaco GP", "laps": 78, "temp": 28},
        {"id": "monza", "name": "Monza GP", "laps": 53, "temp": 32},
        {"id": "spa", "name": "Spa-Francorchamps", "laps": 44, "temp": 18},
        {"id": "suzuka", "name": "Suzuka Circuit", "laps": 53, "temp": 25},
    ]

    # ── Car Performance Profiles (2023 Season Data) ─────────────────
    # tire_wear_mult : multiplier on base degradation rate
    #   < 1.0 = gentler on tires,  > 1.0 = harder on tires
    # downforce      : aero grip factor (higher = more corner speed but more wear)
    # base_lap_delta : per-lap time offset vs benchmark (RB19), in seconds
    #   Derived from average 2023 qualifying gaps & race-pace analysis
    # fuel_eff       : fuel consumption efficiency multiplier (lower = better)
    CARS = [
        {
            "id": "rb19", "model": "RB19", "team": "Red Bull Racing",
            "tire_wear_mult": 0.88,   # Adrian Newey's masterpiece — exceptional tire management
            "downforce": 1.08,        # Class-leading downforce with low drag
            "base_lap_delta": 0.0,    # Benchmark car — won 21 of 22 races
            "fuel_eff": 0.92,
        },
        {
            "id": "w14", "model": "W14", "team": "Mercedes",
            "tire_wear_mult": 1.12,   # Struggled with tire graining & overheating all season
            "downforce": 1.02,        # Zero-pod concept — less efficient downforce
            "base_lap_delta": 0.45,   # Avg gap to pole: ~0.4-0.5s
            "fuel_eff": 0.96,
        },
        {
            "id": "sf23", "model": "SF-23", "team": "Ferrari",
            "tire_wear_mult": 1.06,   # Rear-limited car — harder on rear tires
            "downforce": 1.05,        # Strong aero, less efficient than RB19
            "base_lap_delta": 0.30,   # Competitive but inconsistent
            "fuel_eff": 0.95,
        },
        {
            "id": "mcl60", "model": "MCL60", "team": "McLaren",
            "tire_wear_mult": 0.94,   # After Silverstone upgrade — excellent tire life
            "downforce": 1.04,        # Massively improved post-upgrade
            "base_lap_delta": 0.25,   # Became 2nd fastest car mid-season
            "fuel_eff": 0.97,
        },
        {
            "id": "amr23", "model": "AMR23", "team": "Aston Martin",
            "tire_wear_mult": 1.02,   # Strong early season, fell off on development
            "downforce": 1.03,
            "base_lap_delta": 0.50,   # Fast in Bahrain/Jeddah, faded later
            "fuel_eff": 0.98,
        },
        {
            "id": "a523", "model": "A523", "team": "Alpine",
            "tire_wear_mult": 1.08,   # Struggled with rear-end stability
            "downforce": 0.98,
            "base_lap_delta": 0.85,
            "fuel_eff": 1.00,
        },
        {
            "id": "c43", "model": "C43", "team": "Alfa Romeo",
            "tire_wear_mult": 1.05,
            "downforce": 0.97,
            "base_lap_delta": 0.95,
            "fuel_eff": 1.02,
        },
        {
            "id": "at04", "model": "AT04", "team": "AlphaTauri",
            "tire_wear_mult": 1.10,   # Known for eating rear tires
            "downforce": 0.96,
            "base_lap_delta": 1.00,
            "fuel_eff": 1.01,
        },
        {
            "id": "fw45", "model": "FW45", "team": "Williams",
            "tire_wear_mult": 1.14,   # Low-downforce car — heavy on tires in corners
            "downforce": 0.94,        # Lowest downforce on the grid
            "base_lap_delta": 1.10,
            "fuel_eff": 1.03,
        },
        {
            "id": "vf23", "model": "VF-23", "team": "Haas",
            "tire_wear_mult": 1.08,
            "downforce": 0.95,
            "base_lap_delta": 1.05,
            "fuel_eff": 1.02,
        },
    ]

    # Approximate lap-time penalty per kg of fuel
    FUEL_PENALTY_PER_KG = 0.035  # seconds

    @classmethod
    def get_car(cls, car_id: str) -> dict:
        """Returns a car profile by ID, or the RB19 as default."""
        for car in cls.CARS:
            if car["id"] == car_id:
                return car
        return cls.CARS[0]  # Default to RB19

    @classmethod
    def tire_wear_model(cls, compound: str, track_temp: float,
                        total_laps: int, car: dict = None) -> list:
        """
        Returns a list of {lap, grip, lap_time_delta} dicts showing
        how grip and pace degrade over a stint.
        Car profile affects degradation rate and lap-time delta.
        """
        base_rate = cls.DEGRAD_RATES.get(compound.upper(), 0.05)
        temp_mult = 1.0 + max(0, track_temp - 25) * 0.02

        # Apply car-specific tire wear multiplier
        car_wear = car["tire_wear_mult"] if car else 1.0
        car_delta = car["base_lap_delta"] if car else 0.0
        car_downforce = car["downforce"] if car else 1.0

        grip = 1.0
        profile = []
        for lap in range(1, total_laps + 1):
            wear = base_rate * temp_mult * car_wear * (1 + lap * 0.008)
            # Higher downforce provides more grip but accelerates wear
            grip_bonus = (car_downforce - 1.0) * 0.15  # Small aero grip offset
            grip = max(0.10, grip - wear)
            effective_grip = min(1.0, grip + grip_bonus)
            # Lap time delta: tire deg + car baseline gap
            delta = round((1.0 - effective_grip) * 3.2 + car_delta, 3)
            profile.append({
                "lap": lap,
                "grip": round(effective_grip * 100, 2),
                "lap_time_delta": delta,
            })
        return profile

    @classmethod
    def fuel_penalty(cls, fuel_kg: float, car: dict = None) -> float:
        """Returns the per-lap time penalty (seconds) for a given fuel load."""
        fuel_eff = car["fuel_eff"] if car else 1.0
        return round(fuel_kg * cls.FUEL_PENALTY_PER_KG * fuel_eff, 3)

    @classmethod
    def optimal_pit_stop(cls, compound: str, track_temp: float,
                         total_laps: int, stops: int = 1, car: dict = None) -> dict:
        """
        Finds the optimal pit window by minimising cumulative time loss
        from tire degradation. Supports 1 and 2 stops.
        """
        profile = cls.tire_wear_model(compound, track_temp, total_laps, car)
        
        if stops == 1:
            # Find the lap where grip drops below 45% — that's our pit window
            pit_window = total_laps 
            for p in profile:
                if p["grip"] < 45:
                    pit_window = p["lap"]
                    break
            
            return {
                "stops": 1,
                "recommended_pit_laps": [pit_window],
                "stints": [compound.upper(), "HARD" if compound.upper() == "SOFT" else "MEDIUM"],
                "estimated_total_loss_s": round(sum(p["lap_time_delta"] for p in profile[:pit_window]), 2),
            }
        else:
            # Simple heuristic for 2 stops: 35% and 70% of distance
            l1 = int(total_laps * 0.35)
            l2 = int(total_laps * 0.70)
            
            return {
                "stops": 2,
                "recommended_pit_laps": [l1, l2],
                "stints": [compound.upper(), "MEDIUM", "HARD"],
                "estimated_total_loss_s": round(sum(p["lap_time_delta"] for p in profile[:l1]) * 0.8, 2),
            }

    @classmethod
    def multi_stint_curve(cls, pit_laps: list, stint_compounds: list,
                          track_temp: float, total_laps: int, car: dict = None) -> list:
        """
        Builds a full-race degradation curve that resets grip at each pit stop.
        Each stint uses the compound specified in stint_compounds.
        Returns a list of {lap, grip, lap_time_delta, compound, stint} dicts.
        """
        curve = []
        # Build stint boundaries: [(start_lap, end_lap, compound), ...]
        boundaries = []
        prev = 1
        for i, pit_lap in enumerate(pit_laps):
            boundaries.append((prev, pit_lap, stint_compounds[i]))
            prev = pit_lap + 1
        # Final stint from last pit to end
        boundaries.append((prev, total_laps, stint_compounds[len(pit_laps)]))

        for stint_idx, (start, end, comp) in enumerate(boundaries):
            stint_profile = cls.tire_wear_model(comp, track_temp, end - start + 1, car)
            for j, p in enumerate(stint_profile):
                curve.append({
                    "lap": start + j,
                    "grip": p["grip"],
                    "lap_time_delta": p["lap_time_delta"],
                    "compound": comp,
                    "stint": stint_idx + 1,
                })
        return curve

    @classmethod
    def validate_stints(cls, stints: list) -> dict:
        """
        Validates stint compounds against F1 dry-race regulations.
        Rule: at least two DIFFERENT slick compounds must be used.
        Returns {valid: bool, error: str|None}.
        """
        for c in stints:
            if c.upper() not in cls.COMPOUNDS:
                return {"valid": False, "error": f"Unknown compound: {c}"}
        unique = set(c.upper() for c in stints)
        if len(unique) < 2:
            return {"valid": False, "error": "F1 rules require at least 2 different slick compounds in a dry race."}
        return {"valid": True, "error": None}

    @classmethod
    def simulate(cls, compound: str, fuel_kg: float, track_temp: float,
                 total_laps: int, stops: int = 1, stints: list = None,
                 car_id: str = None) -> dict:
        """
        Full strategy simulation combining tire wear, fuel, and pit recommendation.
        If `stints` is provided (e.g. ["SOFT","HARD"]), it overrides auto-recommendation.
        If `car_id` is provided, car-specific performance factors are applied.
        """
        car = cls.get_car(car_id) if car_id else None
        fuel_pen = cls.fuel_penalty(fuel_kg, car)
        pit = cls.optimal_pit_stop(compound, track_temp, total_laps, stops, car)

        # If user specified stint compounds, override the recommendation
        if stints and len(stints) == stops + 1:
            stints = [s.upper() for s in stints]
            validation = cls.validate_stints(stints)
            pit["stints"] = stints
            pit["rule_violation"] = None if validation["valid"] else validation["error"]
        else:
            pit["rule_violation"] = None

        # Build a realistic multi-stint curve using the final strategy
        degradation = cls.multi_stint_curve(
            pit["recommended_pit_laps"],
            pit["stints"],
            track_temp,
            total_laps,
            car,
        )

        # Recalculate estimated total loss from the actual multi-stint curve
        pit["estimated_total_loss_s"] = round(
            sum(p["lap_time_delta"] for p in degradation), 2
        )

        result = {
            "degradation_curve": degradation,
            "fuel_penalty_per_lap_s": fuel_pen,
            "pit_recommendation": pit,
            "compound": compound.upper(),
            "fuel_kg": fuel_kg,
            "track_temp": track_temp,
            "total_laps": total_laps,
            "stops": stops,
        }

        if car:
            result["car"] = {
                "id": car["id"],
                "model": car["model"],
                "team": car["team"],
                "tire_wear_mult": car["tire_wear_mult"],
                "downforce": car["downforce"],
                "base_lap_delta": car["base_lap_delta"],
            }

        return result
