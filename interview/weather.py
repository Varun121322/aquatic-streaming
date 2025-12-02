from typing import Any, Iterable, Generator


def process_events(events: Iterable[dict[str, Any]]) -> Generator[dict[str, Any], None, None]:
    stations = {}
    last_sample_time_stamp = None
    
    for message in events:
        if "type" not in message:
            raise ValueError("Type field missing in message")
        
        message_type = message["type"]
        if message_type == "sample":
            try:
                name = message["stationName"]
                time_stamp = message["timestamp"]
                temperature = message["temperature"]
            except:
                raise ValueError("Missing field in message")
            last_sample_time_stamp = time_stamp
            stats = stations.get(name)
            if stats is None:
                stations[name] = {"high": temperature, "low": temperature}
            else:
                if temperature > stations[name]["high"]:
                    stations[name]["high"] = temperature
                if temperature < stations[name]["low"]:
                    stations[name]["low"] = temperature
        elif message_type == "control":
            command = message.get("command")
            if command is None:
                print("Command field missing")
            if last_sample_time_stamp is None:
                continue
            if command == "snapshot":
                stations_snapshot = {
                    name: {"high": vals["high"], "low": vals["low"]}
                    for name, vals in stations.items()
                }
                yield {
                    "type": "snapshot",
                    "asOf": last_sample_time_stamp,
                    "stations": stations_snapshot
                }
            elif command == "reset":
                yield{
                    "type": "reset",
                    "asOf": last_sample_time_stamp
                }
                stations.clear()
                last_sample_time_stamp = None
            else:
                raise ValueError("Please verify input.")
        else:
            raise ValueError("Please verify input.")
        