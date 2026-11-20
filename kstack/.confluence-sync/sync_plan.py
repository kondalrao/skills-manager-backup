#!/usr/bin/env python3
"""Plan and track the kstack-skill -> Confluence replica sync.

Deterministic and offline. The Atlassian MCP calls themselves are performed by
the agent following SYNC.md; this script decides WHAT to do and records results.

Commands:
  plan        Render every page, diff its hash against sync_state.json, write the
              rendered bodies to rendered/<key>.txt, and print a JSON plan:
                {meta, nodes:[{key,title,parent_key,source,action,hash,
                               page_id,parent_page_id,rendered_path,unmapped}],
                 orphans:[...]}
              action is one of: create | update | skip.
  body KEY    Print the rendered body for one node (what to pass to MCP).
  get KEY     Print the recorded Confluence pageId for a node (empty if none).
  record KEY PAGE_ID HASH
              Persist pageId+hash for a node into sync_state.json.

Config below (cloudId/spaceId/folderId) are non-secret Confluence identifiers.
"""

import json
import sys
from pathlib import Path

import md_to_confluence as conv

SELF_DIR = Path(__file__).resolve().parent
STATE_PATH = SELF_DIR / "sync_state.json"
RENDERED_DIR = SELF_DIR / "rendered"

CLOUD_ID = "cc5672c2-37d3-438b-9543-58ff06df6f4c"
SPACE_ID = "633077987"
FOLDER_ID = "1504677719"

ROOT_KEY = "__root__"
ROOT_TITLE = "KStack Skill (replica)"

# Ordered parents-first. Each node: (key, title, source_relpath_or_None, parent_key)
# source None  -> generated landing/index body (see _generated_body).
# parent_key None (root only) -> parent is the Confluence FOLDER_ID.
PAGE_TREE = [
    (ROOT_KEY, ROOT_TITLE, None, None),

    ("SKILL.md", "SKILL.md", "SKILL.md", ROOT_KEY),
    ("KNOWLEDGE.md", "KNOWLEDGE.md", "KNOWLEDGE.md", ROOT_KEY),
    ("USAGE_COUNTS.md", "USAGE_COUNTS.md", "USAGE_COUNTS.md", ROOT_KEY),

    ("knowledge/", "knowledge/", None, ROOT_KEY),
    ("knowledge/entries.md", "knowledge/entries.md", "knowledge/entries.md", "knowledge/"),
    ("knowledge/methods.md", "knowledge/methods.md", "knowledge/methods.md", "knowledge/"),
    ("knowledge/switch-commands.md", "knowledge/switch-commands.md", "knowledge/switch-commands.md", "knowledge/"),

    ("references/", "references/", "references/README.md", ROOT_KEY),
    ("references/catch-all.md", "references/catch-all.md", "references/catch-all.md", "references/"),
    ("references/hw-codenames-confluence-cache.md", "references/hw-codenames-confluence-cache.md", "references/hw-codenames-confluence-cache.md", "references/"),
    ("references/hw-codenames-sone.md", "references/hw-codenames-sone.md", "references/hw-codenames-sone.md", "references/"),
    ("references/ipsec.md", "references/ipsec.md", "references/ipsec.md", "references/"),
    ("references/kfib-route-sync.md", "references/kfib-route-sync.md", "references/kfib-route-sync.md", "references/"),
    ("references/kim-mts-map.md", "references/kim-mts-map.md", "references/kim-mts-map.md", "references/"),
    ("references/kim-process-arch.md", "references/kim-process-arch.md", "references/kim-process-arch.md", "references/"),
    ("references/monthly-pr-sweep.md", "references/monthly-pr-sweep.md", "references/monthly-pr-sweep.md", "references/"),
    ("references/netbroker-rtnl-trap.md", "references/netbroker-rtnl-trap.md", "references/netbroker-rtnl-trap.md", "references/"),
    ("references/psdev-init.md", "references/psdev-init.md", "references/psdev-init.md", "references/"),
    ("references/psinb-rx-sone.md", "references/psinb-rx-sone.md", "references/psinb-rx-sone.md", "references/"),
    ("references/sone-encap-tx.md", "references/sone-encap-tx.md", "references/sone-encap-tx.md", "references/"),
    ("references/vdc-ioctl-writers.md", "references/vdc-ioctl-writers.md", "references/vdc-ioctl-writers.md", "references/"),
    ("references/vdc-rx-classification-sone.md", "references/vdc-rx-classification-sone.md", "references/vdc-rx-classification-sone.md", "references/"),
    ("references/vxlan-decap-sone-rx.md", "references/vxlan-decap-sone-rx.md", "references/vxlan-decap-sone-rx.md", "references/"),

    ("architecture/", "architecture/", None, ROOT_KEY),
    ("architecture/psinb-driver-architecture.md", "architecture/psinb-driver-architecture.md", "architecture/psinb-driver-architecture.md", "architecture/"),
    ("architecture/klm-vdc-driver-architecture.md", "architecture/klm-vdc-driver-architecture.md", "architecture/klm-vdc-driver-architecture.md", "architecture/"),
    ("architecture/kim-process-architecture.md", "architecture/kim-process-architecture.md", "architecture/kim-process-architecture.md", "architecture/"),
    ("architecture/kfib-library-architecture.md", "architecture/kfib-library-architecture.md", "architecture/kfib-library-architecture.md", "architecture/"),
    ("architecture/netbroker-architecture.md", "architecture/netbroker-architecture.md", "architecture/netbroker-architecture.md", "architecture/"),

    ("scripts/", "scripts/", "scripts/README.md", ROOT_KEY),
    ("scripts/trap_code.py", "scripts/trap_code.py", "scripts/trap_code.py", "scripts/"),
    ("scripts/group_by_packet.py", "scripts/group_by_packet.py", "scripts/group_by_packet.py", "scripts/"),
]

NODE_BY_KEY = {n[0]: n for n in PAGE_TREE}


def _children(parent_key):
    return [n for n in PAGE_TREE if n[3] == parent_key]


def _generated_body(key, title):
    if key == ROOT_KEY:
        lines = [
            "> Auto-generated replica of the **kstack** skill "
            "(`" + conv.SKILL_DISPLAY_ROOT + "`). Edit the skill source, not "
            "these Confluence pages. Changes appear on the next sync run.",
            "",
            "This page tree mirrors the on-disk skill layout. Markdown tables are "
            "rendered as native Confluence tables; mermaid diagrams are rendered "
            "as ASCII.",
            "",
            "## Sections",
            "",
        ]
    else:
        lines = [
            "> Auto-generated index for `" + key + "` in the **kstack** skill. "
            "Edit the skill source, not this page.",
            "",
            "## Pages",
            "",
        ]
    for child in _children(key):
        # Backtick child names so the markdown parser does not auto-link bare
        # "name.md" tokens as URLs.
        lines.append("- `" + child[1] + "`")
    return "\n".join(lines) + "\n"


def _render_node(key):
    node = NODE_BY_KEY[key]
    _k, title, source, _parent = node
    if source is None:
        body = _generated_body(key, title)
        unmapped = []
    else:
        r = conv.render_file(source)
        body = r["body"]
        unmapped = r["unmapped_mermaid"]
    return body, conv.sha256_text(body), unmapped


def _safe(key):
    return key.replace("/", "__") or "root"


def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"pages": {}}


def save_state(state):
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cmd_plan():
    state = load_state()
    pages = state.get("pages", {})
    RENDERED_DIR.mkdir(exist_ok=True)
    nodes = []
    for key, title, source, parent_key in PAGE_TREE:
        body, h, unmapped = _render_node(key)
        rendered_path = RENDERED_DIR / (_safe(key) + ".txt")
        rendered_path.write_text(body, encoding="utf-8")
        rec = pages.get(key, {})
        page_id = rec.get("pageId")
        if not page_id:
            action = "create"
        elif rec.get("hash") != h:
            action = "update"
        else:
            action = "skip"
        parent_page_id = FOLDER_ID if parent_key is None else pages.get(parent_key, {}).get("pageId")
        nodes.append({
            "key": key,
            "title": title,
            "parent_key": parent_key,
            "source": source,
            "action": action,
            "hash": h,
            "page_id": page_id,
            "parent_page_id": parent_page_id,
            "rendered_path": str(rendered_path),
            "unmapped": unmapped,
        })
    orphans = [k for k in pages.keys() if k not in NODE_BY_KEY]
    out = {
        "meta": {"cloudId": CLOUD_ID, "spaceId": SPACE_ID, "folderId": FOLDER_ID},
        "nodes": nodes,
        "orphans": orphans,
    }
    sys.stdout.write(json.dumps(out, indent=2) + "\n")
    return 0


def cmd_body(key):
    if key not in NODE_BY_KEY:
        sys.stderr.write("unknown key: " + key + "\n")
        return 2
    body, _h, _u = _render_node(key)
    sys.stdout.write(body)
    return 0


def cmd_get(key):
    state = load_state()
    rec = state.get("pages", {}).get(key, {})
    sys.stdout.write((rec.get("pageId") or "") + "\n")
    return 0


def cmd_record(key, page_id, h):
    if key not in NODE_BY_KEY:
        sys.stderr.write("unknown key: " + key + "\n")
        return 2
    state = load_state()
    state.setdefault("pages", {})[key] = {
        "title": NODE_BY_KEY[key][1],
        "pageId": page_id,
        "hash": h,
    }
    save_state(state)
    sys.stdout.write("recorded " + key + " -> " + page_id + "\n")
    return 0


def main(argv):
    if not argv:
        sys.stderr.write(__doc__)
        return 2
    cmd = argv[0]
    if cmd == "plan":
        return cmd_plan()
    if cmd == "body" and len(argv) == 2:
        return cmd_body(argv[1])
    if cmd == "get" and len(argv) == 2:
        return cmd_get(argv[1])
    if cmd == "record" and len(argv) == 4:
        return cmd_record(argv[1], argv[2], argv[3])
    sys.stderr.write("bad args; see --help / docstring\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
