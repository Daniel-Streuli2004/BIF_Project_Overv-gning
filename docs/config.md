# Configuration (`simulated_city.config`)

This project loads configuration from:

- `config.yaml` for non-secret defaults
- `.env` (optional, gitignored) for secrets like broker credentials

For Phase 2, you define both MQTT and simulation parameters in `config.yaml` so notebooks do not hardcode values.


## Install

The base install already includes config support:

```bash
python -m pip install -e "."
```


## Data classes

### `MqttConfig`

Holds broker and topic settings for one active profile.

Main fields:

- `host`, `port`, `tls`
- `username`, `password` (resolved from env vars when configured)
- `client_id_prefix`, `keepalive_s`, `base_topic`


### `AppConfig`

Top-level config wrapper contains:

- `mqtt: MqttConfig` (primary active profile)
- `mqtt_configs: dict[str, MqttConfig]` (all active profiles)
- `simulation` (optional simulation section)


## Functions

### `load_config(path="config.yaml") -> AppConfig`

Loads configuration with these rules:

1. Load `.env` if present.
2. Resolve `config.yaml` from the current folder or parent folders.
3. Read active MQTT profiles from `mqtt.active_profiles`.
4. Merge common MQTT settings with profile-specific overrides.
5. Resolve credentials from env vars defined in profile keys:
   - `username_env`
   - `password_env`
6. Parse optional `simulation:` mapping.

Example:

```python
from simulated_city.config import load_config

cfg = load_config()
print(cfg.mqtt.host, cfg.mqtt.port, cfg.mqtt.tls)
print("base topic:", cfg.mqtt.base_topic)
```

## Phase 2 `config.yaml` layout

Phase 2 expects these sections in `config.yaml`:

### MQTT section

- `mqtt.active_profiles`
- `mqtt.profiles.<name>.host`
- `mqtt.profiles.<name>.port`
- `mqtt.profiles.<name>.tls`
- `mqtt.profiles.<name>.username_env` (optional)
- `mqtt.profiles.<name>.password_env` (optional)
- `mqtt.client_id_prefix`
- `mqtt.keepalive_s`
- `mqtt.base_topic`

### Simulation section

- `simulation.seed`
- `simulation.total_people`
- `simulation.locations` (entry-compatible fallback list)
- `simulation.stadium.center_lat`
- `simulation.stadium.center_lon`
- `simulation.stadium.boundary_radius_m`
- `simulation.stadium.entries`
- `simulation.stadium.entry_gate_lines`
- `simulation.stadium.gate_crossing_tolerance_m`
- `simulation.stadium.exit_waypoints`
- `simulation.motion.min_speed_kmh`
- `simulation.motion.max_speed_kmh`
- `simulation.motion.step_noise_m`
- `simulation.routing.tie_break_rule`
- `simulation.routing.retarget_interval_s`
- `simulation.routing.lock_on_at_distance_m`
- `simulation.decision.true_allow_probability`
- `simulation.decision.camera_confidence_threshold`
- `simulation.decision.entry_proximity_m`
- `simulation.decision.out_of_bounds_margin_m`
- `simulation.decision.false_positive_rate`
- `simulation.decision.false_negative_rate`
- `simulation.timing.tick_interval_s`
- `simulation.timing.person_state_publish_interval_s`
- `simulation.timing.occupancy_publish_interval_s`
- `simulation.timing.command_timeout_s`
- `simulation.timing.command_retry_interval_s`
- `simulation.timing.heartbeat_interval_s`

## Notes for this phase

- You keep using `load_config()` in notebooks.
- You do not add MQTT publish/subscribe implementation in Phase 2.
- You define configuration now so later phases can consume the same keys without hardcoding.


## Internal helpers (advanced)

These are used by `load_config()` and normally don’t need to be called directly:

- `_load_yaml_dict(path) -> dict`: reads a YAML mapping (or returns `{}`)
- `_resolve_default_config_path(path) -> Path`: notebook-friendly path resolution
