"""Timeline events and date groups."""

from datetime import date

from .records import active_items, as_date

ALERT_DAYS = (60, 30, 14, 7, 3, 1)


def event_label(confidence):
    if confidence == "predicted":
        return "PREDICTED — VERIFY OFFICIAL DATE"
    if confidence == "personal_target":
        return "PERSONAL TARGET"
    return str(confidence or "tbd").replace("_", " ").upper()


def events(data, today=None):
    today = today or date.today()
    result = []
    for item in active_items(data):
        for field, kind, confidence in (
            ("primary_deadline", "Primary", item.get("confidence", "tbd")),
            ("target_deadline", "Target", "personal_target"),
            ("secondary_deadline", "Secondary", item.get("secondary_confidence", "confirmed")),
        ):
            due = as_date(item.get(field))
            if due:
                result.append({"date": due, "days": (due - today).days, "kind": kind,
                               "confidence": confidence, "name": item.get("name", ""),
                               "track": item.get("track", ""), "source": item,
                               "time": item.get("primary_time") if field == "primary_deadline" else None})
    for entry in data["resources"]:
        if entry.get("state", "active") != "active" or not entry.get("separate_action"):
            continue
        due = as_date(entry.get("deadline"))
        if due:
            result.append({"date": due, "days": (due - today).days, "kind": "Resource",
                           "confidence": entry.get("confidence", "tbd"),
                           "name": entry.get("item_name", ""), "track": entry.get("name", ""),
                           "source": entry, "time": None})
    priority = {"high": 0, "medium": 1, "low": 2}
    kind_order = {"Target": 0, "Primary": 1, "Secondary": 2, "Resource": 3}
    return sorted(result, key=lambda event: (event["date"],
                                             priority.get(event["source"].get("priority"), 3),
                                             kind_order.get(event["kind"], 4), event["name"]))


def upcoming(data, days, today=None):
    return [event for event in events(data, today) if 0 <= event["days"] <= days]


def alerts(data, today=None):
    return [event for event in events(data, today) if event["days"] in ALERT_DAYS]


def month_groups(data):
    groups = {}
    for item in active_items(data):
        due = as_date(item.get("primary_deadline"))
        key = due.strftime("%B %Y") if due else "Date to confirm"
        groups.setdefault(key, []).append(item)
    return sorted(groups.items(), key=lambda pair: (pair[0] == "Date to confirm",
                                                    as_date(pair[1][0].get("primary_deadline")) or date.max))
