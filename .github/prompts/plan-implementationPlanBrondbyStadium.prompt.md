# Implementation Plan

This implementation plan is based on [docs/concepts.md](docs/concepts.md) and follows [.github/copilot-instructions.md](.github/copilot-instructions.md): one notebook per agent, MQTT communication between agents, configuration loaded via `simulated_city.config.load_config()`, and `anymap-ts` for dashboard mapping.

## Phase 1: Minimal Working Example (One Agent, No MQTT)

**Goal:** Build a minimal people-agent simulation that runs locally in one notebook with basic movement and state transitions, without MQTT.

**New Files:**
- `notebooks/agent_people.ipynb` (notebook)
- `docs/exercises.md` (documentation update)

**Implementation Details:**
- Load simulation settings with `simulated_city.config.load_config()`.
- Simulate 50 people moving toward entrances.
- Apply state and color transitions at entry attempt (`white` → `green` or `red`).
- Enforce permanent exit behavior for denied people.
- Keep all logic local in notebook memory (no publish/subscribe yet).

**Dependencies:**
- No new dependencies.

**Verification:**
- Run `python scripts/verify_setup.py`.
- Run `python scripts/validate_structure.py`.
- Run `python -m pytest`.
- Manual: open notebook in JupyterLab, run all cells, confirm movement and transitions work.

**Investigation:**
- Verify that local state fields already match planned MQTT payload fields.
- Confirm the minimal loop is understandable before adding messaging.

## Phase 2: Add Configuration File Parameters

**Goal:** Extend configuration so all simulation and MQTT behavior uses `config.yaml` values instead of hardcoded notebook values.

**New Files:**
- `config.yaml` (config file update)
- `docs/config.md` (documentation update)
- `docs/exercises.md` (documentation update)

**Implementation Details:**
- Add/confirm simulation keys from concepts (timing, routing, gate geometry, decision probabilities).
- Keep MQTT broker settings in profiles and credentials via env variable names.
- Ensure notebook code reads values via config loader only.

**Dependencies:**
- No new dependencies.

**Verification:**
- Run `python scripts/verify_setup.py`.
- Run `python -m pytest`.
- Manual: run notebook from `notebooks/` and confirm config is resolved correctly.

**Investigation:**
- Confirm defaults are realistic and stable for classroom demos.
- Confirm naming consistency between config keys and concepts document.

## Phase 3: Add MQTT Publishing

**Goal:** Add MQTT publishing from the people agent to broadcast state and entry events.

**New Files:**
- `notebooks/agent_people.ipynb` (notebook update)
- `docs/mqtt.md` (documentation update)
- `docs/exercises.md` (documentation update)

**Implementation Details:**
- Connect to broker using `mqtt.connect_mqtt()`.
- Publish with `mqtt.publish_json_checked()`.
- Publish to `simulated-city/stadium/person/state` and `simulated-city/stadium/entry/event`.
- Use QoS `0` and no retained messages.

**Dependencies:**
- No new dependencies (uses existing MQTT stack).

**Verification:**
- Run `python scripts/verify_setup.py`.
- Run `python scripts/validate_structure.py`.
- Run `python -m pytest`.
- Manual: confirm messages are sent at expected intervals and schema fields are present.

**Investigation:**
- Validate publish frequency vs performance.
- Confirm command-free publisher behavior is stable before adding subscriptions.

## Phase 4: Add Second Agent with MQTT Subscription

**Goal:** Add a camera agent that subscribes to people state and publishes allow/deny decisions so agents communicate through MQTT.

**New Files:**
- `notebooks/agent_camera.ipynb` (notebook)
- `docs/mqtt.md` (documentation update)
- `docs/exercises.md` (documentation update)

**Implementation Details:**
- Subscribe camera agent to `simulated-city/stadium/person/state`.
- Publish decisions to `simulated-city/stadium/camera/decision`.
- Apply decision policy with more allowed than denied outcomes.
- Include false positives and false negatives using configured rates.
- Emit fixed `reason_code` taxonomy from concepts.

**Dependencies:**
- No new dependencies.

**Verification:**
- Run `python scripts/verify_setup.py`.
- Run `python scripts/validate_structure.py`.
- Run `python -m pytest`.
- Manual: run both notebooks and confirm end-to-end message flow and realistic decision distribution.

**Investigation:**
- Check whether schema validation helper should be added in `src/simulated_city/` for reuse.
- Confirm topic naming and base topic consistency before dashboard phase.

## Phase 5: Add Dashboard Visualization (anymap-ts)

**Goal:** Build a dashboard notebook that subscribes to agent topics and visualizes live state with `anymap-ts`.

**New Files:**
- `notebooks/dashboard.ipynb` (notebook)
- `docs/maplibre_anymap.md` (documentation update)
- `docs/exercises.md` (documentation update)

**Implementation Details:**
- Subscribe to person state and camera decision topics.
- Render live people markers with color (`white`, `green`, `red`).
- Display occupancy based on gate-crossing/inside-count rule.
- Keep dashboard focused on visualization (no control logic).

**Dependencies:**
- Confirm `anymap-ts[all]` in project extras.
- No folium/plotly/matplotlib additions.

**Verification:**
- Run `python scripts/verify_setup.py`.
- Run `python scripts/validate_structure.py`.
- Run `python -m pytest`.
- Manual: run people + camera + dashboard notebooks and confirm visual state matches incoming messages.

**Investigation:**
- Tune update intervals for smooth map rendering.
- Verify dashboard remains lightweight and readable for beginners.

## Phase 6+: Integration, Reliability, and Documentation Polish

**Goal:** Stabilize the full workflow, validate behavior across notebooks, and finalize documentation for submission.

**New Files:**
- `notebooks/agent_control.ipynb` (notebook, if introduced after dashboard)
- `docs/testing.md` (documentation update)
- `docs/overview.md` (documentation update)
- `README.md` (documentation update)
- `tests/` (targeted test additions if relevant)

**Implementation Details:**
- Add control agent for command publishing and occupancy topic if needed.
- Verify latest-command-wins behavior and TTL/retry handling under QoS `0`.
- Validate nearest-entry routing, gate-crossing tolerance, and permanent-exit rule.
- Keep notebook responsibilities separate and avoid monolithic designs.

**Dependencies:**
- No new dependencies unless a strict gap is discovered.

**Verification:**
- Run `python scripts/verify_setup.py`.
- Run `python scripts/validate_structure.py`.
- Run `python -m pytest`.
- Manual: full multi-notebook run in JupyterLab with broker active.

**Investigation:**
- Identify repeated logic that should move into reusable helpers in `src/simulated_city/`.
- Confirm final docs reflect implemented behavior exactly and include PR requirement `Docs updated: yes/no`.
