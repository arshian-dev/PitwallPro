"""
CarAnalyzer — compares car specs and computes derived metrics.
Used by the Car Lab page for radar-chart comparisons.
"""
import numpy as np


class CarAnalyzer:
    @staticmethod
    def power_to_weight(horsepower: int, weight: int) -> float:
        """Returns hp/kg ratio."""
        if weight <= 0:
            return 0.0
        return round(horsepower / weight, 3)

    @staticmethod
    def predict_acceleration(horsepower: int, torque: int, weight: int) -> float:
        """Estimates 0-100 km/h time (seconds) using simplified physics."""
        if weight <= 0 or torque <= 0:
            return 99.0
        # Simplified model: t ≈ (weight * v) / (torque * gear_ratio * efficiency)
        # Using a calibration constant for F1 cars
        t = (weight * 27.78) / (torque * 3.5 * 0.85)
        return round(max(1.5, min(t, 5.0)), 2)

    @staticmethod
    def compare_cars(car1: dict, car2: dict) -> dict:
        """
        Returns a comparison dict with normalised 0-100 scores
        for radar chart display.
        Dimensions: power, torque, weight (inverted), top_speed, acceleration (inverted)
        """
        def _norm(val, lo, hi):
            if hi == lo:
                return 50
            return round(((val - lo) / (hi - lo)) * 100, 1)

        dims = ["horsepower", "torque", "weight", "top_speed", "acceleration"]
        # Reasonable F1 ranges for normalisation
        ranges = {
            "horsepower":   (800, 1100),
            "torque":       (300, 600),
            "weight":       (700, 900),   # lower is better
            "top_speed":    (300, 380),
            "acceleration": (1.5, 3.5),   # lower is better
        }
        invert = {"weight", "acceleration"}

        result = {"car1": {}, "car2": {}}
        for d in dims:
            lo, hi = ranges[d]
            v1 = car1.get(d, (lo + hi) / 2)
            v2 = car2.get(d, (lo + hi) / 2)
            s1 = _norm(v1, lo, hi)
            s2 = _norm(v2, lo, hi)
            if d in invert:
                s1 = 100 - s1
                s2 = 100 - s2
            result["car1"][d] = max(0, min(100, s1))
            result["car2"][d] = max(0, min(100, s2))

        return result
