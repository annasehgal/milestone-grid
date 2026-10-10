from datetime import date
from pathlib import Path
import subprocess

from icalendar import Calendar

from milestone_grid.calendar_export import build_calendar
from milestone_grid.loader import load_tracker
from milestone_grid.records import active_items, date_text, sorted_items
from milestone_grid.resources import group
from milestone_grid.timeline import alerts, event_label, events, upcoming
from milestone_grid.validation import coverage, validate
from tools.privacy_check import scan


def sample_data():
    return {
        "settings": {"timezone": "UTC", "active_item_target": 2, "allow_restricted_requirements": False},
        "items": [
            {"name": "Project Atlas", "track": "Planning", "primary_deadline": "2027-02-01", "confidence": "confirmed", "state": "active", "status": "active"},
            {"name": "Renewal Beta", "track": "Operations", "primary_deadline": "2027-01-10", "confidence": "predicted", "prior_cycle_date": "2026-01-10", "predicted_window": "early January", "prediction_reason": "prior cycle", "state": "active", "status": "watch"},
            {"name": "Project Cedar", "track": "Past", "primary_deadline": "2027-01-01", "confidence": "confirmed", "state": "archived"},
        ],
        "resources": [{"item_name": "Project Atlas", "name": "Workspace access", "separate_action": True,
                       "automatic": False, "referral_required": False, "deadline": "2027-01-20",
                       "confidence": "confirmed", "state": "active"}],
        "archive": [], "completed": [], "history": [], "decisions": [],
    }


def test_yaml_loading(tmp_path):
    path = tmp_path / "example.yaml"
    path.write_text("items: []\nresources: []\n", encoding="utf-8")
    data, source = load_tracker(path)
    assert source == path
    assert data["archive"] == []
    assert data["labels"]["primary_entity"] == "Item"


def test_local_paths_are_ignored():
    root = Path(__file__).resolve().parents[1]
    paths = ["private/tracker.local.yaml", "private/labels.local.yaml",
             "private/privacy_terms.local.txt", "exports/private/milestones.local.ics"]
    result = subprocess.run(["git", "check-ignore", *paths], cwd=root, capture_output=True, text=True, check=True)
    assert result.stdout.splitlines() == paths


def test_sorting_and_archive_filter():
    data = sample_data()
    assert [item["name"] for item in sorted_items(data)] == ["Renewal Beta", "Project Atlas"]
    assert len(active_items(data)) == 2


def test_date_formatting_and_upcoming():
    data = sample_data()
    assert date_text("2027-01-10") == "Jan 10, 2027"
    entries = upcoming(data, 15, date(2027, 1, 5))
    assert [entry["name"] for entry in entries] == ["Renewal Beta", "Project Atlas"]
    assert entries[0]["confidence"] == "predicted"
    assert event_label("predicted") == "PREDICTED — VERIFY OFFICIAL DATE"
    assert event_label("personal_target") == "PERSONAL TARGET"
    assert [entry["name"] for entry in alerts(data, date(2027, 1, 3))] == ["Renewal Beta"]


def test_validation_and_coverage():
    data = sample_data()
    assert coverage(data)["covered"] == 2
    assert validate(data) == []
    data["items"][0].update(target_deadline="2027-02-02", secondary_deadline="2027-01-30",
                            restricted_requirement=True)
    data["resources"][0]["automatic"] = True
    messages = validate(data)
    assert any("Target follows" in message for message in messages)
    assert any("Secondary date precedes" in message for message in messages)
    assert any("Restricted item" in message for message in messages)
    assert any("Separate action" in message for message in messages)


def test_calendar_generation():
    data = sample_data()
    calendar = Calendar.from_ical(build_calendar(data, [7, 1]))
    entries = [entry for entry in calendar.walk() if entry.name == "VEVENT"]
    assert len(entries) == len(events(data)) == 3
    assert all(len([part for part in entry.subcomponents if part.name == "VALARM"]) == 2 for entry in entries)
    assert any("PREDICTED — VERIFY OFFICIAL DATE" in str(entry.get("description")) for entry in entries)


def test_resource_grouping():
    assert group({"state": "active", "separate_action": True}) == "Needs action"
    assert group({"state": "active", "automatic": True}) == "Automatic"
    assert group({"state": "active", "referral_required": True}) == "Nomination / referral"
    assert group({"state": "unavailable"}) == "Unavailable"


def test_local_term_scan(tmp_path):
    path = tmp_path / "candidate.txt"
    path.write_text("Project Atlas\nAtlasian\n", encoding="utf-8")
    assert scan([path], ["Atlas"]) == [(path, 1)]
