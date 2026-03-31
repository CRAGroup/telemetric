"""Metrics and KPI calculations.

Provides calculation helpers for fuel efficiency, distance, driver score,
idle time percentage, carbon emissions estimates, maintenance cost per km,
and trip cost calculations.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class FuelPrices:
    price_per_liter: float  # in currency units per liter


class CalculationService:
    @staticmethod
    def fuel_efficiency_km_per_l(distance_km: float, fuel_liters: float) -> Optional[float]:
        if fuel_liters is None or fuel_liters <= 0:
            return None
        if distance_km is None or distance_km < 0:
            return None
        return distance_km / fuel_liters

    @staticmethod
    def cost_per_km(price_per_liter: float, efficiency_km_per_l: Optional[float]) -> Optional[float]:
        if efficiency_km_per_l is None or efficiency_km_per_l <= 0:
            return None
        if price_per_liter is None or price_per_liter < 0:
            return None
        # cost per km = (price per liter) / (km per liter)
        return price_per_liter / efficiency_km_per_l

    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    @staticmethod
    def driver_score(num_harsh_accel: int, num_hard_brake: int, num_speeding: int) -> int:
        # Simple scoring: start from 100, subtract weights
        score = 100
        score -= (num_harsh_accel or 0) * 3
        score -= (num_hard_brake or 0) * 4
        score -= (num_speeding or 0) * 5
        return max(0, min(100, score))

    @staticmethod
    def idle_time_percentage(total_time_s: float, idle_time_s: float) -> Optional[float]:
        if total_time_s is None or total_time_s <= 0:
            return None
        if idle_time_s is None or idle_time_s < 0:
            return None
        pct = (idle_time_s / total_time_s) * 100.0
        return max(0.0, min(100.0, pct))

    @staticmethod
    def carbon_emissions_kg(distance_km: float, fuel_liters: Optional[float] = None, *, kg_co2_per_l: float = 2.31, km_per_l: Optional[float] = None) -> Optional[float]:
        """Estimate CO2 emissions.

        Either provide `fuel_liters` directly or provide `km_per_l` to infer liters.
        Default factor 2.31 kg CO2 per liter (gasoline average).
        """
        if fuel_liters is None:
            if km_per_l is None or km_per_l <= 0:
                return None
            fuel_liters = distance_km / km_per_l
        if fuel_liters < 0:
            return None
        return fuel_liters * kg_co2_per_l

    @staticmethod
    def maintenance_cost_per_km(total_maintenance_cost: float, distance_km: float) -> Optional[float]:
        if distance_km is None or distance_km <= 0:
            return None
        if total_maintenance_cost is None or total_maintenance_cost < 0:
            return None
        return total_maintenance_cost / distance_km

    @staticmethod
    def trip_cost(distance_km: float, price_per_liter: float, km_per_l: Optional[float], other_costs: float = 0.0) -> Optional[float]:
        if distance_km is None or distance_km < 0:
            return None
        if price_per_liter is None or price_per_liter < 0:
            return None
        if km_per_l is None or km_per_l <= 0:
            return None
        fuel_liters = distance_km / km_per_l
        return fuel_liters * price_per_liter + max(0.0, other_costs or 0.0)
