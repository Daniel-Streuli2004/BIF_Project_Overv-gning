# Simulated City Workshop Template

This repository is a notebook-driven template for building a distributed city simulation with MQTT.

## Core rules

- Use `anymap-ts` for mapping.
- Keep one notebook per agent.
- Load settings from `config.yaml` through `simulated_city.config.load_config()`.
- Use `simulated_city.mqtt.connect_mqtt()` and `simulated_city.mqtt.publish_json_checked()`.

## Notebooks

- `notebooks/agent_people.ipynb` — movement + person/event publishing
- `notebooks/agent_camera.ipynb` — decision subscriber/publisher
- `notebooks/agent_control.ipynb` — command + occupancy publisher (Phase 6)
- `notebooks/dashboard.ipynb` — map/dashboard subscriber

## Install

```bash
pip install -e ".[dev,notebooks]"
```

## Verify setup and tests

```bash
python scripts/verify_setup.py
python scripts/validate_structure.py
python -m pytest
```

## Run manually in JupyterLab

```bash
python -m jupyterlab
```

Open and run the four notebooks above in separate tabs.

## Documentation

- Overview: [docs/overview.md](docs/overview.md)
- Testing: [docs/testing.md](docs/testing.md)
- Runtime guide for all phases: [docs/phases_runtime.md](docs/phases_runtime.md)

## PR requirement

Include this line in your PR description:

```text
Docs updated: yes/no
```
