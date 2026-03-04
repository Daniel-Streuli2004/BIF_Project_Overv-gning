# Phases Runtime Guide

This document explains how to run the implemented phases end-to-end.

## Prerequisites

From repository root:

```bash
pip install -e ".[dev,notebooks]"
python scripts/verify_setup.py
python scripts/validate_structure.py
python -m pytest
```

## Runtime order

Start JupyterLab:

```bash
python -m jupyterlab
```

Then run notebooks in this order.

## Phase 3: People agent

Notebook: `notebooks/agent_people.ipynb`

- Run setup cells first.
- Run MQTT connect cell.
- Run simulation/publish loop cell.

Expected behavior:
- Publishes `person/state` and `entry/event` topics.
- Emits final counts after simulation loop.

## Phase 4: Camera agent

Notebook: `notebooks/agent_camera.ipynb`

- Run setup/config cells.
- Run MQTT connect + callback cells.
- Keep runtime cell active while people agent publishes.

Expected behavior:
- Subscribes to `person/state`.
- Publishes allow/deny decisions to `camera/decision`.

## Phase 5: Dashboard

Notebook: `notebooks/dashboard.ipynb`

- Run import/config and map cells.
- Run MQTT subscription/callback cell.
- Optionally run heartbeat loop cell.

Expected behavior:
- Shows live markers with `white`/`green`/`red` states.
- Tracks camera decisions and occupancy-related counters.

## Phase 6: Control agent

Notebook: `notebooks/agent_control.ipynb`

- Run setup/config cells.
- Run MQTT connect + callback cell.
- Run control loop cell.

Expected behavior:
- Subscribes to `camera/decision` and `entry/event`.
- Publishes latest-command-wins command messages to `control/command`.
- Commands include TTL metadata and sequence fields.
- Retries command publishes using QoS `0` retry interval logic.
- Publishes occupancy snapshots to `occupancy/state`.

## MQTT topics summary

- `.../person/state` (people -> camera/dashboard)
- `.../camera/decision` (camera -> dashboard/control)
- `.../entry/event` (people -> dashboard/control)
- `.../control/command` (control -> downstream command consumers)
- `.../occupancy/state` (control -> dashboard/monitoring)

## Validation checklist

- Agents are in separate notebooks (no monolithic workflow).
- Map is rendered with `anymap-ts`.
- Config values come from `config.yaml`.
- MQTT helper functions from `simulated_city.mqtt` are used.

## PR reminder

Add this in your PR description:

```text
Docs updated: yes/no
```
