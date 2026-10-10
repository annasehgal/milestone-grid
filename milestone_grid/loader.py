"""Local YAML loading and private-only saving."""

from pathlib import Path
import yaml

PRIVATE_DIR = Path("private")
DEFAULT_PRIVATE = PRIVATE_DIR / "tracker.local.yaml"
PRIVATE_LABELS = PRIVATE_DIR / "labels.local.yaml"
SAMPLE = Path("examples/sample.yaml")
DEFAULT_LABELS = {
    "primary_entity": "Item", "secondary_entity": "Track", "resources": "Resources",
    "primary_date": "Primary date", "secondary_date": "Secondary date",
    "target_date": "Target date",
}


def _read_yaml(path):
    with Path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_tracker(path=None):
    source = Path(path) if path else DEFAULT_PRIVATE if DEFAULT_PRIVATE.exists() else SAMPLE
    data = _read_yaml(source)
    if not isinstance(data, dict):
        raise ValueError("Tracker root must be a mapping")
    for key in ("items", "resources", "archive", "completed", "history", "decisions"):
        data.setdefault(key, [])
        if not isinstance(data[key], list):
            raise ValueError(f"{key} must be a list")
    data.setdefault("settings", {})
    labels = dict(DEFAULT_LABELS)
    labels.update(data.get("labels") or {})
    if source.resolve() == DEFAULT_PRIVATE.resolve() and PRIVATE_LABELS.exists():
        overrides = _read_yaml(PRIVATE_LABELS)
        if not isinstance(overrides, dict):
            raise ValueError("Local labels must be a mapping")
        labels.update(overrides)
    data["labels"] = labels
    return data, source


def save_tracker(data, path):
    target = Path(path)
    if not target.name.endswith(".local.yaml") or PRIVATE_DIR.resolve() not in target.resolve().parents:
        raise ValueError("Edits can only be saved to an ignored local YAML file")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True, width=100)
