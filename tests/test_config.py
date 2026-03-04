from simulated_city.config import load_config
from textwrap import dedent


def test_load_config_defaults_when_missing(tmp_path) -> None:
    """Test that default config loads when file is missing."""
    cfg = load_config(tmp_path / "missing.yaml")
    assert cfg.mqtt.host
    assert cfg.mqtt.port
    # Should have at least the default 'local' profile
    assert "local" in cfg.mqtt_configs or len(cfg.mqtt_configs) > 0


def test_load_config_reads_yaml(tmp_path) -> None:
    """Test reading YAML config with multi-broker structure."""
    p = tmp_path / "config.yaml"
    p.write_text(
        """
        mqtt:
          active_profiles: [default]
          profiles:
            default:
              host: example.com
              port: 1883
              tls: false
          client_id_prefix: demo
          keepalive_s: 30
        """.strip(),
        encoding="utf-8",
    )

    cfg = load_config(p)
    assert cfg.mqtt.host == "example.com"
    assert cfg.mqtt.port == 1883
    assert cfg.mqtt.tls is False
    assert cfg.mqtt.client_id_prefix == "demo"
    assert cfg.mqtt.keepalive_s == 30


def test_load_config_finds_parent_config_yaml(tmp_path, monkeypatch) -> None:
    """Test that config is found in parent directories."""
    # Simulate running from a subdirectory (like notebooks/)
    root = tmp_path
    (root / "config.yaml").write_text(
        """
        mqtt:
          active_profiles: [parent]
          profiles:
            parent:
              host: parent.example.com
              port: 1883
              tls: false
          client_id_prefix: demo
          keepalive_s: 30
        """.strip(),
        encoding="utf-8",
    )

    subdir = root / "notebooks"
    subdir.mkdir()
    monkeypatch.chdir(subdir)

    cfg = load_config("config.yaml")
    assert cfg.mqtt.host == "parent.example.com"

def test_load_config_multi_broker_with_active_profiles(tmp_path) -> None:
    """Test multi-broker configuration with active_profiles list."""
    p = tmp_path / "config.yaml"
    p.write_text(
        """
        mqtt:
          active_profiles: [local, public]
          profiles:
            local:
              host: localhost
              port: 1883
              tls: false
            public:
              host: broker.example.com
              port: 1883
              tls: false
          client_id_prefix: multi-test
          keepalive_s: 60
          base_topic: test-city
        """.strip(),
        encoding="utf-8",
    )

    cfg = load_config(p)
    
    # Primary broker (first in list)
    assert cfg.mqtt.host == "localhost"
    assert cfg.mqtt.port == 1883
    
    # All brokers available by name
    assert "local" in cfg.mqtt_configs
    assert "public" in cfg.mqtt_configs
    assert cfg.mqtt_configs["local"].host == "localhost"
    assert cfg.mqtt_configs["public"].host == "broker.example.com"


def test_load_config_single_broker_with_active_profiles(tmp_path) -> None:
    """Test single-broker configuration using active_profiles."""
    p = tmp_path / "config.yaml"
    p.write_text(
        """
        mqtt:
          active_profiles: [local]
          profiles:
            local:
              host: localhost
              port: 1883
              tls: false
          client_id_prefix: single-test
          keepalive_s: 60
          base_topic: test-city
        """.strip(),
        encoding="utf-8",
    )

    cfg = load_config(p)
    
    # Primary broker
    assert cfg.mqtt.host == "localhost"
    
    # Only local broker in configs
    assert "local" in cfg.mqtt_configs
    assert len(cfg.mqtt_configs) == 1


def test_load_config_phase6_timing_and_gate_tolerance(tmp_path) -> None:
    """Test parsing of Phase 6 timing and gate-crossing simulation fields."""
    p = tmp_path / "config.yaml"
    p.write_text(
        dedent(
            """
            mqtt:
              active_profiles: [local]
              profiles:
                local:
                  host: localhost
                  port: 1883
                  tls: false
            simulation:
              stadium:
                center_lat: 55.65
                center_lon: 12.4186
                gate_crossing_tolerance_m: 2.5
              timing:
                tick_interval_s: 1.0
                command_timeout_s: 9.0
                command_retry_interval_s: 3.0
                occupancy_publish_interval_s: 4.0
                heartbeat_interval_s: 12.0
            """
        ).strip(),
        encoding="utf-8",
    )

    cfg = load_config(p)
    assert cfg.simulation is not None
    assert cfg.simulation.command_timeout_s == 9.0
    assert cfg.simulation.command_retry_interval_s == 3.0
    assert cfg.simulation.occupancy_publish_interval_s == 4.0
    assert cfg.simulation.heartbeat_interval_s == 12.0
    assert cfg.simulation.gate_crossing_tolerance_m == 2.5


def test_load_config_motion_speed_kmh_and_mps_fallback(tmp_path) -> None:
    """Test simulation motion speed parsing with km/h keys and legacy mps fallback."""
    p = tmp_path / "config.yaml"
    p.write_text(
        dedent(
            """
            mqtt:
              active_profiles: [local]
              profiles:
                local:
                  host: localhost
                  port: 1883
                  tls: false
            simulation:
              motion:
                min_speed_kmh: 5.5
                max_speed_kmh: 6.2
            """
        ).strip(),
        encoding="utf-8",
    )

    cfg = load_config(p)
    assert cfg.simulation is not None
    assert cfg.simulation.min_speed_kmh == 5.5
    assert cfg.simulation.max_speed_kmh == 6.2

    p2 = tmp_path / "legacy-config.yaml"
    p2.write_text(
        dedent(
            """
            mqtt:
              active_profiles: [local]
              profiles:
                local:
                  host: localhost
                  port: 1883
                  tls: false
            simulation:
              motion:
                min_speed_mps: 1.0
                max_speed_mps: 1.5
            """
        ).strip(),
        encoding="utf-8",
    )

    cfg2 = load_config(p2)
    assert cfg2.simulation is not None
    assert cfg2.simulation.min_speed_kmh == 3.6
    assert cfg2.simulation.max_speed_kmh == 5.4