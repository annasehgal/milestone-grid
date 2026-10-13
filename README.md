# milestone-grid

## Demo: [View Live](https://arkive-2hhjguyfufwtyqzteafgaf.streamlit.app/)

`milestone-grid` is a local-first dashboard for tracking milestones, deadlines, resources, decisions, and historical changes.

It includes timeline views, date grouping, private YAML records, calendar export, a historical archive, resource and action tracking, and a decision comparison view. It runs on your machine without an account or database.

## Run

Use Python 3.12 or newer, then run `./run.sh`. The script creates `.venv`, installs dependencies when needed, and starts the dashboard on `127.0.0.1`. After installation, the dashboard works offline.

The app reads `private/tracker.local.yaml` when it exists and otherwise opens the fictional `examples/sample.yaml`. Keep personal records and label overrides in the ignored `private/` directory. Generated calendars are written only to ignored `exports/private/`.

## Local files

- `private/tracker.local.yaml`: your records
- `private/labels.local.yaml`: optional display labels
- `private/privacy_terms.local.txt`: optional one-term-per-line audit list

Run `python3 tools/privacy_check.py --include-untracked` before publishing. The script loads terms from the ignored file and reports matches without storing those terms in public code. Run tests with `.venv/bin/python -m pytest`.
