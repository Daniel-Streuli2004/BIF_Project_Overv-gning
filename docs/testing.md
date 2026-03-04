# Testing Guide

This project uses `pytest` for unit/integration checks and notebook-based manual runtime validation.

## Required verification commands

Run these commands from repository root:

```bash
python scripts/verify_setup.py
python scripts/validate_structure.py
python -m pytest
```

## Test modules

- `tests/test_config.py`
  - Configuration parsing and profile selection.
  - Includes Phase 6 timing and gate-tolerance parsing checks.
- `tests/test_agent_rules.py`
  - Latest-command-wins behavior.
  - Command TTL handling.
  - Retry interval behavior under QoS `0` workflow assumptions.
  - Nearest-entry tie-break behavior.
  - Gate crossing tolerance helper behavior.
  - Permanent-exit helper behavior.
- `tests/test_mqtt_profiles.py`, `tests/test_smoke.py`
  - Broker connectivity/publish checks (network dependent).
- `tests/test_geo.py`, `tests/test_maplibre_live.py`
  - Geospatial and map helper sanity checks.

## Manual runtime validation (Phase 6)

1. Start JupyterLab: `python -m jupyterlab`
2. Run these notebooks in separate tabs:
   - `notebooks/agent_people.ipynb`
   - `notebooks/agent_camera.ipynb`
   - `notebooks/agent_control.ipynb`
   - `notebooks/dashboard.ipynb`
3. Confirm:
   - dashboard receives person updates and decisions
   - control agent prints command publish/retry heartbeat
   - occupancy topic updates are emitted

## Notes

- Keep notebooks split by agent responsibility.
- Do not install packages from notebook cells.
- Add new tests for new reusable helper logic in `src/simulated_city/`.
