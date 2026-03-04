# Simulated City Workshop Overview

This repository provides a beginner-friendly, notebook-first template for a distributed city simulation using MQTT.

## Phase 6 architecture

The project uses one notebook per agent:

- `notebooks/agent_people.ipynb`
  - Simulates people movement and state changes.
  - Publishes person state and entry/exit events.
- `notebooks/agent_camera.ipynb`
  - Subscribes to person state.
  - Publishes allow/deny decisions.
- `notebooks/agent_control.ipynb`
  - Subscribes to camera decisions and entry/exit events.
  - Publishes control commands with TTL metadata and latest-command-wins sequencing.
  - Publishes occupancy updates.
- `notebooks/dashboard.ipynb`
  - Subscribes to simulation topics and renders the live map with `anymap-ts`.

This separation avoids monolithic notebooks and allows each agent to restart independently.

## Shared Python helpers

Reusable helpers are placed in `src/simulated_city/`:

- `config.py`: loads YAML + environment settings.
- `mqtt.py`: MQTT connection and checked publish helpers.
- `agent_rules.py`: shared routing/reliability logic:
  - nearest-point routing helper
  - gate crossing with tolerance check
  - permanent-exit rule helper
  - latest-command-wins command store
  - retry interval helper

## Reliability behavior in Phase 6

- Command publishing uses QoS `0` with retry interval handling.
- Commands carry TTL/expiry metadata.
- Latest command wins per person using monotonically increasing sequence numbers.
- Occupancy is derived from gate events (`entered`, `exited`) and published as state updates.

## Submission reminder

Include this line in your PR description:

```text
Docs updated: yes/no
```

If `yes`, list updated doc files. If `no`, provide one sentence explaining why no docs changed.
