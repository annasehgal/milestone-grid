"""Private calendar export."""

from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from icalendar import Calendar, Event, Alarm

from .timeline import event_label, events

PRIVATE_EXPORTS = Path("exports/private")


def build_calendar(data, reminders=()):
    calendar = Calendar()
    calendar.add("prodid", "-//milestone-grid//local//EN")
    calendar.add("version", "2.0")
    zone = ZoneInfo(data.get("settings", {}).get("timezone", "UTC"))
    for entry in events(data):
        event = Event()
        event.add("summary", f"{entry['kind']}: {entry['name']} / {entry['track']}")
        event.add("description", event_label(entry["confidence"]))
        hour, minute = (int(part) for part in entry["time"].split(":")) if entry.get("time") else (9, 0)
        start = datetime.combine(entry["date"], time(hour, minute), zone)
        event.add("dtstart", start)
        event.add("dtend", start + timedelta(minutes=30))
        event.add("uid", f"{entry['date']}-{entry['kind']}-{entry['name']}-{entry['track']}@milestone-grid.local")
        for days in reminders:
            alarm = Alarm()
            alarm.add("action", "DISPLAY")
            alarm.add("description", event_label(entry["confidence"]))
            alarm.add("trigger", timedelta(days=-int(days)))
            event.add_component(alarm)
        calendar.add_component(event)
    return calendar.to_ical()


def save_calendar(data, reminders=(), path=None):
    target = Path(path or PRIVATE_EXPORTS / "milestones.local.ics")
    if target.suffix != ".ics" or PRIVATE_EXPORTS.resolve() not in target.resolve().parents:
        raise ValueError("Calendar exports must stay in exports/private")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(build_calendar(data, reminders))
    return target
