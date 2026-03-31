"""Rule evaluation for alerts and thresholds.

Flexible rule engine supporting:
- Complex conditions (e.g., speed > 100 AND outside_hours)
- Per-vehicle/driver overrides
- Time-based rules and geofence windows
- Compound rules
- Rule templates for common scenarios
- Rule testing/simulation
- Simple versioning

DSL: Python-like safe expressions evaluated against a context dict.
Example condition:
  "speed_kph > threshold_speed and outside_hours"
Where context provides "speed_kph", "threshold_speed", and helper flags.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Any, Dict, List, Optional


@dataclass
class Rule:
    id: str
    name: str
    condition: str  # DSL/Python expression
    severity: str = "medium"
    version: int = 1
    active: bool = True
    window_start: Optional[time] = None
    window_end: Optional[time] = None
    geofence_ids: Optional[List[int]] = None
    overrides: Dict[str, Any] = field(default_factory=dict)  # per-vehicle/driver thresholds


class RuleEngine:
    SAFE_GLOBALS = {"__builtins__": {}}  # prevent access to builtins

    def __init__(self, rules: Optional[List[Rule]] = None) -> None:
        self.rules = {r.id: r for r in (rules or [])}

    def register(self, rule: Rule) -> None:
        self.rules[rule.id] = rule

    def remove(self, rule_id: str) -> None:
        self.rules.pop(rule_id, None)

    def evaluate(self, context: Dict[str, Any], *, vehicle_id: Optional[int] = None, driver_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return list of fired rules with metadata."""
        fired: List[Dict[str, Any]] = []
        now = context.get("now") or datetime.utcnow()
        ctx = dict(context)
        for rule in self.rules.values():
            if not rule.active:
                continue
            if rule.window_start and rule.window_end:
                now_t = now.time()
                if not (rule.window_start <= now_t <= rule.window_end):
                    continue
            # apply overrides
            if vehicle_id is not None:
                for k, v in (rule.overrides.get(f"vehicle:{vehicle_id}") or {}).items():
                    ctx[k] = v
            if driver_id is not None:
                for k, v in (rule.overrides.get(f"driver:{driver_id}") or {}).items():
                    ctx[k] = v
            try:
                result = bool(eval(rule.condition, self.SAFE_GLOBALS, ctx))
            except Exception:
                result = False
            if result:
                fired.append({"rule_id": rule.id, "name": rule.name, "severity": rule.severity, "version": rule.version})
        return fired

    # Templates
    @staticmethod
    def template_speed_outside_hours(threshold_speed: float, work_start: time, work_end: time) -> Rule:
        return Rule(
            id=f"speed_outside_{threshold_speed}",
            name="Speeding outside work hours",
            condition="(speed_kph or 0) > threshold_speed and outside_hours",
            severity="high",
            window_start=None,
            window_end=None,
            overrides={"threshold_speed": threshold_speed, "work_start": work_start, "work_end": work_end},
        )

    # Simulation
    def simulate(self, rule_id: str, samples: List[Dict[str, Any]]) -> List[bool]:
        r = self.rules.get(rule_id)
        if not r:
            return [False for _ in samples]
        results: List[bool] = []
        for s in samples:
            ctx = dict(s)
            # derive outside_hours from work window if provided
            ws = ctx.get("work_start") or r.overrides.get("work_start")
            we = ctx.get("work_end") or r.overrides.get("work_end")
            if ws and we and "outside_hours" not in ctx:
                now = ctx.get("now") or datetime.utcnow()
                ctx["outside_hours"] = not (ws <= now.time() <= we)
            try:
                results.append(bool(eval(r.condition, self.SAFE_GLOBALS, ctx)))
            except Exception:
                results.append(False)
        return results
