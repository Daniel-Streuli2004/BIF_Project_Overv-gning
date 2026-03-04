# Brøndby Stadium Simulation Architecture (Pre-Code)

## 1. System Overview

### Trigger (Movement Generator)
- Simulate 50 person agents moving around Brøndby Stadium.
- All persons start with neutral status and white color.
- Each person is assigned a movement target from a list of stadium entrances.
- Persons remain white while approaching entrances and only change status at entry attempt.

### Observer (Perception Layer)
- A camera-sensor agent observes persons when they reach an entry zone.
- The observer evaluates each entry attempt and produces a normalized decision.
- Decision output contains an `allowed` boolean and a `reason_code` from a fixed taxonomy: `allowed_lucky`, `allowed_clear`, `denied_unlucky`, `denied_flagged`, `camera_false_positive`, `camera_false_negative`.
- Decision policy is random probability with more allowed outcomes than disallowed outcomes.
- Ground truth status at entry attempt is modeled as `lucky` or `unlucky` by random draw before camera error is applied.
- Camera decisions include realistic false positives and false negatives.

### Control Center (Decision Layer)
- A control agent consumes camera decisions and current person states.
- The control agent publishes movement directives per person:
	- continue toward entry
	- enter stadium
	- move away from stadium

### Response (Actuation + Outcome)
- Person agents apply directives and update position/state on each simulation tick.
- If a person is allowed, color changes to green and state changes to inside.
- If a person is denied, color changes to red and state changes to exiting.
- Denied persons exit permanently and do not re-attempt entry.
- A dashboard displays live person locations, colors, and stadium occupancy.
- Occupancy count includes only allowed persons who crossed the gate line.

## 2. MQTT Architecture

Base namespace: `simulated-city/stadium`

QoS policy: QoS `0` for all topics and no retained messages.

QoS `0` command handling policy: commands are best-effort, re-published every `command_retry_interval_s` while valid, and expire at `command_ttl_s`; if a command is dropped, person agents continue their last valid command until a newer valid command arrives or TTL expires.

### Topic: `simulated-city/stadium/person/state`
- **Publishes:** `agent_people`
- **Subscribes:** `agent_camera`, `agent_control`, `dashboard`
- **Message schema (JSON):**
	- `person_id` (string)
	- `name` (string)
	- `timestamp` (string, ISO 8601)
	- `lat` (number)
	- `lon` (number)
	- `state` (string: `approaching_entry|inside|exiting`)
	- `color` (string: `white|green|red`)
	- `speed_kmh` (number)
	- `target_entry_id` (string)

### Topic: `simulated-city/stadium/camera/decision`
- **Publishes:** `agent_camera`
- **Subscribes:** `agent_control`, `dashboard`
- **Message schema (JSON):**
	- `person_id` (string)
	- `timestamp` (string, ISO 8601)
	- `allowed` (boolean)
	- `reason_code` (string: `allowed_lucky|allowed_clear|denied_unlucky|denied_flagged|camera_false_positive|camera_false_negative`)
	- `confidence` (number, 0.0-1.0)
	- `entry_id` (string)

### Topic: `simulated-city/stadium/control/command`
- **Publishes:** `agent_control`
- **Subscribes:** `agent_people`, `dashboard`
- **Message schema (JSON):**
	- `person_id` (string)
	- `command_id` (string)
	- `timestamp` (string, ISO 8601)
	- `command` (string: `continue|enter|exit`)
	- `target_waypoint_id` (string)
	- `command_ttl_s` (number)

### Topic: `simulated-city/stadium/entry/event`
- **Publishes:** `agent_people`
- **Subscribes:** `agent_control`, `dashboard`
- **Message schema (JSON):**
	- `person_id` (string)
	- `timestamp` (string, ISO 8601)
	- `event_type` (string: `entered|denied|exited`)
	- `entry_id` (string)

### Topic: `simulated-city/stadium/occupancy/state`
- **Publishes:** `agent_control`
- **Subscribes:** `dashboard`
- **Message schema (JSON):**
	- `timestamp` (string, ISO 8601)
	- `inside_count` (integer, only persons allowed and crossed the gate line)

### Topic: `simulated-city/stadium/system/heartbeat`
- **Publishes:** `agent_people`, `agent_camera`, `agent_control`, `dashboard`
- **Subscribes:** `dashboard` (and optional operations monitor)
- **Message schema (JSON):**
	- `agent_name` (string)
	- `timestamp` (string, ISO 8601)
	- `status` (string: `ok|degraded|error`)
	- `tick_id` (integer)

## 3. Configuration Parameters

Suggested keys for `config.yaml` with realistic defaults:

### MQTT broker settings
- `mqtt.profiles.local.host`: `localhost`
- `mqtt.profiles.local.port`: `1883`
- `mqtt.profiles.local.username_env`: `MQTT_USER`
- `mqtt.profiles.local.password_env`: `MQTT_PASS`
- `mqtt.profiles.local.tls`: `false`
- `mqtt.profiles.local.keepalive_s`: `60`
- `mqtt.profiles.local.client_id_prefix`: `stadium-sim`
- `mqtt.profiles.local.base_topic`: `simulated-city/stadium`
- `mqtt.active_profiles`: `[local]`

### GPS coordinates and map geometry
- `simulation.stadium.center_lat`: `55.6479`
- `simulation.stadium.center_lon`: `12.0417`
- `simulation.stadium.boundary_radius_m`: `220`
- `simulation.stadium.entries`: list of entry objects with `entry_id`, `lat`, `lon`
- `simulation.stadium.entry_gate_lines`: list of gate-line segments with `entry_id`, `lat1`, `lon1`, `lat2`, `lon2`
- `simulation.stadium.gate_crossing_tolerance_m`: `1.5`
- `simulation.stadium.exit_waypoints`: list of waypoint objects with `waypoint_id`, `lat`, `lon`

### Thresholds and limits
- `simulation.population.total_people`: `50`
- `simulation.population.max_inside`: `50000`
- `simulation.motion.min_speed_kmh`: `5.0`
- `simulation.motion.max_speed_kmh`: `6.0`
- `simulation.motion.step_noise_m`: `0.5`
- `simulation.decision.true_allow_probability`: `0.80`
- `simulation.decision.camera_confidence_threshold`: `0.70`
- `simulation.decision.entry_proximity_m`: `8`
- `simulation.decision.out_of_bounds_margin_m`: `15`
- `simulation.decision.false_positive_rate`: `0.05`
- `simulation.decision.false_negative_rate`: `0.10`
- `simulation.routing.tie_break_rule`: `lowest_entry_id`
- `simulation.routing.retarget_interval_s`: `5.0`
- `simulation.routing.lock_on_at_distance_m`: `12.0`

### Timing parameters
- `simulation.timing.tick_interval_s`: `1.0`
- `simulation.timing.person_state_publish_interval_s`: `1.0`
- `simulation.timing.occupancy_publish_interval_s`: `2.0`
- `simulation.timing.command_timeout_s`: `5.0`
- `simulation.timing.command_retry_interval_s`: `2.0`
- `simulation.timing.heartbeat_interval_s`: `10.0`
- `simulation.random.seed`: `42`

## 4. Architecture Decisions

### Notebooks to Create
- `notebooks/agent_people.ipynb`: simulates person movement, publishes person state and entry events, applies control commands.
- `notebooks/agent_camera.ipynb`: subscribes to person state near entries and publishes allow/deny decisions.
- `notebooks/agent_control.ipynb`: consumes camera decisions and entry events, publishes movement commands and occupancy state.
- `notebooks/dashboard.ipynb`: subscribes to all relevant topics and renders live map plus occupancy counters.

### Library Code (src/simulated_city/)

#### Data models (dataclasses)
- `PersonState`: person identity, location, state, color, speed, target entry.
- `CameraDecision`: person ID, allowed flag, reason code, confidence, entry ID.
- `ControlCommand`: command type, target waypoint, timeout metadata.
- `EntryEvent`: entered/denied/exited event payload.
- `OccupancyState`: current counts and timestamp.

#### Utility functions
- Topic builder helpers using configured `base_topic`.
- JSON payload validation helpers for required fields/types.
- Coordinate and distance helpers for entry proximity checks.
- State transition guard helpers (allowed transitions only, latest command wins on conflict).

#### Calculation helpers
- Entry-zone distance calculations.
- Occupancy counter update rules from entry events.
- Target selection for dynamic nearest-entry routing and exit waypoint.
- Routing rules: nearest entry each `retarget_interval_s`, tie-break by lowest `entry_id`, and lock entry when distance is below `lock_on_at_distance_m`.
- Tick-based movement step updates with bounded noise.

### Classes vs Functions

#### Model as classes
- Stateful agents: people, camera, control, dashboard subscribers.
- Data models for MQTT messages and simulation state.
- Optional occupancy tracker with internal counters.

#### Model as functions
- Pure calculations (distance, heading, step interpolation).
- Message transformations (dataclass ⇄ dict/json).
- Stateless validations (schema checks, command validity).
- Topic formatting and config extraction helpers.

## 5. Resolved Decisions

- Denied persons exit permanently.
- Allowed/denied ground truth is random with more allowed than denied (`true_allow_probability`).
- Camera output can differ from ground truth through false positives/false negatives.
- Entry assignment uses dynamic nearest-entry routing with explicit tie-break and lock-on behavior.
- "Inside stadium" is defined by crossing a configured entry gate line within tolerance.
- Occupancy state tracks only `inside_count` (allowed persons who crossed the gate line).
- MQTT uses QoS `0` and no retained messages.
- Command conflict handling uses latest command wins.
- With dropped commands, people continue the last valid command until TTL expiry or a new valid command arrives.
