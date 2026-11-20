#!/usr/bin/env python3
"""From-file Confluence push (stdlib-only) for large kstack replica pages.

Why this exists: `updateConfluencePage` via MCP needs the ENTIRE rendered body
inlined into a tool call, so large pages (`knowledge/entries.md` ~1.3k lines,
`references/kim-mts-map.md` ~900 lines) risk silent transcription corruption.
This helper reads the rendered body FROM FILE and PUTs it via the Confluence
Cloud v2 REST API (representation=storage), so no agent transcription occurs.

Markdown -> Confluence storage (XHTML) conversion is intentionally scoped to the
constructs the kstack replica actually uses: headings, hr, GFM tables (with
code-span-aware + escaped-pipe cell splitting), fenced code (CDATA code macro),
blockquotes, nested bullet/ordered lists, paragraphs, and inline `code`/**bold**.

Creds: ~/.config/kstack/confluence.env (CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN).
Token is read at runtime, never printed, never persisted.

Usage:
  push_to_confluence.py <page_id> <title> <rendered_file> [--message MSG]
  push_to_confluence.py --render <rendered_file>        # print storage, no PUT
"""
import argparse
import base64
import html
import json
import os
import re
import ssl
import sys
import urllib.request

BASE = "https://ciscoteams.atlassian.net/wiki"
ENV_PATH = os.path.expanduser("~/.config/kstack/confluence.env")
SPACE_ID = "633077987"


def load_creds():
    env = {}
    with open(ENV_PATH) as fh:
        for line in fh:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k] = v
    return env["CONFLUENCE_EMAIL"], env["CONFLUENCE_API_TOKEN"]


def esc(s):
    """XML-escape text content: &,<,>," (NOT apostrophe, matching MCP output)."""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def inline(s):
    """Inline spans over a whole block (may contain '\\n' soft breaks).

    `code` spans are detected ACROSS newlines (newline -> space inside code) so
    multi-line code spans with pipes/parens do not corrupt; **bold** toggles;
    soft newlines outside code become <br />; other text is XML-escaped.
    """
    out = []
    i, n = 0, len(s)
    bold = False
    while i < n:
        c = s[i]
        if c == "`":
            j = s.find("`", i + 1)
            if j < 0:
                # unterminated backtick: treat rest as text
                out.append(esc(s[i:]).replace("\n", "<br />"))
                break
            code = s[i + 1:j].replace("\n", " ")
            out.append("<code>" + esc(code) + "</code>")
            i = j + 1
            continue
        if c == "*" and i + 1 < n and s[i + 1] == "*":
            out.append("</strong>" if bold else "<strong>")
            bold = not bold
            i += 2
            continue
        if c == "\n":
            out.append("<br />")
            i += 1
            continue
        out.append(esc(c))
        i += 1
    if bold:
        out.append("</strong>")
    return "".join(out)


def split_cells(line):
    """Split a GFM table row on top-level pipes (ignore pipes inside `code`
    spans and escaped \\|)."""
    cells, cur = [], []
    i, n = 0, len(line)
    code = False
    while i < n:
        c = line[i]
        if c == "`":
            code = not code
            cur.append(c)
            i += 1
            continue
        if c == "\\" and i + 1 < n and line[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if c == "|" and not code:
            cells.append("".join(cur))
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    cells.append("".join(cur))
    if cells and cells[0].strip() == "":
        cells = cells[1:]
    if cells and cells[-1].strip() == "":
        cells = cells[:-1]
    return [c.strip() for c in cells]


SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
HDR_RE = re.compile(r"^(#{1,6})\s+(.*)$")
HR_RE = re.compile(r"^-{3,}\s*$")
FENCE_RE = re.compile(r"^```")
ULI_RE = re.compile(r"^(\s*)[-*]\s+(.*)$")
OLI_RE = re.compile(r"^(\s*)(\d+)\.\s+(.*)$")


def is_table_start(lines, i):
    return (
        "|" in lines[i]
        and i + 1 < len(lines)
        and SEP_RE.match(lines[i + 1])
        and lines[i].strip() != ""
    )


def _is_block_boundary(lines, i):
    ln = lines[i]
    return (
        HDR_RE.match(ln)
        or HR_RE.match(ln)
        or FENCE_RE.match(ln)
        or ln.lstrip().startswith(">")
        or is_table_start(lines, i)
    )


def parse_list(lines, i, base_indent):
    """Parse a (possibly nested) list starting at line i. Returns (html, next_i).

    Each item gathers wrapped continuation lines (non-blank, non-list-marker,
    non-block-boundary) and any deeper-indented nested list.
    """
    items_html = []
    ordered = None
    start_num = None
    while i < len(lines):
        m_u = ULI_RE.match(lines[i])
        m_o = OLI_RE.match(lines[i])
        if not (m_u or m_o):
            break
        indent = len((m_o.group(1) if m_o else m_u.group(1)))
        if indent < base_indent:
            break
        if indent > base_indent:
            break
        if ordered is None:
            ordered = bool(m_o)
            if m_o:
                start_num = m_o.group(2)
        text_parts = [m_o.group(3) if m_o else m_u.group(2)]
        i += 1
        # gather wrapped continuation lines for this item
        while (
            i < len(lines)
            and lines[i].strip() != ""
            and not ULI_RE.match(lines[i])
            and not OLI_RE.match(lines[i])
            and not _is_block_boundary(lines, i)
        ):
            text_parts.append(lines[i].strip())
            i += 1
        # nested list (deeper indent)?
        nested_html = ""
        if i < len(lines) and (ULI_RE.match(lines[i]) or OLI_RE.match(lines[i])):
            mm = ULI_RE.match(lines[i]) or OLI_RE.match(lines[i])
            child_indent = len(mm.group(1))
            if child_indent > base_indent:
                nested_html, i = parse_list(lines, i, child_indent)
        items_html.append(
            "<li><p>" + inline("\n".join(text_parts)) + "</p>" + nested_html + "</li>"
        )
    tag = "ol" if ordered else "ul"
    open_tag = '<ol start="%s">' % start_num if (ordered and start_num) else "<%s>" % tag
    return open_tag + "".join(items_html) + "</%s>" % tag, i


def md_to_storage(md):
    lines = md.replace("\r\n", "\n").split("\n")
    out = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue
        # fenced code
        if FENCE_RE.match(line):
            i += 1
            code_lines = []
            while i < n and not FENCE_RE.match(lines[i]):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            body = "\n".join(code_lines)
            out.append(
                '<ac:structured-macro ac:name="code">'
                "<ac:plain-text-body><![CDATA[" + body + "]]></ac:plain-text-body>"
                "</ac:structured-macro>"
            )
            continue
        # heading
        m = HDR_RE.match(line)
        if m:
            lvl = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (lvl, inline(m.group(2).strip()), lvl))
            i += 1
            continue
        # hr
        if HR_RE.match(line):
            out.append("<hr />")
            i += 1
            continue
        # table
        if is_table_start(lines, i):
            header = split_cells(lines[i])
            i += 2  # header + separator
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip() != "":
                rows.append(split_cells(lines[i]))
                i += 1
            th = "".join("<th><p>%s</p></th>" % inline(c) for c in header)
            trs = ["<tr>" + th + "</tr>"]
            for r in rows:
                tds = "".join("<td><p>%s</p></td>" % inline(c) for c in r)
                trs.append("<tr>" + tds + "</tr>")
            out.append(
                '<table data-layout="default"><tbody>' + "".join(trs) + "</tbody></table>"
            )
            continue
        # blockquote
        if line.lstrip().startswith(">"):
            q = []
            while i < n and lines[i].lstrip().startswith(">"):
                q.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote><p>" + inline("\n".join(q)) + "</p></blockquote>")
            continue
        # list
        if ULI_RE.match(line) or OLI_RE.match(line):
            m0 = ULI_RE.match(line) or OLI_RE.match(line)
            indent = len(m0.group(1))
            html_frag, i = parse_list(lines, i, indent)
            out.append(html_frag)
            continue
        # paragraph (gather until blank / block boundary)
        para = []
        while i < n and lines[i].strip() != "":
            nxt = lines[i]
            if (
                HDR_RE.match(nxt)
                or HR_RE.match(nxt)
                or FENCE_RE.match(nxt)
                or nxt.lstrip().startswith(">")
                or ULI_RE.match(nxt)
                or OLI_RE.match(nxt)
                or is_table_start(lines, i)
            ):
                break
            para.append(nxt)
            i += 1
        if para:
            out.append("<p>" + inline("\n".join(para)) + "</p>")
    return "".join(out)


def api_get(page_id, email, token):
    auth = base64.b64encode(("%s:%s" % (email, token)).encode()).decode()
    url = "%s/api/v2/pages/%s?body-format=storage" % (BASE, page_id)
    req = urllib.request.Request(
        url, headers={"Authorization": "Basic %s" % auth, "Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30, context=ssl.create_default_context()) as r:
        return json.load(r)


def api_create(title, storage, parent_id, email, token):
    auth = base64.b64encode(("%s:%s" % (email, token)).encode()).decode()
    url = "%s/api/v2/pages" % BASE
    payload = {
        "spaceId": SPACE_ID,
        "status": "current",
        "title": title,
        "parentId": str(parent_id),
        "body": {"representation": "storage", "value": storage},
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": "Basic %s" % auth,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as r:
        return json.load(r)


def api_update(page_id, title, storage, version, message, email, token):
    auth = base64.b64encode(("%s:%s" % (email, token)).encode()).decode()
    url = "%s/api/v2/pages/%s" % (BASE, page_id)
    payload = {
        "id": str(page_id),
        "status": "current",
        "title": title,
        "body": {"representation": "storage", "value": storage},
        "version": {"number": version, "message": message},
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="PUT",
        headers={
            "Authorization": "Basic %s" % auth,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page_id", nargs="?")
    ap.add_argument("title", nargs="?")
    ap.add_argument("rendered_file", nargs="?")
    ap.add_argument("--message", default="Sync from kstack skill (from-file push)")
    ap.add_argument("--create", metavar="PARENT_ID", help="create under parent page id")
    ap.add_argument("--render", metavar="FILE", help="print storage for FILE and exit")
    args = ap.parse_args()

    if args.render:
        with open(args.render) as fh:
            sys.stdout.write(md_to_storage(fh.read()))
        return

    if args.create:
        if not (args.title and args.rendered_file):
            ap.error("title and rendered_file required with --create")
        email, token = load_creds()
        with open(args.rendered_file) as fh:
            storage = md_to_storage(fh.read())
        res = api_create(args.title, storage, args.create, email, token)
        print(
            "created page %s -> v%s (%s)"
            % (res.get("id"), res.get("version", {}).get("number"), res.get("title"))
        )
        return

    if not (args.page_id and args.title and args.rendered_file):
        ap.error("page_id, title, rendered_file required (or use --render or --create)")

    email, token = load_creds()
    with open(args.rendered_file) as fh:
        storage = md_to_storage(fh.read())
    cur = api_get(args.page_id, email, token)
    nextv = cur.get("version", {}).get("number", 0) + 1
    res = api_update(args.page_id, args.title, storage, nextv, args.message, email, token)
    print(
        "updated page %s -> v%s (%s)"
        % (res.get("id"), res.get("version", {}).get("number"), res.get("title"))
    )


if __name__ == "__main__":
    main()
