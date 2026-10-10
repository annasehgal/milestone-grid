"""Shared record formatting and selection."""

from datetime import date, datetime


def as_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if value:
        try:
            return date.fromisoformat(str(value)[:10])
        except ValueError:
            pass
    return None


def iso(value):
    parsed = as_date(value)
    return parsed.isoformat() if parsed else ""


def date_text(value):
    parsed = as_date(value)
    return f"{parsed:%b} {parsed.day}, {parsed.year}" if parsed else "—"


def short_date(value):
    parsed = as_date(value)
    return f"{parsed:%b} {parsed.day}" if parsed else "TBD"


def history_date(value):
    parsed = as_date(value)
    if parsed:
        return parsed
    if isinstance(value, str) and len(value) == 7:
        try:
            return date.fromisoformat(value + "-01")
        except ValueError:
            pass
    return None


def relative_text(value, today=None):
    parsed = as_date(value)
    if not parsed:
        return "Date to confirm"
    days = (parsed - (today or date.today())).days
    if days == 0:
        return "Today"
    if days == 1:
        return "Tomorrow"
    if days > 0:
        return f"{days} days"
    return f"{abs(days)} days ago"


def text(value, fallback="—"):
    return str(value) if value is not None and str(value).strip() else fallback


def active_items(data, include_separate=False):
    return [item for item in data["items"]
            if item.get("state", "active") == "active"
            and (include_separate or not item.get("separate"))]


def sorted_items(data, include_separate=False):
    return sorted(active_items(data, include_separate),
                  key=lambda item: (as_date(item.get("target_deadline"))
                                    or as_date(item.get("primary_deadline")) or date.max,
                                    item.get("name", "")))
