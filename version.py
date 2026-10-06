#!/usr/bin/env python3
"""Bump the SDK version, commit the changed files, and create a release tag."""

import argparse
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parent
FIELDS = (('src/lara_sdk/__init__.py', '(?m)^(?P<before>__version__\\s*=\\s*[\'\\"])(?P<version>\\d+\\.\\d+\\.\\d+)(?P<after>[\'\\"])'),)


def fail(message):
    raise SystemExit(f"Error: {message}")


def git(*args, check=True):
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True
    )
    if check and result.returncode != 0:
        fail(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result


def check_git():
    if git("status", "--porcelain").stdout.strip():
        fail("Working tree is not clean. Commit or stash changes first.")
    if git("branch", "--show-current").stdout.strip() != "main":
        fail("Version bumps must be run on main.")


def next_version(current, part):
    major, minor, patch = map(int, current.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def plan_changes(part):
    contents = {}
    matches = []
    for relative_path, pattern in FIELDS:
        path = ROOT / relative_path
        if relative_path not in contents:
            try:
                contents[relative_path] = path.read_text(encoding="utf-8")
            except OSError as error:
                fail(f"Cannot read {relative_path}: {error}")
        found = list(re.finditer(pattern, contents[relative_path]))
        if len(found) != 1:
            fail(f"Expected one version field in {relative_path}; found {len(found)}")
        matches.append((relative_path, found[0]))

    current = matches[0][1].group("version")
    for relative_path, match in matches[1:]:
        if match.group("version") != current:
            fail(f"Version in {relative_path} differs from {current}")

    updated = next_version(current, part)
    tag = f"v{updated}"
    tag_check = git("show-ref", "--verify", "--quiet", f"refs/tags/{tag}", check=False)
    if tag_check.returncode == 0:
        fail(f"Tag {tag} already exists.")
    if tag_check.returncode != 1:
        fail(tag_check.stderr.strip() or f"Could not check whether tag {tag} exists")

    for relative_path in contents:
        file_matches = [match for name, match in matches if name == relative_path]
        content = contents[relative_path]
        for match in reversed(file_matches):
            start, end = match.span("version")
            content = content[:start] + updated + content[end:]
        contents[relative_path] = content
    return current, updated, contents


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("part", choices=("major", "minor", "patch"))
    parser.add_argument("--dry-run", action="store_true", help="show the bump without changing files or Git")
    args = parser.parse_args()

    check_git()
    current, updated, changes = plan_changes(args.part)
    if args.dry_run:
        print(f"Would bump {current} to {updated} and create tag v{updated}")
        for relative_path in changes:
            print(f"  {relative_path}")
        return

    for relative_path, content in changes.items():
        try:
            (ROOT / relative_path).write_text(content, encoding="utf-8")
        except OSError as error:
            fail(f"Cannot write {relative_path}: {error}")
    git("add", "--", *changes)
    git("commit", "-m", f"v{updated}")
    git("tag", "-a", f"v{updated}", "-m", f"v{updated}")
    print(f"Tag v{updated} created.")


if __name__ == "__main__":
    main()
