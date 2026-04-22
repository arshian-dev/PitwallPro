"""
DriverAnalyzer — computes performance metrics from race results.
Used by the Drivers page for stats cards.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models


class DriverAnalyzer:
    def __init__(self, db: Session):
        self.db = db

    def avg_finish(self, driver_id: int) -> float:
        """Average finishing position across all results."""
        result = (
            self.db.query(func.avg(models.RaceResult.position))
            .filter(models.RaceResult.driver_id == driver_id)
            .scalar()
        )
        return round(float(result), 1) if result else 0.0

    def consistency_score(self, driver_id: int) -> float:
        """
        Consistency = 100 - stddev(position).
        A lower spread in finishing positions = higher consistency.
        """
        positions = (
            self.db.query(models.RaceResult.position)
            .filter(models.RaceResult.driver_id == driver_id)
            .all()
        )
        if len(positions) < 2:
            return 100.0
        import numpy as np
        vals = [p[0] for p in positions if p[0] is not None]
        if not vals:
            return 0.0
        std = float(np.std(vals))
        return round(max(0, 100 - (std * 10)), 1)

    def podium_rate(self, driver_id: int) -> float:
        """Percentage of races finished in P1-P3."""
        total = (
            self.db.query(func.count(models.RaceResult.result_id))
            .filter(models.RaceResult.driver_id == driver_id)
            .scalar()
        )
        podiums = (
            self.db.query(func.count(models.RaceResult.result_id))
            .filter(
                models.RaceResult.driver_id == driver_id,
                models.RaceResult.position <= 3,
            )
            .scalar()
        )
        if not total:
            return 0.0
        return round((podiums / total) * 100, 1)

    def wins(self, driver_id: int) -> int:
        """Total P1 finishes."""
        return (
            self.db.query(func.count(models.RaceResult.result_id))
            .filter(
                models.RaceResult.driver_id == driver_id,
                models.RaceResult.position == 1,
            )
            .scalar()
        ) or 0

    def podiums(self, driver_id: int) -> int:
        """Total P1-P3 finishes."""
        return (
            self.db.query(func.count(models.RaceResult.result_id))
            .filter(
                models.RaceResult.driver_id == driver_id,
                models.RaceResult.position <= 3,
            )
            .scalar()
        ) or 0

    def total_points(self, driver_id: int) -> int:
        """Sum of championship points."""
        result = (
            self.db.query(func.sum(models.RaceResult.points))
            .filter(models.RaceResult.driver_id == driver_id)
            .scalar()
        )
        return int(result) if result else 0

    def position_history(self, driver_id: int) -> list:
        """List of finishing positions in chronological order (for sparkline)."""
        rows = (
            self.db.query(models.RaceResult.position, models.Race.date)
            .join(models.Race, models.RaceResult.race_id == models.Race.race_id)
            .filter(models.RaceResult.driver_id == driver_id)
            .order_by(models.Race.date.asc())
            .all()
        )
        return [r[0] for r in rows if r[0] is not None]

    def full_stats(self, driver_id: int) -> dict:
        """Aggregate all stats into a single dict for the frontend."""
        return {
            "avg_finish": self.avg_finish(driver_id),
            "consistency": self.consistency_score(driver_id),
            "podium_rate": self.podium_rate(driver_id),
            "wins": self.wins(driver_id),
            "podiums": self.podiums(driver_id),
            "total_points": self.total_points(driver_id),
            "position_history": self.position_history(driver_id),
        }
