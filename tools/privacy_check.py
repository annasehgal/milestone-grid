"""Scan public files using terms stored only in an ignored local file."""

import argparse
from pathlib import Path
import re
import subprocess


def git_paths(include_untracked=False):
    commands = [["git", "ls-files", "-z"]]
    if include_untracked:
        commands.append(["git", "ls-files", "--others", "--exclude-standard", "-z"])
    paths = []
    for command in commands:
        result = subprocess.run(command, check=True, capture_output=True)
        paths.extend(Path(part.decode("utf-8")) for part in result.stdout.split(b"\0") if part)
    return sorted(set(paths))


def scan(paths, terms):
    matches = []
    pattern = re.compile(r"(?<![A-Za-z])(?:" + "|".join(re.escape(term) for term in terms) + r")(?![A-Za-z])", re.IGNORECASE)
    for path in paths:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(lines, 1):
            if pattern.search(line):
                matches.append((path, number))
    return matches


def main():
    parser = argparse.ArgumentParser(description="Check public files against a local term list")
    parser.add_argument("--include-untracked", action="store_true")
    args = parser.parse_args()
    source = Path("private/privacy_terms.local.txt")
    if not source.exists():
        print(f"Local term list missing: {source}")
        return 2
    terms = [line.strip().casefold() for line in source.read_text(encoding="utf-8").splitlines()
             if line.strip() and not line.lstrip().startswith("#")]
    if not terms:
        print("Local term list is empty")
        return 2
    paths = git_paths(args.include_untracked)
    matches = scan(paths, terms)
    for path, number in matches:
        print(f"Match: {path}:{number}")
    print(f"Checked {len(paths)} files; {len(matches)} matching lines")
    return 1 if matches else 0


if __name__ == "__main__":
    raise SystemExit(main())
