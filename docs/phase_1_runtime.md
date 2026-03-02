# Phase 5 Runtime Guide (stored in `docs/phase_1_runtime.md`)

This document describes exactly what was implemented for Phase 5 and how you validate it.

## 1. What Was Created

- Notebook created:
  - `notebooks/dashboard.ipynb`
- Documentation updated:
  - `docs/maplibre_anymap.md`
  - `docs/exercises.md`
  - `docs/phase_1_runtime.md`
- Existing notebooks used (from earlier phases):
  - `notebooks/agent_people.ipynb`
  - `notebooks/agent_camera.ipynb`
- Library modules added in `src/simulated_city/`:
  - None
- Configuration changes in `config.yaml`:
  - None in this phase

## 2. How to Run

### Workflow A: Start People Agent

1. Start JupyterLab:
   - `python -m jupyterlab`
2. Open `notebooks/agent_people.ipynb`.
3. Run cells 1-8 in order.
4. Observe output in final cell:
   - `Phase 3 simulation + publishing complete.`

### Workflow B: Start Camera Agent

1. Open `notebooks/agent_camera.ipynb`.
2. Run cells 1-6 in order.
3. Observe output in Cell 6:
   - `Camera agent running. Press Interrupt to stop.`

### Workflow C: Start Dashboard

1. Open `notebooks/dashboard.ipynb`.
2. Run cell 1 (markdown for context), then run code cells 2-6 in order.
3. In Cell 2, observe:
   - `Loaded config. MQTT base topic: simulated-city/stadium`
4. In Cell 3, observe:
   - `Map created with OpenStreetMap.Mapnik basemap.`
5. In Cell 4, observe topic subscriptions:
   - `Subscribing to: simulated-city/stadium/person/state`
   - `Subscribing to: simulated-city/stadium/camera/decision`
   - `Subscribing to: simulated-city/stadium/entry/event`
6. In Cell 6, keep loop running and observe heartbeats:
   - Prefix: `heartbeat -> person_msgs=`
7. Observe map behavior:
   - People markers appear and update color (`white`, `green`, `red`) as messages arrive.

### Workflow D: Optional Topic Monitor

Run in a terminal:

```bash
mosquitto_sub -h broker.mqttdashboard.com -p 1883 -t "simulated-city/stadium/#" -v
```

You should see:
- `simulated-city/stadium/person/state`
- `simulated-city/stadium/camera/decision`
- `simulated-city/stadium/entry/event`

## 3. Expected Output

### Dashboard notebook outputs

- **Cell 2 (imports + config load):**
  - Exact line: `Loaded config. MQTT base topic: simulated-city/stadium`
  - Prefix: `Dashboard center: lat=`

- **Cell 3 (map setup):**
  - Exact line: `Map created with OpenStreetMap.Mapnik basemap.`
  - A map widget appears centered near Brøndby Stadium.

- **Cell 4 (MQTT setup):**
  - Prefix: `Connected to MQTT broker at `
  - Exact lines:
    - `Subscribing to: simulated-city/stadium/person/state`
    - `Subscribing to: simulated-city/stadium/camera/decision`
    - `Subscribing to: simulated-city/stadium/entry/event`

- **Cell 5 (callbacks):**
  - Exact line: `Dashboard subscriptions active.`
  - Repeating status prefix while messages flow:
    - `dashboard status -> people=`

- **Cell 6 (keep-alive loop):**
  - Exact line: `Dashboard running. Press Interrupt to stop.`
  - Repeating heartbeat prefix every ~5s:
    - `heartbeat -> person_msgs=`

### Meaning of different output

- If map appears but no markers update:
  - Dashboard is running but no `person/state` messages are arriving.
- If marker counts increase but colors do not change:
  - Check incoming payload includes `color` field.
- If `inside_count` never changes:
  - Check `entry/event` messages include `event_type` of `entered` or `exited`.

### Success criteria

- Dashboard subscribes to all three topics.
- Marker colors reflect incoming `person/state.color` values.
- `inside_count` changes only from `entry/event` gate events.
- Dashboard remains read-only and does not publish control decisions.

## 4. MQTT Topics

- `simulated-city/stadium/person/state`
  - Publisher: `notebooks/agent_people.ipynb`
  - Subscriber: `notebooks/dashboard.ipynb`
  - Key schema:
    - `person_id`, `timestamp`, `lat`, `lon`, `state`, `color`, `target_entry_id`

- `simulated-city/stadium/camera/decision`
  - Publisher: `notebooks/agent_camera.ipynb`
  - Subscriber: `notebooks/dashboard.ipynb`
  - Key schema:
    - `person_id`, `timestamp`, `allowed`, `reason_code`, `confidence`, `entry_id`

- `simulated-city/stadium/entry/event`
  - Publisher: `notebooks/agent_people.ipynb`
  - Subscriber: `notebooks/dashboard.ipynb`
  - Key schema:
    - `person_id`, `timestamp`, `event_type`, `entry_id`

## 5. Debugging Guidance

### Increase log visibility

- In dashboard Cell 5, temporarily print raw payloads inside `on_message`.
- Keep Cell 6 running to view heartbeat counters.

### Common errors and solutions

- **`ModuleNotFoundError: simulated_city`**
  - Install editable package from repo root:
  - `pip install -e ".[dev,notebooks]"`

- **`ModuleNotFoundError: anymap_ts`**
  - Ensure notebooks extras are installed:
  - `pip install -e ".[notebooks]"`

- **No MQTT messages received**
  - Verify active profile broker settings in `config.yaml`.
  - Confirm people/camera notebooks are running.

- **No occupancy changes**
  - Verify `entry/event` traffic contains `event_type=entered` or `event_type=exited`.

### Verify MQTT flow

Use:

```bash
mosquitto_sub -h broker.mqttdashboard.com -p 1883 -t "simulated-city/stadium/#" -v
```

You should see all three topic families while notebooks are active.

## 6. Verification Commands

```bash
python scripts/verify_setup.py
python scripts/validate_structure.py
python -m pytest
```
