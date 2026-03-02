# Phase 4 Runtime Guide (stored in `docs/phase_1_runtime.md`)

This document describes exactly what was implemented for Phase 4 and how you validate it.

## 1. What Was Created

- Notebook created:
  - `notebooks/agent_camera.ipynb`
- Documentation updated:
  - `docs/mqtt.md`
  - `docs/exercises.md`
  - `docs/phase_1_runtime.md`
- Existing notebook used (from Phase 3):
  - `notebooks/agent_people.ipynb`
- Library modules added in `src/simulated_city/`:
  - None
- Configuration changes in `config.yaml`:
  - none in this phase

## 2. How to Run

### Workflow A: Start the camera agent

1. Start JupyterLab:
   - `python -m jupyterlab`
2. Open `notebooks/agent_camera.ipynb`.
3. Run cells 1-5 in order.
4. Keep the camera notebook running (Cell 6 loop).

### Workflow B: Start the people agent (publisher)

1. Open `notebooks/agent_people.ipynb`.
2. Run cells 1-8 in order.
3. This sends `person/state` and `entry/event` messages that the camera reacts to.

### Workflow C: Monitor topics from terminal

Run this in another terminal to observe published messages:

```bash
mosquitto_sub -h broker.mqttdashboard.com -p 1883 -t "simulated-city/stadium/#" -v
```

You should see all three topics in real time:
- `simulated-city/stadium/person/state`
- `simulated-city/stadium/entry/event`
- `simulated-city/stadium/camera/decision`

### Workflow D: Run project verification commands

1. `python scripts/verify_setup.py`
2. `python scripts/validate_structure.py`
3. `python -m pytest`

## 3. Expected Output

### Camera notebook outputs

- **Cell 2 (imports + config):**
  - Exact line: `Loaded config. MQTT base topic: simulated-city/stadium`
  - Exact line: `Simulation section present: True`

- **Cell 3 (decision settings):**
  - Exact prefix line: `Decision settings -> allow=`
  - Exact line: `Reason-code taxonomy size: 6`

- **Cell 4 (MQTT connection):**
  - Exact prefix line: `Connected to MQTT broker at `
  - Exact line: `Subscribing to: simulated-city/stadium/person/state`
  - Exact line: `Publishing decisions to: simulated-city/stadium/camera/decision`

- **Cell 5 (callback setup):**
  - Exact line: `Camera callback registered and subscription active.`

- **Cell 6 (run loop):**
  - Exact line: `Camera agent running. Press Interrupt to stop.`
  - Exact prefix line every ~5s: `status decisions=`
  - Decision callback lines as messages arrive:
    - `decision#<n> person=<id> allowed=<True|False> reason=<reason_code> confidence=<value> publish_ok=True`

### Terminal monitor output

Expected topic prefixes:

- `simulated-city/stadium/person/state`
- `simulated-city/stadium/entry/event`
- `simulated-city/stadium/camera/decision`

### If output is different

- If no `camera/decision` messages appear, ensure camera notebook Cell 6 is running.
- If no decisions are printed, ensure people notebook is publishing `person/state`.
- If `publish_ok=False` appears, verify broker connectivity and topic permissions.

### Success criteria

- Camera notebook subscribes to `person/state` successfully.
- Camera notebook publishes `camera/decision` messages with taxonomy reason codes.
- End-to-end flow works between people agent and camera agent.

## 4. MQTT Topics (if applicable)

Phase 4 uses and extends topic flow:

- `simulated-city/stadium/person/state`
  - Publisher: `notebooks/agent_people.ipynb`
  - Subscriber: `notebooks/agent_camera.ipynb`
  - Key schema:
    - `person_id`, `name`, `timestamp`, `lat`, `lon`, `state`, `color`, `speed_mps`, `target_entry_id`

- `simulated-city/stadium/entry/event`
  - Publisher: `notebooks/agent_people.ipynb`
  - Key schema:
    - `person_id`, `timestamp`, `event_type`, `entry_id`

- `simulated-city/stadium/camera/decision`
  - Publisher: `notebooks/agent_camera.ipynb`
  - Key schema:
    - `person_id` (string)
    - `timestamp` (ISO string)
    - `allowed` (boolean)
    - `reason_code` (`allowed_lucky|allowed_clear|denied_unlucky|denied_flagged|camera_false_positive|camera_false_negative`)
    - `confidence` (number)
    - `entry_id` (string)

## 5. Debugging Guidance

### Enable more visibility

- In camera notebook Cell 5, temporarily print incoming payload before decision build.
- In terminal monitor, keep `-v` enabled to include topic names.

### Common errors and solutions

- **`ModuleNotFoundError: simulated_city`**
  - Run commands from repository root with:
  - `PYTHONPATH=src`
  - or install editable package: `pip install -e ".[dev,notebooks]"`

- **MQTT connection timeout/failure**
  - Check broker host/port in `config.yaml` active profile.
  - Test broker with `mosquitto_pub` and `mosquitto_sub`.

- **No messages in monitor**
  - Ensure people notebook simulation cell has been run.
  - Ensure monitor topic is `simulated-city/stadium/#`.

- **No camera decisions**
  - Ensure camera notebook run-loop cell is active.
  - Ensure incoming person state has `state="approaching_entry"`.

- **Publish failures increase**
  - Verify internet/network path to broker.
  - Re-run camera connection cell to reconnect broker client.

### MQTT flow checks

- Use:
  - `mosquitto_sub -h broker.mqttdashboard.com -p 1883 -t "simulated-city/stadium/#" -v`
  - You should see state, event, and camera decision topics while both notebooks run.

## 6. Verification Commands

```bash
python scripts/verify_setup.py
python scripts/validate_structure.py
python -m pytest
```
