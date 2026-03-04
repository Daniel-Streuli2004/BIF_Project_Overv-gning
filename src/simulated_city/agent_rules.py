from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any


def meters_between(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in meters between two WGS84 points."""

    earth_radius_m = 6_371_000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return earth_radius_m * c


def move_towards(
    lat: float,
    lon: float,
    target_lat: float,
    target_lon: float,
    step_m: float,
) -> tuple[float, float]:
    """Move from one coordinate towards a target by at most ``step_m`` meters."""

    distance_m = meters_between(lat, lon, target_lat, target_lon)
    if distance_m <= 1e-9:
        return lat, lon
    ratio = min(1.0, step_m / distance_m)
    new_lat = lat + (target_lat - lat) * ratio
    new_lon = lon + (target_lon - lon) * ratio
    return new_lat, new_lon


def nearest_point(
    lat: float,
    lon: float,
    points: list[dict[str, Any]],
    id_key: str,
) -> dict[str, Any]:
    """Return nearest point with deterministic tie-breaking by ``id_key``."""

    return min(
        points,
        key=lambda point: (
            meters_between(lat, lon, float(point["lat"]), float(point["lon"])),
            str(point[id_key]),
        ),
    )


def is_permanent_exit(state: str) -> bool:
    """Return True when an agent state means no further routing updates."""

    return state == "exited"


def crosses_gate_with_tolerance(
    prev_lat: float,
    prev_lon: float,
    curr_lat: float,
    curr_lon: float,
    gate_lat1: float,
    gate_lon1: float,
    gate_lat2: float,
    gate_lon2: float,
    tolerance_m: float,
) -> bool:
    """Approximate gate crossing from two track points and a gate segment.

    The check passes when:
    - movement crosses from one side of the gate line to the other, and
    - current position is within ``tolerance_m`` of the gate segment.
    """

    # Local equirectangular projection around gate midpoint.
    ref_lat = (gate_lat1 + gate_lat2) / 2.0
    ref_lon = (gate_lon1 + gate_lon2) / 2.0

    def to_xy(lat: float, lon: float) -> tuple[float, float]:
        dlat = math.radians(lat - ref_lat)
        dlon = math.radians(lon - ref_lon)
        earth_radius_m = 6_371_000.0
        x = earth_radius_m * dlon * math.cos(math.radians(ref_lat))
        y = earth_radius_m * dlat
        return x, y

    p0 = to_xy(prev_lat, prev_lon)
    p1 = to_xy(curr_lat, curr_lon)
    g0 = to_xy(gate_lat1, gate_lon1)
    g1 = to_xy(gate_lat2, gate_lon2)

    gate_dx = g1[0] - g0[0]
    gate_dy = g1[1] - g0[1]
    prev_side = gate_dx * (p0[1] - g0[1]) - gate_dy * (p0[0] - g0[0])
    curr_side = gate_dx * (p1[1] - g0[1]) - gate_dy * (p1[0] - g0[0])

    side_changed = prev_side == 0 or curr_side == 0 or (prev_side * curr_side < 0)
    if not side_changed:
        return False

    seg_dx = g1[0] - g0[0]
    seg_dy = g1[1] - g0[1]
    seg_len2 = seg_dx * seg_dx + seg_dy * seg_dy
    if seg_len2 <= 1e-9:
        return False

    t = ((p1[0] - g0[0]) * seg_dx + (p1[1] - g0[1]) * seg_dy) / seg_len2
    t = max(0.0, min(1.0, t))
    nearest_x = g0[0] + t * seg_dx
    nearest_y = g0[1] + t * seg_dy
    distance_to_gate_m = math.hypot(p1[0] - nearest_x, p1[1] - nearest_y)

    return distance_to_gate_m <= max(0.0, tolerance_m)


@dataclass(frozen=True, slots=True)
class CommandEnvelope:
    """Normalized command envelope used by the control agent."""

    person_id: str
    command: str
    sequence: int
    issued_ts: float
    expires_ts: float


class LatestCommandStore:
    """In-memory latest-command-wins store with TTL checks."""

    def __init__(self):
        self._by_person: dict[str, CommandEnvelope] = {}

    def upsert(self, envelope: CommandEnvelope) -> bool:
        """Store a command if it is newer than what we already have."""

        existing = self._by_person.get(envelope.person_id)
        if existing is None:
            self._by_person[envelope.person_id] = envelope
            return True

        if envelope.sequence > existing.sequence:
            self._by_person[envelope.person_id] = envelope
            return True

        if envelope.sequence == existing.sequence and envelope.issued_ts >= existing.issued_ts:
            self._by_person[envelope.person_id] = envelope
            return True

        return False

    def get_active(self, person_id: str, now_ts: float) -> CommandEnvelope | None:
        """Return active command or None if no command exists / command is expired."""

        cmd = self._by_person.get(person_id)
        if cmd is None:
            return None
        if now_ts > cmd.expires_ts:
            return None
        return cmd


def should_retry(last_attempt_ts: float | None, now_ts: float, retry_interval_s: float) -> bool:
    """Return True when retry interval has elapsed or no attempt exists yet."""

    if last_attempt_ts is None:
        return True
    return (now_ts - last_attempt_ts) >= max(0.0, retry_interval_s)
