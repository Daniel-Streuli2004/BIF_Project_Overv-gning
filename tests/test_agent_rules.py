from simulated_city.agent_rules import (
    CommandEnvelope,
    LatestCommandStore,
    crosses_gate_with_tolerance,
    is_permanent_exit,
    nearest_point,
    should_retry,
)


def test_latest_command_wins_with_sequence() -> None:
    store = LatestCommandStore()

    older = CommandEnvelope(
        person_id="p001",
        command="leave",
        sequence=1,
        issued_ts=100.0,
        expires_ts=120.0,
    )
    newer = CommandEnvelope(
        person_id="p001",
        command="enter",
        sequence=2,
        issued_ts=101.0,
        expires_ts=121.0,
    )

    assert store.upsert(older) is True
    assert store.upsert(newer) is True
    active = store.get_active("p001", now_ts=110.0)

    assert active is not None
    assert active.command == "enter"
    assert active.sequence == 2


def test_latest_command_rejects_older_sequence() -> None:
    store = LatestCommandStore()

    latest = CommandEnvelope(
        person_id="p002",
        command="enter",
        sequence=5,
        issued_ts=100.0,
        expires_ts=120.0,
    )
    stale = CommandEnvelope(
        person_id="p002",
        command="leave",
        sequence=4,
        issued_ts=101.0,
        expires_ts=121.0,
    )

    assert store.upsert(latest) is True
    assert store.upsert(stale) is False
    active = store.get_active("p002", now_ts=110.0)

    assert active is not None
    assert active.command == "enter"
    assert active.sequence == 5


def test_command_ttl_expiry() -> None:
    store = LatestCommandStore()
    cmd = CommandEnvelope(
        person_id="p003",
        command="leave",
        sequence=1,
        issued_ts=10.0,
        expires_ts=12.0,
    )

    store.upsert(cmd)
    assert store.get_active("p003", now_ts=11.5) is not None
    assert store.get_active("p003", now_ts=12.1) is None


def test_should_retry_behavior() -> None:
    assert should_retry(None, now_ts=10.0, retry_interval_s=2.0) is True
    assert should_retry(9.5, now_ts=10.0, retry_interval_s=2.0) is False
    assert should_retry(7.5, now_ts=10.0, retry_interval_s=2.0) is True


def test_nearest_point_tie_breaks_by_id() -> None:
    points = [
        {"entry_id": "E2", "lat": 55.65, "lon": 12.4186},
        {"entry_id": "E1", "lat": 55.65, "lon": 12.4186},
    ]
    nearest = nearest_point(55.65, 12.4186, points, "entry_id")
    assert nearest["entry_id"] == "E1"


def test_gate_crossing_with_tolerance() -> None:
    crossed = crosses_gate_with_tolerance(
        prev_lat=55.6500,
        prev_lon=12.4184,
        curr_lat=55.6500,
        curr_lon=12.41862,
        gate_lat1=55.6499,
        gate_lon1=12.4186,
        gate_lat2=55.6501,
        gate_lon2=12.4186,
        tolerance_m=5.0,
    )
    assert crossed is True


def test_permanent_exit_rule() -> None:
    assert is_permanent_exit("exited") is True
    assert is_permanent_exit("inside") is False
