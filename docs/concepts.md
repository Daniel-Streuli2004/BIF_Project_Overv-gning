# Clarified Design (Pre-Code)

## 1) Four Components (Technical Rewrite)

- Trigger (Movement Generator): Simulate 50 person agents around Brøndby Stadium with fixed initial cohorts: 20 in searching_entry, 25 in entering, 5 in blocked_exiting. Each person has an ID, display name, position, velocity/step behavior, and status color (yellow/green/red).
- Observer (Perception Layer): A camera-sensor agent ingests person position/state updates and determines whether a person is authorized to enter. It produces a normalized decision (allowed true/false + reason code) rather than raw color-only logic.
- Control Center (Decision Layer): A control agent consumes sensor decisions and current movement state, then publishes movement directives: continue searching, proceed to gate/inside, or move away from stadium perimeter.
- Response (Actuation + Outcome): Person agents apply directives and update trajectory/state. A dashboard agent visualizes live positions and stadium occupancy, including an inside_count counter updated when entry events are confirmed.

## 2) MQTT Topic Design (Agent Pub/Sub)

### stadium/person/state
- Publishes: agent_people
- Subscribes: agent_camera, agent_control, dashboard
- Payload: person ID, timestamp, lat/lon, current state, color, speed, heading

### stadium/camera/decision
- Publishes: agent_camera
- Subscribes: agent_control, dashboard
- Payload: person ID, allowed flag, reason code, confidence, timestamp

### stadium/control/command
- Publishes: agent_control
- Subscribes: agent_people, dashboard
- Payload: person ID, command (search|enter|exit), target waypoint ID, effective timestamp

### stadium/entry/event
- Publishes: agent_people (on gate crossing)
- Subscribes: agent_control, dashboard
- Payload: person ID, event type (entered|denied|exited), gate ID, timestamp

### stadium/occupancy/state
- Publishes: agent_control (or dedicated occupancy agent)
- Subscribes: dashboard
- Payload: inside count, denied count, searching count, entering count, blocked count, timestamp

### stadium/system/heartbeat
- Publishes: all agents
- Subscribes: dashboard/ops monitor
- Payload: agent name, status, last processed tick, timestamp

## 3) Configuration Parameters (What should be in config)

### MQTT broker
- host, port, username env key, password env key, keepalive, TLS enabled, client ID prefix, base topic

### Locations
- stadium center lat/lon
- stadium boundary radius/polygon
- entry gate coordinates (list)
- exit corridor/away-point coordinates

### Simulation limits
- total persons = 50
- cohort sizes: searching 20, entering 25, blocked 5
- max speed, min speed, step distance noise
- max persons inside (optional safety threshold)

### Decision thresholds
- camera confidence threshold
- gate proximity threshold (meters) to trigger entry event
- out-of-bounds threshold for corrective command

### Timing
- simulation tick interval (e.g., 0.5–1.0 s)
- publish intervals per topic (state faster, occupancy slower)
- command timeout/retry window
- heartbeat interval

### Good default assumptions
- single local broker profile for development, plus optional cloud profile
- base topic namespace per project (simulated-city/stadium)
- deterministic random seed for repeatable demos

## 4) Ambiguities / Missing Details to Confirm

- Whether cohort membership is fixed, or if people can transition between yellow/green/red categories dynamically.
- Exact rule for “allowed”: is it predefined at startup, sensor-derived, or both.
- Whether denied persons can re-attempt entry or must permanently exit.
- Definition of “inside stadium” (gate crossing, polygon containment, or both).
- Counter semantics: current inside count only, or cumulative entries as well.
- Movement model detail: purely random walk vs waypoint-guided behavior.
- Required QoS/retain policy per topic and whether offline message replay matters.
- Whether control decisions are centralized only, or partially autonomous per person agent.
