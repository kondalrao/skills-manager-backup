#!/usr/bin/env python3
"""Render a kstack skill file into a Confluence-ready markdown body.

Deterministic and offline (no network). Used by sync_plan.py and the runbook
in SYNC.md.

Behavior:
  * Markdown files: each fenced ```mermaid block is replaced by a pre-rendered
    ASCII diagram (from mermaid_ascii/<key>.<idx>.txt) wrapped in a plain code
    fence so Confluence renders it monospaced. Tables/code/lists pass through as
    markdown -- the Atlassian MCP (contentFormat="markdown") turns GFM tables
    into native Confluence tables. A mermaid block with no stored ASCII is
    flagged (returned in unmapped_mermaid) and rendered as a visible TODO plus
    the original mermaid source, so drift never silently ships a raw diagram.
  * Python files: wrapped in a language-tagged code fence.
  * Every page gets a one-line "auto-generated replica" header note pointing at
    the skill source of truth.

CLI:
  python md_to_confluence.py <relpath>              # JSON: relpath/title/hash/unmapped/body
  python md_to_confluence.py <relpath> --body-only  # just the rendered body text
"""

import hashlib
import json
import re
import sys
from pathlib import Path

SELF_DIR = Path(__file__).resolve().parent
SKILL_DIR = SELF_DIR.parent
ASCII_DIR = SELF_DIR / "mermaid_ascii"

# Skill source of truth as the user sees it (stable, machine-independent).
SKILL_DISPLAY_ROOT = "~/.agents/skills/kstack"

MERMAID_BLOCK = re.compile(r"^```mermaid[^\n]*\n(.*?)\n```[ \t]*$", re.DOTALL | re.MULTILINE)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _ascii_key(relpath, idx):
    return relpath.replace("/", "__") + "." + str(idx) + ".txt"


def _header_note(relpath):
    return (
        "> Auto-generated replica of `" + relpath + "`. "
        "Edit the skill source (`" + SKILL_DISPLAY_ROOT + "/" + relpath + "`), "
        "not this Confluence page. Changes appear on the next sync run.\n\n"
    )


def _replace_mermaid(relpath, text, unmapped):
    counter = {"i": 0}

    def repl(match):
        idx = counter["i"]
        counter["i"] += 1
        original = match.group(1)
        ascii_path = ASCII_DIR / _ascii_key(relpath, idx)
        if ascii_path.exists():
            art = ascii_path.read_text(encoding="utf-8").rstrip("\n")
            return (
                "_ASCII rendering (source diagram was mermaid):_\n\n"
                "```\n" + art + "\n```"
            )
        unmapped.append(relpath + "#" + str(idx))
        return (
            "> TODO: manual ASCII conversion needed for mermaid diagram #"
            + str(idx) + " (add `" + _ascii_key(relpath, idx)
            + "` under .confluence-sync/mermaid_ascii/). Original source below.\n\n"
            "```\n" + original + "\n```"
        )

    return MERMAID_BLOCK.sub(repl, text)


def render_markdown(relpath, text):
    unmapped = []
    body = _header_note(relpath) + _replace_mermaid(relpath, text, unmapped)
    return body, unmapped


def render_python(relpath, text):
    body = _header_note(relpath) + "```python\n" + text.rstrip("\n") + "\n```\n"
    return body, []


def render_file(relpath):
    src = SKILL_DIR / relpath
    text = src.read_text(encoding="utf-8")
    if relpath.endswith(".py"):
        body, unmapped = render_python(relpath, text)
    else:
        body, unmapped = render_markdown(relpath, text)
    return {
        "relpath": relpath,
        "title": relpath,
        "body": body,
        "hash": sha256_text(body),
        "unmapped_mermaid": unmapped,
    }


def main(argv):
    if not argv:
        sys.stderr.write("usage: md_to_confluence.py <relpath> [--body-only]\n")
        return 2
    relpath = argv[0]
    body_only = "--body-only" in argv[1:]
    result = render_file(relpath)
    if body_only:
        sys.stdout.write(result["body"])
    else:
        sys.stdout.write(json.dumps(result, indent=2))
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
