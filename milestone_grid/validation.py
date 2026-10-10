"""Checks that keep local plans internally consistent."""

from .records import active_items, as_date


def coverage(data):
    items = active_items(data)
    missing = [item.get("name", "Unnamed") for item in items
               if not item.get("confidence") or
               (item.get("confidence") != "tbd" and not as_date(item.get("primary_deadline")))]
    return {"total": len(items), "covered": len(items) - len(missing), "missing": missing,
            "expected": data.get("settings", {}).get("active_item_target"),
            "secondary": sum(bool(item.get("secondary_deadline")) for item in items),
            "targets": sum(bool(item.get("target_deadline")) for item in items),
            "resource_targets": sum(bool(item.get("resource_target")) for item in items),
            "separate_actions": sum(bool(entry.get("separate_action")) for entry in data["resources"]),
            "referrals": sum(bool(entry.get("referral_required")) for entry in data["resources"]),
            "completed": len(data["completed"]), "archived": len(data["archive"])}


def validate(data):
    warnings = []
    items = active_items(data)
    expected = data.get("settings", {}).get("active_item_target")
    if expected is not None and len(items) != expected:
        warnings.append(f"Expected {expected} active items; found {len(items)}")
    archived = {(entry.get("name"), entry.get("track")) for entry in data["archive"]
                if not entry.get("restored_date")}
    seen = set()
    for item in items:
        key = (item.get("name"), item.get("track"))
        name = " / ".join(str(part or "?") for part in key)
        if key in seen:
            warnings.append(f"Duplicate item: {name}")
        seen.add(key)
        if key in archived:
            warnings.append(f"Archived item is active: {name}")
        confidence = item.get("confidence")
        primary = as_date(item.get("primary_deadline"))
        target = as_date(item.get("target_deadline"))
        secondary = as_date(item.get("secondary_deadline"))
        if not confidence or (confidence != "tbd" and not primary):
            warnings.append(f"Missing primary date record: {name}")
        if confidence == "confirmed" and (item.get("predicted_window") or item.get("prediction_reason")):
            warnings.append(f"Estimate marked confirmed: {name}")
        if confidence == "predicted" and not (item.get("prior_cycle_date") and item.get("predicted_window") and item.get("prediction_reason")):
            warnings.append(f"Prediction needs prior date, window, and reason: {name}")
        if primary and target and target > primary:
            warnings.append(f"Target follows primary date: {name}")
        if primary and secondary and secondary < primary:
            warnings.append(f"Secondary date precedes primary date: {name}")
        if data.get("settings", {}).get("allow_restricted_requirements") is False and item.get("restricted_requirement"):
            warnings.append(f"Restricted item remains active: {name}")
    for entry in data["resources"]:
        if entry.get("separate_action") and entry.get("automatic"):
            warnings.append(f"Separate action also marked automatic: {entry.get('name', '?')}")
        if data.get("settings", {}).get("allow_repayable_resources") is False and entry.get("repayable"):
            warnings.append(f"Repayable resource conflicts with settings: {entry.get('name', '?')}")
    return warnings
