#!/usr/bin/env python3
"""Set Confluence page width to full/wide for every replica page.

Confluence Cloud stores the editor "Fixed vs Full width" toggle as two content
properties (NOT page body, and NOT exposed by the Atlassian MCP):
  - content-appearance-published  -> controls the rendered/published view
  - content-appearance-draft      -> controls the editor default
Setting both to "full-width" makes the page wide; "fixed" reverts it.

This script reads the page ids from sync_state.json and PUT/POSTs those
properties via the Confluence REST v1 API using Basic auth.

Credentials come from the environment (never hard-code / never commit):
  CONFLUENCE_EMAIL      Atlassian account email
  CONFLUENCE_API_TOKEN  API token from id.atlassian.com/manage-profile/security/api-tokens
Optional:
  CONFLUENCE_BASE_URL   default https://ciscoteams.atlassian.net/wiki
  PAGE_WIDTH            full-width (default) | fixed

Usage:
  export CONFLUENCE_EMAIL='you@cisco.com'
  export CONFLUENCE_API_TOKEN='xxxx'
  python3 set_page_width.py            # apply to all pages in sync_state.json
  python3 set_page_width.py <id> ...   # apply to specific page id(s) only
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "sync_state.json")
BASE = os.environ.get("CONFLUENCE_BASE_URL", "https://ciscoteams.atlassian.net/wiki").rstrip("/")
WIDTH = os.environ.get("PAGE_WIDTH", "full-width")
PROP_KEYS = ("content-appearance-published", "content-appearance-draft")


def _auth_header():
    email = os.environ.get("CONFLUENCE_EMAIL")
    token = os.environ.get("CONFLUENCE_API_TOKEN")
    if not email or not token:
        sys.stderr.write(
            "ERROR: set CONFLUENCE_EMAIL and CONFLUENCE_API_TOKEN in the env.\n"
        )
        sys.exit(2)
    raw = (email + ":" + token).encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def _req(method, url, auth, payload=None):
    data = None
    headers = {"Authorization": auth, "Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, (json.loads(body) if body else {})
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        return e.code, body


def _get_prop_version(page_id, key, auth):
    url = BASE + "/rest/api/content/" + page_id + "/property/" + key
    status, data = _req("GET", url, auth)
    if status == 200 and isinstance(data, dict):
        return data.get("version", {}).get("number")
    return None  # property does not exist yet


def set_width(page_id, auth):
    results = []
    for key in PROP_KEYS:
        cur = _get_prop_version(page_id, key, auth)
        url = BASE + "/rest/api/content/" + page_id + "/property/" + key
        if cur is None:
            status, data = _req("POST",
                                BASE + "/rest/api/content/" + page_id + "/property",
                                auth, {"key": key, "value": WIDTH})
        else:
            status, data = _req("PUT", url, auth,
                                {"value": WIDTH, "version": {"number": cur + 1}})
        ok = status in (200, 201)
        results.append((key, status, ok))
    return results


def _page_ids(argv):
    if argv:
        return list(argv)
    with open(STATE) as f:
        state = json.load(f)
    pages = state.get("pages", {})
    return [meta["pageId"] for meta in pages.values() if meta.get("pageId")]


def main(argv):
    auth = _auth_header()
    ids = _page_ids(argv)
    print("Setting page width = " + WIDTH + " on " + str(len(ids)) + " page(s) @ " + BASE)
    failures = 0
    for pid in ids:
        res = set_width(pid, auth)
        tag = "OK" if all(ok for _, _, ok in res) else "FAIL"
        if tag == "FAIL":
            failures += 1
        detail = ", ".join(k.split("-")[-1] + ":" + str(s) for k, s, _ in res)
        print("  [" + tag + "] " + pid + "  (" + detail + ")")
    print("Done. " + str(len(ids) - failures) + "/" + str(len(ids)) + " pages updated.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
