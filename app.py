"""Local milestone dashboard."""

from datetime import date
from html import escape

import streamlit as st

from milestone_grid.calendar_export import save_calendar
from milestone_grid.loader import DEFAULT_PRIVATE, load_tracker, save_tracker
from milestone_grid.records import active_items, as_date, date_text, history_date, iso, short_date, sorted_items, text
from milestone_grid.resources import grouped
from milestone_grid.timeline import alerts, event_label, events, month_groups, upcoming
from milestone_grid.ui import STYLE, archive_entry, event_list, feature, history_entry, page_header, pill, record, resource, safe, section, stats
from milestone_grid.validation import coverage, validate

st.set_page_config(page_title="milestone-grid", layout="wide", initial_sidebar_state="auto")
data, source = load_tracker()
labels = data["labels"]
editable = source.resolve() == DEFAULT_PRIVATE.resolve()
st.markdown(STYLE, unsafe_allow_html=True)

nav = ["Overview", "Timeline", labels["resources"], "History", "Decisions", "Settings"]
st.sidebar.markdown('<div class="mg-brand">milestone-grid</div>', unsafe_allow_html=True)
page = st.sidebar.radio("Workspace", nav, label_visibility="collapsed", key="page")
st.sidebar.divider()
st.sidebar.caption(f"{text(data.get('settings', {}).get('cycle'), 'Local workspace')}")
st.sidebar.caption("Private workspace" if editable else "Example workspace")


def html(markup):
    st.markdown(markup, unsafe_allow_html=True)


def table(rows):
    if rows:
        st.dataframe(rows, hide_index=True, width="stretch")
    else:
        st.caption("No records yet.")


def title(name, detail=""):
    html(page_header(name, detail))


def go_to_month(month):
    st.session_state["timeline_month"] = month
    st.session_state["page"] = "Timeline"


def attention_rows():
    rows = []
    for entry in alerts(data):
        rows.append({"name": entry["name"],
                     "track": f"{entry['kind']} · {event_label(entry['confidence'])} · {entry['days']} days"})
    for warning in validate(data):
        rows.append({"name": "Review record", "track": warning})
    for item in active_items(data):
        if item.get("confidence") in ("predicted", "provisional", "tbd") or item.get("verification_status"):
            note = item.get("verification_status") or f"{text(item.get('confidence')).title()} date needs review"
            rows.append({"name": item.get("name"), "track": note})
    for entry in data["resources"]:
        if entry.get("state", "active") == "active" and entry.get("separate_action") and entry.get("confidence") in ("predicted", "provisional", "tbd"):
            rows.append({"name": entry.get("name"), "track": "Action date needs confirmation"})
    return rows


def show_overview():
    title("Overview", date.today().strftime("%A, %B %-d"))
    current = active_items(data)
    future = [entry for entry in events(data) if entry["days"] >= 0]
    html(stats([("Active", len(current)), ("Upcoming 30 days", len(upcoming(data, 30))),
                ("Completed", len(data["completed"])), ("Archived", len(data["archive"]))]))
    html(feature(future[0] if future else None))
    html(section("Next up", "Next five dates"))
    html(event_list(future[:5]))
    html(section("Current workload", "Select a month to open the timeline"))
    groups = month_groups(data)
    if groups:
        for start in range(0, len(groups), 4):
            cols = st.columns(min(4, len(groups) - start))
            for column, (month, items) in zip(cols, groups[start:start + 4]):
                with column:
                    st.button(f"{month}\n{len(items)} items", key=f"month_{month}", width="stretch",
                              on_click=go_to_month, args=(month,))
    else:
        st.caption("No active items yet.")
    rows = attention_rows()
    html(section("Attention needed", f"{len(rows)} items"))
    if rows:
        body = "".join(f'<div class="mg-list-row"><div class="mg-date">VERIFY</div>'
                       f'<div><div class="mg-name">{safe(row["name"])}</div>'
                       f'<div class="mg-meta">{safe(row["track"])}</div></div><div></div></div>' for row in rows[:5])
        html(f'<div class="mg-list">{body}</div>')
        if len(rows) > 5:
            st.caption(f"{len(rows) - 5} more in Settings")
    else:
        st.caption("Nothing needs review right now.")


def item_table(items):
    rows = []
    for item in items:
        rows.append({"Date": date_text(item.get("primary_deadline")), labels["primary_entity"]: item.get("name"),
                     labels["secondary_entity"]: item.get("track"), "Status": text(item.get("status")),
                     "Target": date_text(item.get("target_deadline")), "Confidence": text(item.get("confidence"))})
    table(rows)


def edit_item():
    if not editable or not data["items"]:
        return
    with st.expander("Update a record"):
        index = st.selectbox(labels["primary_entity"], range(len(data["items"])),
                             format_func=lambda i: f"{data['items'][i].get('name')} · {data['items'][i].get('track')}")
        item = data["items"][index]
        states = ["active", "done", "archived"]
        levels = ["high", "medium", "low"]
        confidences = ["confirmed", "provisional", "predicted", "tbd"]
        with st.form("item_form"):
            cols = st.columns(3)
            state = cols[0].selectbox("State", states, index=states.index(item.get("state", "active")))
            priority = cols[1].selectbox("Priority", levels, index=levels.index(item.get("priority", "medium")))
            confidence = cols[2].selectbox("Confidence", confidences, index=confidences.index(item.get("confidence", "tbd")))
            status = st.text_input("Status", value=text(item.get("status"), ""))
            cols = st.columns(3)
            primary = cols[0].text_input(labels["primary_date"], value=iso(item.get("primary_deadline")), placeholder="YYYY-MM-DD")
            target = cols[1].text_input(labels["target_date"], value=iso(item.get("target_deadline")), placeholder="YYYY-MM-DD")
            secondary = cols[2].text_input(labels["secondary_date"], value=iso(item.get("secondary_deadline")), placeholder="YYYY-MM-DD")
            note = st.text_area("Note", value=text(item.get("note"), ""))
            reason = st.text_input("Archive reason", disabled=state != "archived")
            reconsiderable = st.checkbox("Reconsiderable", disabled=state != "archived")
            submitted = st.form_submit_button("Save record", type="primary")
        if submitted:
            dates = {"primary_deadline": primary.strip(), "target_deadline": target.strip(), "secondary_deadline": secondary.strip()}
            invalid = [key for key, value in dates.items() if value and (len(value) != 10 or iso(value) != value)]
            if invalid:
                st.error("Use YYYY-MM-DD for each date.")
                return
            if state == "archived" and item.get("state") != "archived" and not reason.strip():
                st.error("Add a reason before archiving.")
                return
            name = item.get("name", "Item")
            for key, value in dates.items():
                if iso(item.get(key)) != value:
                    data["history"].append({"date": date.today(), "type": "target_updated" if key == "target_deadline" else "date_updated",
                                            "name": name, "note": f"{key.replace('_', ' ').title()}: {date_text(item.get(key))} to {date_text(value)}"})
                    item[key] = value or None
            old_state = item.get("state", "active")
            if old_state != state:
                kind = "removed" if state == "archived" else "completed" if state == "done" else "restored"
                data["history"].append({"date": date.today(), "type": kind, "name": name,
                                        "note": f"State changed from {old_state} to {state}."})
                if state == "archived":
                    data["archive"].append({"name": name, "track": item.get("track"), "reason": reason.strip(),
                                            "date": date.today(), "reconsiderable": reconsiderable, "note": note})
                if state == "done":
                    data["completed"].append({"name": item.get("track") or name, "item_name": name,
                                              "date": date.today(), "status": status or "done"})
                if old_state == "archived" and state == "active":
                    for entry in data["archive"]:
                        if entry.get("name") == name and entry.get("track") == item.get("track") and not entry.get("restored_date"):
                            entry["restored_date"] = date.today()
            item.update({"state": state, "status": status, "priority": priority,
                         "confidence": confidence, "note": note})
            save_tracker(data, source)
            st.success("Saved locally")


def show_timeline():
    title("Timeline", f"{len(active_items(data))} active items")
    candidates = active_items(data, include_separate=True)
    months = [name for name, _ in month_groups(data)]
    choices = ["All months"] + months
    default_month = st.session_state.get("timeline_month", "All months")
    if default_month not in choices:
        default_month = "All months"
    filters = st.columns([1.4, 1, 1, 1])
    month = filters[0].selectbox("Month", choices, index=choices.index(default_month))
    category = filters[1].selectbox("Category", ["All"] + sorted({text(item.get("category"), "General") for item in candidates}))
    status = filters[2].selectbox("Status", ["All"] + sorted({text(item.get("status"), "Active") for item in candidates}))
    confidence = filters[3].selectbox("Confidence", ["All", "confirmed", "provisional", "predicted", "tbd"])
    include_separate = st.checkbox("Include separate items", value=False)
    items = active_items(data, include_separate=include_separate)
    items = [item for item in items if (month == "All months" or (as_date(item.get("primary_deadline")).strftime("%B %Y") if as_date(item.get("primary_deadline")) else "Date to confirm") == month)
             and (category == "All" or text(item.get("category"), "General") == category)
             and (status == "All" or text(item.get("status"), "Active") == status)
             and (confidence == "All" or item.get("confidence") == confidence)]
    items.sort(key=lambda item: (as_date(item.get("primary_deadline")) or date.max, item.get("name", "")))
    by_month = {}
    for item in items:
        due = as_date(item.get("primary_deadline"))
        key = due.strftime("%B %Y") if due else "Date to confirm"
        by_month.setdefault(key, {}).setdefault(due, []).append(item)
    if not items:
        st.info("No items match these filters.")
    for group_name, dates in by_month.items():
        html(f'<div class="mg-group-heading">{safe(group_name)}</div>')
        for due, entries in dates.items():
            html(f'<div class="mg-day-heading">{safe(short_date(due))} · {len(entries)}</div>')
            for item in entries:
                html(record(item, labels))
    with st.expander("Table view"):
        item_table(items)
    edit_item()


def edit_resource():
    if not editable or not data["resources"]:
        return
    with st.expander("Update a resource"):
        index = st.selectbox("Resource", range(len(data["resources"])),
                             format_func=lambda i: f"{data['resources'][i].get('item_name')} · {data['resources'][i].get('name')}")
        entry = data["resources"][index]
        states = ["active", "done", "unavailable"]
        confidences = ["confirmed", "provisional", "predicted", "tbd", "not_applicable"]
        with st.form("resource_form"):
            cols = st.columns(2)
            state = cols[0].selectbox("State", states, index=states.index(entry.get("state", "active")))
            confidence = cols[1].selectbox("Confidence", confidences, index=confidences.index(entry.get("confidence", "tbd")))
            status = st.text_input("Status", value=text(entry.get("status"), ""))
            deadline = st.text_input("Deadline", value=iso(entry.get("deadline")), placeholder="YYYY-MM-DD")
            action = st.text_input("Action", value=text(entry.get("action"), ""))
            note = st.text_area("Note", value=text(entry.get("note"), ""))
            submitted = st.form_submit_button("Save resource", type="primary")
        if submitted:
            if deadline and (len(deadline) != 10 or iso(deadline) != deadline):
                st.error("Use YYYY-MM-DD for the date.")
                return
            if entry.get("state", "active") != "done" and state == "done":
                data["completed"].append({"name": entry.get("name"), "item_name": entry.get("item_name"),
                                          "date": date.today(), "status": status or "done"})
            if any(entry.get(key) != value for key, value in (("state", state), ("status", status), ("confidence", confidence))) or iso(entry.get("deadline")) != deadline:
                data["history"].append({"date": date.today(), "type": "resource_updated", "name": entry.get("name"),
                                        "note": f"Status: {status}; date: {date_text(deadline)}."})
            entry.update({"state": state, "status": status, "confidence": confidence,
                          "deadline": deadline or None, "action": action, "note": note})
            save_tracker(data, source)
            st.success("Saved locally")


def show_resources():
    title(labels["resources"], f"{len(data['resources'])} records")
    groups = grouped(data)
    tabs = st.tabs([f"{name} · {len(entries)}" for name, entries in groups.items()])
    for tab, (name, entries) in zip(tabs, groups.items()):
        with tab:
            if entries:
                html('<div class="mg-resource-grid">' + "".join(resource(entry) for entry in entries) + '</div>')
            else:
                st.caption("Nothing here right now.")
    edit_resource()


def show_history():
    title("History", "Completed work, prior decisions, and changes")
    html(section("Completed", f"{len(data['completed'])} record{'s' if len(data['completed']) != 1 else ''}"))
    completed = sorted(data["completed"], key=lambda row: as_date(row.get("date")) or date.min, reverse=True)
    if completed:
        body = "".join(f'<div class="mg-list-row"><div class="mg-date">{safe(short_date(row.get("date")))}</div>'
                       f'<div><div class="mg-name">{safe(row.get("name"))}</div><div class="mg-meta">{safe(row.get("item_name"))}</div></div>'
                       f'<div class="mg-tail">{pill(row.get("status", "done"))}</div></div>' for row in completed)
        html(f'<div class="mg-list">{body}</div>')
    else:
        st.caption("Nothing completed yet.")
    html(section("Archived", f"{len(data['archive'])} record{'s' if len(data['archive']) != 1 else ''}"))
    if data["archive"]:
        for entry in data["archive"]:
            html(archive_entry(entry))
    else:
        st.caption("No archived records.")
    html(section("Change log", f"{len(data['history'])} changes"))
    history = sorted(data["history"], key=lambda row: history_date(row.get("date")) or date.min, reverse=True)
    if history:
        html("".join(history_entry(entry) for entry in history))
    else:
        st.caption("No changes recorded yet.")
    with st.expander("Date coverage audit"):
        report = coverage(data)
        st.write(f"{report['covered']} / {report['total']} active items have a date record")
        if report["missing"]:
            st.warning("Missing: " + ", ".join(report["missing"]))
        metrics = st.columns(4)
        for col, (name, value) in zip(metrics, (("Secondary dates", report["secondary"]), ("Targets", report["targets"]),
                                                ("Resource targets", report["resource_targets"]), ("Separate actions", report["separate_actions"]))):
            col.metric(name, value)
        table([{labels["primary_entity"]: item.get("name"), labels["secondary_entity"]: item.get("track"),
                labels["primary_date"]: date_text(item.get("primary_deadline")),
                labels["target_date"]: date_text(item.get("target_deadline")),
                labels["secondary_date"]: date_text(item.get("secondary_deadline")),
                "Resource target": date_text(item.get("resource_target")),
                "Confidence": text(item.get("confidence")), "Last verified": date_text(item.get("last_verified")),
                "Verification": text(item.get("verification_status")), "Note": text(item.get("note"))}
               for item in sorted_items(data)])
        table([{labels["primary_entity"]: row.get("item_name"), "Resource": row.get("name"),
                "Deadline": date_text(row.get("deadline")), "Referral window": text(row.get("referral_window")),
                "Prior cycle": date_text(row.get("prior_cycle_date")), "Predicted window": text(row.get("predicted_window")),
                "Confidence": text(row.get("confidence")), "Status": text(row.get("status"))} for row in data["resources"]])


def show_decisions():
    title("Decisions", f"{len(data['decisions'])} comparisons")
    fields = (("result", "Result"), ("base_cost", "Base cost"), ("support", "Support"),
              ("net_cost", "Net cost"), ("duration", "Duration"), ("location", "Location"),
              ("key_feature", "Key feature"), ("decision_date", "Decision date"), ("note", "Notes"))
    if data["decisions"]:
        rows = []
        for entry in data["decisions"]:
            row = {labels["primary_entity"]: entry.get("name")}
            row.update({title: date_text(entry.get(key)) if key == "decision_date" else text(entry.get(key)) for key, title in fields})
            rows.append(row)
        table(rows)
    else:
        html('<div class="mg-empty">No comparisons recorded yet.</div>')
    if not editable or not active_items(data):
        return
    with st.expander("Update comparison"):
        names = [item.get("name") for item in active_items(data)]
        name = st.selectbox(labels["primary_entity"], names)
        existing = next((row for row in data["decisions"] if row.get("name") == name), {"name": name})
        with st.form("decision_form"):
            values = {}
            for key, label in fields:
                values[key] = st.text_input(label, value=iso(existing.get(key)) if key == "decision_date" else text(existing.get(key), ""))
            submitted = st.form_submit_button("Save comparison", type="primary")
        if submitted:
            if values["decision_date"] and (len(values["decision_date"]) != 10 or iso(values["decision_date"]) != values["decision_date"]):
                st.error("Use YYYY-MM-DD for the decision date.")
                return
            if existing not in data["decisions"]:
                data["decisions"].append(existing)
            existing.update(values)
            data["history"].append({"date": date.today(), "type": "decision_updated", "name": name,
                                    "note": "Comparison updated."})
            save_tracker(data, source)
            st.success("Saved locally")


def show_settings():
    title("Settings", "Workspace health and local exports")
    report = coverage(data)
    html(stats([("Date coverage", f"{report['covered']} / {report['total']}"),
                ("Targets", report["targets"]), ("Separate actions", report["separate_actions"]),
                ("Referrals", report["referrals"])]))
    if report["expected"] is not None and report["total"] != report["expected"]:
        st.warning(f"Expected {report['expected']} active items; found {report['total']}.")
    warnings = validate(data)
    html(section("Validation", f"{len(warnings)} notices"))
    if warnings:
        for warning in warnings:
            st.warning(warning)
    else:
        st.caption("All current checks pass.")
    html(section("Calendar export"))
    reminders = st.multiselect("Remind me before each date", [30, 14, 7, 3, 1], default=[7, 1],
                               format_func=lambda days: f"{days} days")
    st.caption(f"{len(events(data))} current events · local time zone: {text(data['settings'].get('timezone'), 'UTC')}")
    if st.button("Export calendar", type="primary"):
        path = save_calendar(data, reminders)
        st.success(f"Saved to {path}")
        st.download_button("Download calendar", path.read_bytes(), file_name=path.name, mime="text/calendar")
    html(section("Local workspace"))
    st.caption(f"Source: {source}")
    st.caption("Display labels are loaded from local settings when available.")


if page == "Overview":
    show_overview()
elif page == "Timeline":
    show_timeline()
elif page == labels["resources"]:
    show_resources()
elif page == "History":
    show_history()
elif page == "Decisions":
    show_decisions()
else:
    show_settings()
