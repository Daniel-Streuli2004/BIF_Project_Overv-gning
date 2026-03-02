# MQTT

This template includes **paho-mqtt** by default and ships with a committed `config.yaml` that supports **multiple MQTT brokers simultaneously**.

## Phase 3: People Agent Publishing

Phase 3 adds MQTT publishing from `notebooks/agent_people.ipynb`.

The notebook now:
- loads broker settings from `config.yaml` through `load_config()`
- connects with `mqtt.connect_mqtt(mqtt_cfg)`
- publishes with `mqtt.publish_json_checked(...)`
- uses QoS `0` and no retained messages

### Topics used in Phase 3

- `simulated-city/stadium/person/state`
  - publisher: `agent_people`
  - payload fields:
    - `person_id`
    - `name`
    - `timestamp`
    - `lat`
    - `lon`
    - `state`
    - `color`
    - `speed_mps`
    - `target_entry_id`

- `simulated-city/stadium/entry/event`
  - publisher: `agent_people`
  - payload fields:
    - `person_id`
    - `timestamp`
    - `event_type` (`entered|denied|exited`)
    - `entry_id`

### Convenience helpers

The module provides notebook-friendly wrappers:

- `connect_mqtt(cfg, client_id_suffix=None)`
  - connects and waits for broker connection
  - returns a ready-to-use paho client

- `publish_json_checked(client, topic, data, qos=0, retain=False)`
  - accepts dict/list or string data
  - publishes JSON payload
  - waits for publish acknowledgement and returns success boolean

## Phase 4: Camera Agent Subscription + Decision Publishing

Phase 4 adds a second notebook agent: `notebooks/agent_camera.ipynb`.

The camera agent:
- subscribes to `simulated-city/stadium/person/state`
- evaluates each person once while in `approaching_entry`
- applies a random decision model with:
  - more allowed than denied outcomes
  - false positives and false negatives from config
- publishes decisions to `simulated-city/stadium/camera/decision`

### Topic flow in Phase 4

- Input topic (subscribed by camera):
  - `simulated-city/stadium/person/state`

- Output topic (published by camera):
  - `simulated-city/stadium/camera/decision`

### Decision payload schema

- `person_id` (string)
- `timestamp` (ISO string)
- `allowed` (boolean)
- `reason_code` (string)
- `confidence` (number)
- `entry_id` (string)

### Reason code taxonomy used

- `allowed_lucky`
- `allowed_clear`
- `denied_unlucky`
- `denied_flagged`
- `camera_false_positive`
- `camera_false_negative`

This document covers everything in `simulated_city.mqtt`:

- `MqttConnector`
- `MqttPublisher`

## Quick Start: Using Multiple Brokers

The configuration supports routing different messages to different brokers:

```yaml
mqtt:
  active_profiles: [local, mqtthq]  # Connect to both brokers
  profiles:
    local:
      host: "127.0.0.1"
      port: 1883
      tls: false
    mqtthq:
      host: "broker.mqttdashboard.com"
      port: 1883
      tls: false
```

Then in your code:

```python
from simulated_city.config import load_config

cfg = load_config()

# All configured brokers
for profile_name, broker_cfg in cfg.mqtt_configs.items():
    print(f"{profile_name}: {broker_cfg.host}:{broker_cfg.port}")

# Connect to a specific broker
connector = MqttConnector(cfg.mqtt_configs["local"], client_id_suffix="demo")
```

## Single Broker Setup

If you only want one broker, set:

```yaml
mqtt:
  active_profiles: [local]  # or [mqtthq] for public broker
```

## Configure HiveMQ Cloud

1. Edit `config.yaml` and add a HiveMQ profile:

```yaml
mqtt:
  active_profiles: [local, hivemq_cloud]
  profiles:
    hivemq_cloud:
      host: "xxxxxx.s1.eu.hivemq.cloud"  # Your cluster host
      port: 8883
      tls: true
      username_env: "HIVEMQ_USERNAME"
      password_env: "HIVEMQ_PASSWORD"
```

2. Store credentials in `.env`:

```bash
HIVEMQ_USERNAME=your_username
HIVEMQ_PASSWORD=your_password
```

## Connect from Python

```python
import time
from simulated_city.config import load_config
from simulated_city.mqtt import MqttConnector, MqttPublisher

cfg = load_config().mqtt

# Create a connector and connect
connector = MqttConnector(cfg, client_id_suffix="demo")
connector.connect()

# Wait for connection
if not connector.wait_for_connection():
    raise RuntimeError("Failed to connect to MQTT broker")

# Create a publisher and send a message
publisher = MqttPublisher(connector)
publisher.publish_json("simulated-city/metrics", '{"step": 1, "agents": 25}')

# Disconnect when done
time.sleep(1) # Give time for message to be sent
connector.disconnect()
```

Notes:

- `MqttConnector` handles the connection and automatic reconnection.
- You must call `connect()` to start the connection process.
- The network loop runs in a background thread.

## Monitoring Messages with mosquitto_sub

Use `mosquitto_sub` (part of the mosquitto command-line tools) to monitor messages published to your broker. This is useful for debugging and verifying that agents are publishing correctly.

### Subscribe to a Specific Topic

To monitor a specific topic (e.g., weather data):

```bash
mosquitto_sub -h localhost -t "simulated_city/weather/rain"
```

Replace `simulated_city/weather/rain` with any topic your agents publish to. Messages appear in real time as they arrive.

### Monitor All Messages

To subscribe to all messages on the broker, use the wildcard `#`:

```bash
mosquitto_sub -h localhost -t "#"
```

This displays every message published to any topic, which is helpful for seeing overall system activity.

### Monitor with Topic Verbosity

To see both the topic name and the message content clearly:

```bash
mosquitto_sub -h localhost -v -t "#"
```

The `-v` flag (verbose) prints the topic name before each message.

### Remote Broker Monitoring

If your broker is not on localhost, change the host:

```bash
mosquitto_sub -h broker.example.com -t "simulated_city/weather/rain"
```

For TLS-secured brokers, add `--cafile` or other TLS options as needed.

## Classes

### `MqttConnector`

A class that manages the MQTT connection and provides automatic reconnection.

#### `__init__(self, cfg, client_id_suffix=None)`

Creates a new `MqttConnector`.

#### `connect()`

Starts the connection to the broker and begins the network loop in a background thread.

#### `disconnect()`

Disconnects the client from the broker and stops the network loop.

#### `wait_for_connection(timeout=10.0) -> bool`

Blocks until the client is connected, or until the timeout is reached. Returns `True` if connected, `False` otherwise.


### `MqttPublisher`

A simple class for publishing messages.

#### `__init__(self, connector)`

Creates a new `MqttPublisher` that uses the provided `MqttConnector`.

#### `publish_json(topic, payload, qos=0, retain=False)`

Publishes a JSON string to the given topic. This is a convenience method around paho’s `publish()`.

Example:

```python
# Assuming 'connector' is a connected MqttConnector instance
publisher = MqttPublisher(connector)
publisher.publish_json("my/topic", '{"data": 123}')
```

## Switching Between Single and Multiple Brokers

You can quickly switch your setup by editing `config.yaml`:

**For local development only:**
```yaml
mqtt:
  active_profiles: [local]
```

**For local + public sharing:**
```yaml
mqtt:
  active_profiles: [local, mqtthq]
```

**For cloud-only (production):**
```yaml
mqtt:
  active_profiles: [hivemq_cloud]
```

Your code doesn't need to change—it automatically detects all active brokers via `cfg.mqtt_configs`.

## Using Other Brokers

