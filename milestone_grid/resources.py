"""Resource grouping for the dashboard."""


def group(entry):
    if entry.get("state") == "unavailable":
        return "Unavailable"
    if entry.get("state") == "done":
        return "Later"
    if entry.get("separate_action"):
        return "Needs action"
    if entry.get("referral_required"):
        return "Nomination / referral"
    if entry.get("automatic"):
        return "Automatic"
    return "Later"


def grouped(data):
    names = ("Needs action", "Automatic", "Nomination / referral", "Later", "Unavailable")
    result = {name: [] for name in names}
    for entry in data["resources"]:
        result[group(entry)].append(entry)
    return result
