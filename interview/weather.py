from typing import Any, Iterable, Generator


def process_events(events: Iterable[dict[str, Any]]) -> Generator[dict[str, Any], None, None]:
    # A dictionary from station name to another dictionary of high: float, low: float
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
        