import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.json"

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Errore caricando config.json: {e}")
        return {}
