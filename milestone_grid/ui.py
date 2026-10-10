"""Small, neutral presentation helpers for the local dashboard."""

from html import escape

from .records import date_text, history_date, relative_text, short_date, text

STYLE = """
<style>
:root { --mg-ink:#202c29; --mg-muted:#697873; --mg-line:#e4eae7; --mg-accent:#2e6c62; --mg-surface:#fff; }
.stApp { background:#f6f8f7; color:var(--mg-ink); }
.block-container { max-width:1180px; padding-top:2rem; padding-bottom:4rem; }
section[data-testid="stSidebar"] { background:#fff; border-right:1px solid var(--mg-line); }
section[data-testid="stSidebar"] .block-container { padding-top:1.8rem; }
div[data-testid="stToolbar"] { display:none; }
h1,h2,h3,p { letter-spacing:0; }
h1 { font-size:1.75rem !important; font-weight:690 !important; margin:0 0 .3rem !important; }
h2 { font-size:1.12rem !important; font-weight:660 !important; margin:1.65rem 0 .8rem !important; }
h3 { font-size:1rem !important; font-weight:650 !important; }
.mg-brand { font-size:1.08rem; font-weight:750; color:var(--mg-ink); padding:.1rem 0 1.2rem; }
.mg-kicker { font-size:.71rem; text-transform:uppercase; font-weight:680; color:var(--mg-accent); margin-bottom:.38rem; }
.mg-page-title { font-size:1.8rem; font-weight:700; line-height:1.15; color:var(--mg-ink); margin:0; }
.mg-page-subtitle { color:var(--mg-muted); font-size:.91rem; margin-top:.42rem; }
.mg-section { display:flex; justify-content:space-between; align-items:baseline; gap:1rem; margin:1.7rem 0 .8rem; }
.mg-section-title { font-size:1.08rem; font-weight:680; color:var(--mg-ink); }
.mg-section-meta { color:var(--mg-muted); font-size:.81rem; }
.mg-stats { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.7rem; margin:1.25rem 0 1.55rem; }
.mg-stat { background:var(--mg-surface); border:1px solid var(--mg-line); border-radius:8px; padding:1rem 1.12rem; min-height:95px; }
.mg-stat-label { color:var(--mg-muted); font-size:.8rem; font-weight:540; }
.mg-stat-value { color:var(--mg-ink); font-size:1.72rem; line-height:1.15; font-weight:700; margin-top:.35rem; }
.mg-feature { background:var(--mg-surface); border:1px solid var(--mg-line); border-radius:8px; padding:1.25rem 1.4rem; display:grid; grid-template-columns:minmax(0,1fr) auto; gap:1rem; align-items:center; }
.mg-feature-date { font-size:1.28rem; font-weight:700; color:var(--mg-ink); margin:.2rem 0; }
.mg-feature-name { font-size:1rem; font-weight:640; color:var(--mg-ink); }
.mg-feature-meta { color:var(--mg-muted); font-size:.83rem; margin-top:.32rem; }
.mg-feature-count { font-size:1.18rem; font-weight:680; text-align:right; color:var(--mg-accent); }
.mg-feature-count small { display:block; font-size:.73rem; font-weight:500; color:var(--mg-muted); }
.mg-list { background:#fff; border:1px solid var(--mg-line); border-radius:8px; overflow:hidden; }
.mg-list-row { display:grid; grid-template-columns:76px minmax(0,1fr) auto; align-items:center; gap:1rem; padding:.75rem 1rem; border-top:1px solid var(--mg-line); }
.mg-list-row:first-child { border-top:0; }
.mg-date { font-size:.82rem; font-weight:690; color:var(--mg-accent); white-space:nowrap; }
.mg-name { color:var(--mg-ink); font-size:.91rem; font-weight:630; overflow-wrap:anywhere; }
.mg-meta { color:var(--mg-muted); font-size:.78rem; margin-top:.16rem; overflow-wrap:anywhere; }
.mg-tail { display:flex; align-items:center; gap:.55rem; white-space:nowrap; color:var(--mg-muted); font-size:.78rem; }
.mg-pill { display:inline-block; border-radius:4px; padding:.18rem .45rem; border:1px solid #d9e6e0; background:#f1f7f4; color:#32675a; font-size:.66rem; font-weight:680; text-transform:uppercase; vertical-align:middle; }
.mg-pill.mg-muted { color:#65736f; background:#f6f8f7; border-color:#e3e9e6; }
.mg-pill.mg-warm { color:#84663e; background:#faf6ed; border-color:#ede3d2; }
.mg-wave-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(145px,1fr)); gap:.65rem; }
.mg-wave { background:#fff; border:1px solid var(--mg-line); border-radius:8px; padding:.82rem .95rem; }
.mg-wave strong { display:block; font-size:.9rem; font-weight:660; }
.mg-wave span { display:block; font-size:.77rem; color:var(--mg-muted); margin-top:.25rem; }
.mg-group-heading { font-size:.79rem; color:var(--mg-muted); font-weight:700; text-transform:uppercase; margin:1.6rem 0 .55rem; }
.mg-day-heading { color:var(--mg-accent); font-size:.83rem; font-weight:700; margin:.95rem 0 .45rem; }
details.mg-record { background:#fff; border:1px solid var(--mg-line); border-radius:8px; margin:.38rem 0; }
details.mg-record summary { list-style:none; display:grid; grid-template-columns:minmax(0,1fr) auto; align-items:center; gap:1rem; padding:.82rem 1rem; cursor:pointer; }
details.mg-record summary::-webkit-details-marker { display:none; }
details.mg-record summary:hover { background:#fbfcfb; }
.mg-archive summary { grid-template-columns:minmax(0,1.15fr) minmax(0,1.45fr) auto !important; }
.mg-archive-reason { color:#53625d; font-size:.79rem; overflow-wrap:anywhere; }
.mg-archive-date { color:var(--mg-muted); font-size:.76rem; text-align:right; white-space:nowrap; }
.mg-detail-body { border-top:1px solid var(--mg-line); padding:.9rem 1rem 1rem; }
.mg-detail-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:.85rem; }
.mg-detail-key { color:var(--mg-muted); font-size:.71rem; }
.mg-detail-value { color:var(--mg-ink); font-size:.84rem; margin-top:.13rem; overflow-wrap:anywhere; }
.mg-note { color:#51605b; font-size:.82rem; line-height:1.52; margin-top:.8rem; white-space:pre-wrap; overflow-wrap:anywhere; }
.mg-resource-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.7rem; }
.mg-resource { background:#fff; border:1px solid var(--mg-line); border-radius:8px; padding:1rem 1.08rem; min-width:0; }
.mg-resource-title { color:var(--mg-ink); font-weight:660; font-size:.92rem; overflow-wrap:anywhere; }
.mg-resource-info { color:var(--mg-muted); font-size:.78rem; margin:.23rem 0 .7rem; }
.mg-resource-line { color:#3a4a45; font-size:.81rem; line-height:1.45; margin-top:.35rem; overflow-wrap:anywhere; }
.mg-chips { display:flex; gap:.3rem; flex-wrap:wrap; margin-top:.7rem; }
.mg-history { display:grid; grid-template-columns:75px minmax(0,1fr); gap:.9rem; border-bottom:1px solid var(--mg-line); padding:.75rem 0; }
.mg-history:last-child { border-bottom:0; }
.mg-empty { color:var(--mg-muted); font-size:.87rem; padding:1rem 0; }
.stButton button { border-radius:6px !important; font-weight:600 !important; }
div[data-testid="stDataFrame"] { border:1px solid var(--mg-line); border-radius:8px; overflow:hidden; }
div[data-testid="stExpander"] { border:1px solid var(--mg-line); border-radius:8px; background:#fff; }
@media(max-width:700px) { .block-container{padding:1.15rem .85rem 3rem;} .mg-stats{grid-template-columns:repeat(2,minmax(0,1fr));} .mg-resource-grid{grid-template-columns:1fr;} .mg-list-row{grid-template-columns:58px minmax(0,1fr); gap:.6rem;} .mg-tail{grid-column:2; justify-content:flex-start;} .mg-feature{grid-template-columns:1fr;} .mg-feature-count{text-align:left;} .mg-archive summary{grid-template-columns:minmax(0,1fr) auto !important;} .mg-archive-reason{grid-column:1/-1;} .mg-archive-date{grid-column:2;grid-row:1;} }
</style>
"""


def safe(value):
    return escape(text(value, ""), quote=True)


def pill(value, tone="muted"):
    label = safe(str(value or "TBD").replace("_", " "))
    return f'<span class="mg-pill mg-{tone}">{label}</span>'


def page_header(title, subtitle="", kicker="MILESTONE GRID"):
    return (f'<div class="mg-kicker">{safe(kicker)}</div><div class="mg-page-title">{safe(title)}</div>'
            f'<div class="mg-page-subtitle">{safe(subtitle)}</div>')


def section(title, meta=""):
    return (f'<div class="mg-section"><div class="mg-section-title">{safe(title)}</div>'
            f'<div class="mg-section-meta">{safe(meta)}</div></div>')


def stats(values):
    cards = "".join(f'<div class="mg-stat"><div class="mg-stat-label">{safe(label)}</div>'
                    f'<div class="mg-stat-value">{safe(value)}</div></div>' for label, value in values)
    return f'<div class="mg-stats">{cards}</div>'


def feature(event):
    if not event:
        return '<div class="mg-feature"><div class="mg-empty">No upcoming dates</div></div>'
    confidence = "Target" if event["kind"] == "Target" else str(event["confidence"]).replace("_", " ").title()
    return (f'<div class="mg-feature"><div><div class="mg-kicker">NEXT DEADLINE</div>'
            f'<div class="mg-feature-date">{safe(date_text(event["date"]))}</div>'
            f'<div class="mg-feature-name">{safe(event["name"])}</div>'
            f'<div class="mg-feature-meta">{safe(event["track"])} · {safe(confidence)}</div></div>'
            f'<div class="mg-feature-count">{safe(relative_text(event["date"]))}<small>remaining</small></div></div>')


def event_list(entries):
    if not entries:
        return '<div class="mg-empty">Nothing due in this window.</div>'
    rows = []
    for entry in entries:
        tone = "warm" if entry["confidence"] in ("predicted", "provisional", "tbd") else "muted"
        rows.append(f'<div class="mg-list-row"><div class="mg-date">{safe(short_date(entry["date"]))}</div>'
                    f'<div><div class="mg-name">{safe(entry["name"])}</div><div class="mg-meta">{safe(entry["track"])} · {safe(entry["kind"])}</div></div>'
                    f'<div class="mg-tail">{safe(relative_text(entry["date"]))} {pill(entry["confidence"], tone)}</div></div>')
    return '<div class="mg-list">' + "".join(rows) + '</div>'


def record(item, labels):
    fields = ((labels["primary_date"], date_text(item.get("primary_deadline"))),
              (labels["target_date"], date_text(item.get("target_deadline"))),
              (labels["secondary_date"], date_text(item.get("secondary_deadline"))),
              ("Status", text(item.get("status"))), ("Priority", text(item.get("priority"))),
              ("Confidence", text(item.get("confidence"))))
    details = "".join(f'<div><div class="mg-detail-key">{safe(key)}</div><div class="mg-detail-value">{safe(value)}</div></div>' for key, value in fields)
    note = f'<div class="mg-note">{safe(item.get("note"))}</div>' if item.get("note") else ""
    tone = "warm" if item.get("confidence") in ("predicted", "provisional", "tbd") else "muted"
    return (f'<details class="mg-record"><summary><div><div class="mg-name">{safe(item.get("name"))}</div>'
            f'<div class="mg-meta">{safe(item.get("track"))} · {safe(item.get("category"))}</div></div>'
            f'<div class="mg-tail">{pill(item.get("status"))} {pill(item.get("confidence"), tone)}</div></summary>'
            f'<div class="mg-detail-body"><div class="mg-detail-grid">{details}</div>{note}</div></details>')


def resource(entry):
    chips = []
    if entry.get("separate_action"):
        chips.append(pill("Separate action"))
    if entry.get("automatic"):
        chips.append(pill("Automatic"))
    if entry.get("referral_required"):
        chips.append(pill("Nomination"))
    if entry.get("confidence") in ("predicted", "provisional", "confirmed"):
        chips.append(pill(entry["confidence"], "warm" if entry["confidence"] != "confirmed" else "muted"))
    action = f'<div class="mg-resource-line">{safe(entry["action"])}</div>' if entry.get("action") else ""
    note = f'<details><summary class="mg-meta">Details</summary><div class="mg-note">{safe(entry["note"])}</div></details>' if entry.get("note") else ""
    summary = [date_text(entry.get("deadline")) if entry.get("deadline") else text(entry.get("predicted_window"), "Date to confirm")]
    summary.extend(str(entry[key]) for key in ("amount", "status") if entry.get(key))
    return (f'<div class="mg-resource"><div class="mg-resource-title">{safe(entry.get("name"))}</div>'
            f'<div class="mg-resource-info">{safe(entry.get("item_name"))} · {safe(entry.get("category"))}</div>'
            f'<div class="mg-resource-line"><strong>{safe(" · ".join(summary))}</strong></div>{action}'
            f'<div class="mg-chips">{"".join(chips)}</div>{note}</div>')


def history_entry(entry):
    raw = entry.get("date")
    stamp = (history_date(raw).strftime("%b %Y") if isinstance(raw, str) and len(raw) == 7 and history_date(raw)
             else short_date(raw) if raw else "—")
    return (f'<div class="mg-history"><div class="mg-date">{safe(stamp)}</div>'
            f'<div><div class="mg-name">{safe(str(entry.get("type", "note")).replace("_", " ").title())}'
            f' · {safe(entry.get("name"))}</div><div class="mg-meta">{safe(entry.get("note"))}</div></div></div>')


def archive_entry(entry):
    note_parts = []
    for key, label in (("note", "Note"), ("alternative", "Alternative"),
                       ("previous_category", "Previous category"), ("restored_date", "Restored")):
        if entry.get(key):
            value = date_text(entry[key]) if key == "restored_date" else text(entry[key])
            note_parts.append(f'<div><div class="mg-detail-key">{safe(label)}</div><div class="mg-detail-value">{safe(value)}</div></div>')
    details = '<div class="mg-detail-grid">' + "".join(note_parts) + '</div>' if note_parts else ""
    end = " · ".join(part for part in (date_text(entry.get("date")) if entry.get("date") else "",
                                          "Reconsider" if entry.get("reconsiderable") else "Closed") if part)
    return (f'<details class="mg-record mg-archive"><summary>'
            f'<div><div class="mg-name">{safe(entry.get("name"))}</div><div class="mg-meta">{safe(entry.get("track"))}</div></div>'
            f'<div class="mg-archive-reason">{safe(entry.get("reason"))}</div>'
            f'<div class="mg-archive-date">{safe(end)}</div>'
            f'</summary><div class="mg-detail-body">{details}</div></details>')
