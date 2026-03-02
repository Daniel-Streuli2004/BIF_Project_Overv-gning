# Clarified Design (Pre-Code)

## 1. System Overview

### Trigger (Movement Generator)
- Simulate 50 person agents moving around Brøndby Stadium.
- All persons start with neutral status and white color.
- Each person is assigned a movement target from a list of stadium entrances.
- Persons remain white while approaching entrances and only change status at entry attempt.

### Observer (Perception Layer)
- A camera-sensor agent observes persons when they reach an entry zone.
- The observer evaluates each entry attempt and produces a normalized decision.
- Decision output contains an `allowed` boolean and a `reason_code`.

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
- A dashboard displays live person locations, colors, and stadium occupancy.
- Occupancy is updated when entry events are confirmed.

## 2. MQTT Architecture

Base namespace: `simulated-city/stadium`

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
	- `speed_mps` (number)
	- `target_entry_id` (string)

### Topic: `simulated-city/stadium/camera/decision`
- **Publishes:** `agent_camera`
- **Subscribes:** `agent_control`, `dashboard`
- **Message schema (JSON):**
	- `person_id` (string)
	- `timestamp` (string, ISO 8601)
	- `allowed` (boolean)
	- `reason_code` (string)
	- `confidence` (number, 0.0-1.0)
	- `entry_id` (string)

### Topic: `simulated-city/stadium/control/command`
- **Publishes:** `agent_control`
- **Subscribes:** `agent_people`, `dashboard`
- **Message schema (JSON):**
	- `person_id` (string)
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
	- `inside_count` (integer)
	- `approaching_count` (integer)
	- `exiting_count` (integer)
	- `denied_total` (integer)

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
- `simulation.stadium.exit_waypoints`: list of waypoint objects with `waypoint_id`, `lat`, `lon`

### Thresholds and limits
- `simulation.population.total_people`: `50`
- `simulation.population.max_inside`: `50000`
- `simulation.motion.min_speed_mps`: `0.8`
- `simulation.motion.max_speed_mps`: `1.8`
- `simulation.motion.step_noise_m`: `0.5`
- `simulation.decision.camera_confidence_threshold`: `0.70`
- `simulation.decision.entry_proximity_m`: `8`
- `simulation.decision.out_of_bounds_margin_m`: `15`

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
- State transition guard helpers (allowed transitions only).

#### Calculation helpers
- Entry-zone distance calculations.
- Occupancy counter update rules from entry events.
- Target selection for nearest/assigned entry and exit waypoint.
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

## 5. Open Questions

- Should an initially denied person be allowed to attempt a different entrance later, or always exit permanently?
- What exact policy determines `allowed` decisions: random probability, rule-based profile flags, or external input?
- How should entry assignment work: fixed entry per person at startup, or dynamic nearest-entry routing?
- Is "inside stadium" defined only by gate crossing, or also by position within a stadium boundary polygon?
- Should occupancy track only current inside count, or also cumulative entered/denied totals for reporting?
- What MQTT QoS level should be used per topic (`0`, `1`, or `2`), and should any topics be retained?
- Should command conflict handling be strict (latest command wins) or state-validated (reject conflicting commands)?
- Are there scenario constraints for camera false positives/false negatives that must be modeled explicitly?
