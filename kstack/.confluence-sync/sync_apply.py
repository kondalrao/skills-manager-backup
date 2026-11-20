#!/usr/bin/env python3
"""Apply a sync_plan.py plan to Confluence (create/update + record state).

Usage:
  cd ~/.agents/skills/kstack/.confluence-sync
  python3 sync_plan.py plan > /tmp/plan.json
  python3 sync_apply.py /tmp/plan.json [--message MSG]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SELF = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_file")
    ap.add_argument(
        "--message",
        default="Sync from kstack skill (local replica)",
    )
    args = ap.parse_args()

    plan = json.loads(Path(args.plan_file).read_text(encoding="utf-8"))
    failures = []
    created = updated = skipped = 0

    for node in plan["nodes"]:
        action = node["action"]
        if action == "skip":
            skipped += 1
            continue

        key = node["key"]
        title = node["title"]
        rendered = node["rendered_path"]
        h = node["hash"]

        if action == "create":
            parent_id = node.get("parent_page_id")
            if not parent_id:
                print("FAIL create %s: missing parent_page_id" % key, file=sys.stderr)
                failures.append(key)
                continue
            cmd = [
                "python3",
                str(SELF / "push_to_confluence.py"),
                "0",
                title,
                rendered,
                "--create",
                str(parent_id),
                "--message",
                args.message,
            ]
        elif action == "update":
            page_id = node.get("page_id")
            if not page_id:
                print("FAIL update %s: missing page_id" % key, file=sys.stderr)
                failures.append(key)
                continue
            cmd = [
                "python3",
                str(SELF / "push_to_confluence.py"),
                str(page_id),
                title,
                rendered,
                "--message",
                args.message,
            ]
        else:
            print("FAIL %s: unknown action %s" % (key, action), file=sys.stderr)
            failures.append(key)
            continue

        print("%s %s ..." % (action.upper(), key), flush=True)
        r = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        if r.returncode != 0:
            print(r.stderr or r.stdout, file=sys.stderr)
            failures.append(key)
            continue
        print(r.stdout.strip())

        new_page_id = node.get("page_id")
        if action == "create":
            # "created page 12345 -> v1 (title)"
            parts = r.stdout.strip().split()
            try:
                idx = parts.index("page")
                new_page_id = parts[idx + 1]
            except (ValueError, IndexError):
                print("FAIL record %s: could not parse new page id" % key, file=sys.stderr)
                failures.append(key)
                continue
            created += 1
        else:
            updated += 1

        rr = subprocess.run(
            ["python3", str(SELF / "sync_plan.py"), "record", key, str(new_page_id), h],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        if rr.returncode != 0:
            print(rr.stderr or rr.stdout, file=sys.stderr)
            failures.append(key)
        else:
            print(rr.stdout.strip())

    print(
        "Done: created=%d updated=%d skipped=%d failures=%d"
        % (created, updated, skipped, len(failures))
    )
    if failures:
        print("Failed keys:", ", ".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
