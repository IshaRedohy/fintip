import json
from pathlib import Path


PREFERENCES_VERSION = 1
DEFAULT_PREFERENCES_PATH = Path(__file__).resolve().parent.parent / ".fintip_preferences.json"
DEFAULT_ALERT_STATE_PATH = Path(__file__).resolve().parent.parent / ".fintip_alert_state.json"


def _write_json(path, data):
    path = Path(path)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    temporary_path.replace(path)


def save_preferences(preferences, path=DEFAULT_PREFERENCES_PATH):
    _write_json(path, {"version": PREFERENCES_VERSION, "tickers": preferences})


def load_preferences(path=DEFAULT_PREFERENCES_PATH):
    data = json.loads(Path(path).read_text())
    if data.get("version") != PREFERENCES_VERSION or not isinstance(data.get("tickers"), list):
        raise ValueError("Unsupported or malformed preferences file")
    from trading.monitoring_plan import build_monitoring_plan

    return build_monitoring_plan(data["tickers"])


def load_alert_state(path=DEFAULT_ALERT_STATE_PATH):
    path = Path(path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("Malformed alert state file")
    return data


def save_alert_state(state, path=DEFAULT_ALERT_STATE_PATH):
    _write_json(path, state)
