"""Loads configs/config.yaml. Every other script gets its settings from here."""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "configs" / "config.yaml"


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def machine():
    return "windows" if sys.platform == "win32" else "mac"


def server_spec(cfg, key):
    """Return the config block for 'simulator' or a tested-model key."""
    if key == "simulator":
        return cfg["simulator"]
    if key in cfg["tested_models"]:
        return cfg["tested_models"][key]
    raise KeyError(f"Unknown model key {key!r}. Known: simulator, {', '.join(cfg['tested_models'])}")
