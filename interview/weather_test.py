from . import weather
import pytest


def run(events):
    return list(weather.process_events(events))

def test_single_basic_snapshot():
    """Testing a snapshot for a single station"""
    events = [
        {"type": "sample", "stationName": "Chicago", "timestamp": 1000, "temperature": 32.0},
        {"type": "sample", "stationName": "Chicago", "timestamp": 2000, "temperature": 36.0},
        {"type": "control", "command": "snapshot"},
    ]
    output = run(events)
    assert len(output) == 1
    snapshot = output[0]
    assert(snapshot["type"] == "snapshot")
    assert(snapshot["asOf"] == 2000)
    assert(snapshot["stations"] == {"Chicago": {"high": 36.0, "low": 32.0}})

def test_multiple_stations_snapshot():
    """Testing a snapshot for multiple stations after adding some different values"""
    events = [
        {"type": "sample", "stationName": "Chicago", "timestamp": 1000, "temperature": 36.0},
        {"type": "sample", "stationName": "NYC", "timestamp": 2000, "temperature": 20.0},
        {"type": "sample", "stationName": "Chicago", "timestamp": 5000, "temperature": 55.0},
        {"type": "control", "command": "snapshot"},
    ]
    output = run(events)
    assert len(output) == 1
    snapshot = output[0]
    assert snapshot["asOf"] == 5000
    assert snapshot["stations"] == {
        "Chicago": {"high": 55.0, "low": 36.0},
        "NYC": {"high": 20.0, "low": 20.0},
    }

def test_reset_clears_state():
    """Testing to make sure reset clears state appropriately"""
    events = [
        {"type": "sample", "stationName": "Chicago", "timestamp": 1000, "temperature": 32.0},
        {"type": "control", "command": "reset"},   
        {"type": "control", "command": "snapshot"},  
        {"type": "sample", "stationName": "Chicago", "timestamp": 2000, "temperature": 40.0},
        {"type": "control", "command": "snapshot"},
    ]

    output = run(events)
    assert len(output) == 2
    reset = output[0]
    assert reset["type"] == "reset"
    assert reset["asOf"] == 1000
    snapshot = output[1]
    assert snapshot["type"] == "snapshot"
    assert snapshot["asOf"] == 2000
    assert snapshot["stations"] == {"Chicago": {"high": 40.0, "low": 40.0}}

def test_control_ignored_before_any_sample():
    """Testing to make sure that control messages before samples are ignored"""
    events = [
        {"type": "control", "command": "snapshot"},
        {"type": "control", "command": "reset"},
        {"type": "sample", "stationName": "Chicago", "timestamp": 1000, "temperature": 10},
        {"type": "control", "command": "snapshot"},
    ]
    output = run(events)
    assert len(output) == 1
    snapshot = output[0]
    assert snapshot["asOf"] == 1000
    assert snapshot["stations"] == {"Chicago": {"high": 10, "low": 10}}


def test_unknown_type_raises():
    """Testing to make sure that invalid types are handled correctly"""
    events = [
        {"type": "mysteryType", "Miami": 123}
    ]
    with pytest.raises(ValueError) as e:
        run(events)
    assert "Please verify input." in str(e.value)

def test_unknown_command_raises():
    """Testing to make sure that invalid commands are hanlded correctly"""
    events = [
        {"type": "sample", "stationName": "Chicago", "timestamp": 1000, "temperature": 10},
        {"type": "control", "command": "record"},
    ]
    with pytest.raises(ValueError) as e:
        run(events)
    assert "Please verify input." in str(e.value)







