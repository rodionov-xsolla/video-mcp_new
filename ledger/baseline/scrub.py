#!/usr/bin/env python3
"""Scrub an n8n workflow or execution export so it can be committed and diffed.

Stdlib only (Python 3.9+). The same input always gives the same output, so a
re-export scrubbed with this script can be diffed against the committed
baseline to prove a production workflow was not changed.

Usage:
    python3 scrub.py IN.json OUT.json      scrub one export
    python3 scrub.py --check FILE.json...  report leftover secret-looking
                                           strings (paths and counts only,
                                           never the values); exit 1 if any

Accepted input shapes:
    - the n8n connector's get_workflow_details output  {"workflow": {...}, ...}
    - the n8n public API  GET /api/v1/workflows/{id}    {...workflow...}
    - the n8n public API  GET /api/v1/executions/{id}?includeData=true

What it does:
    - keeps only the workflow fields that describe behaviour (see KEEP_KEYS)
    - header and query parameter values -> "<redacted>" (names are kept)
    - raw JSON header/query blocks -> "<redacted>"
    - literal query-string values inside URLs -> "<redacted>"
    - credential references -> {"name": ...} only (ids dropped)
    - values under secret-looking keys (token, apiKey, password, ...) -> "<redacted>"
    - JWTs, sk-/sb_ keys, Bearer tokens, Google keys, Telegram bot tokens,
      long hex/alphanumeric blobs anywhere in any string -> "<redacted>"
    - inline base64 data: URLs -> "data:<mime>;base64,<redacted>"
    - pinData and staticData contents -> "<redacted>"
    - nodes sorted by name, keys sorted, 2-space indent, trailing newline

Not handled: personal data inside executions (post text, Telegram user ids,
moderator names). Fixtures need that blanked too before they are committed.

The n8n connector's get_workflow_details output carries no node credentials,
so a connector export has no credential names; an API export keeps the names.
"""
import json
import re
import sys

R = "<redacted>"

KEEP_KEYS = (
    "id", "name", "active", "isArchived", "versionId", "createdAt", "updatedAt",
    "settings", "nodes", "connections", "tags", "staticData", "pinData",
    # executions
    "workflowId", "mode", "status", "finished", "startedAt", "stoppedAt",
    "retryOf", "retrySuccessId", "waitTill", "data", "workflowData",
)

SECRET_KEY_RE = re.compile(
    r"^(password|passwd|secret|client_?secret|token|access_?token|refresh_?token|"
    r"api_?key|apikey|x-api-key|authorization|bearer|service_?role_?key|"
    r"private_?key|session_?token)$",
    re.I,
)

# Order matters: specific patterns first.
SECRET_PATTERNS = [
    # inline base64 media (image-model responses in executions): bulk, not secret,
    # collapsed first so the blob patterns below don't cut it into pieces
    (re.compile(r"data:([a-zA-Z]+/[a-zA-Z0-9.+-]+);base64,[A-Za-z0-9+/=]{100,}"),
     r"data:\1;base64," + R),
    # JWTs (Supabase anon/service keys and similar)
    (re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"), R),
    # OpenRouter / OpenAI-style and Supabase new-style keys
    (re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"), R),
    (re.compile(r"\bsb_(secret|publishable)_[A-Za-z0-9_-]{10,}"), R),
    # GitHub, Slack tokens
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), R),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"), R),
    # Google API keys
    (re.compile(r"\bAIza[0-9A-Za-z_-]{30,}"), R),
    # Telegram bot tokens, also glued to "bot" in api.telegram.org/bot<token>/ URLs
    # (no \b: "bot123..." has no word boundary before the digits)
    (re.compile(r"(?<![0-9])\d{8,11}:[A-Za-z0-9_-]{30,}"), R),
    # Bearer / Basic credentials written out
    (re.compile(r"(?i)\b(Bearer|Basic)\s+(?!\{\{)[A-Za-z0-9._~+/=-]{12,}"), r"\1 " + R),
    # key: "value" / key=value assignments in code and bodies
    (re.compile(
        r"(?i)((?:api[_-]?key|apikey|access[_-]?token|auth[_-]?token|token|secret|"
        r"password|passwd|authorization|service[_-]?role[_-]?key)"
        r"[\"']?\s*[:=]\s*[\"'])(?!\{\{|<redacted>)([^\"'\s]{8,})([\"'])"),
     r"\1" + R + r"\3"),
    # long hex blobs (API tokens); UUIDs have dashes and are kept
    (re.compile(r"\b[a-fA-F0-9]{32,}\b"), R),
    # long alphanumeric blobs with mixed case and digits
    (re.compile(r"\b(?=[A-Za-z0-9]*[0-9])(?=[A-Za-z0-9]*[a-z])(?=[A-Za-z0-9]*[A-Z])[A-Za-z0-9]{40,}\b"), R),
]

URL_QUERY_RE = re.compile(r"(https?://[^\s\"'?#]+\?)([^\s\"'#]+)")


def scrub_string(s):
    for pat, repl in SECRET_PATTERNS:
        s = pat.sub(repl, s)

    def _q(m):
        pairs = []
        for part in m.group(2).split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                pairs.append(k + "=" + (v if "{{" in v or v == R else R))
            else:
                pairs.append(part)
        return m.group(1) + "&".join(pairs)

    return URL_QUERY_RE.sub(_q, s)


def redact_param_list(block):
    """n8n {parameters: [{name, value}]} blocks: keep names, drop values."""
    if isinstance(block, dict) and isinstance(block.get("parameters"), list):
        out = []
        for p in block["parameters"]:
            if isinstance(p, dict):
                q = dict(p)
                if "value" in q:
                    q["value"] = R
                out.append(q)
            else:
                out.append(R)
        b = dict(block)
        b["parameters"] = out
        return b
    return R if block not in (None, "", {}, []) else block


def scrub_node_parameters(params):
    if not isinstance(params, dict):
        return params
    p = dict(params)
    for k in ("headerParameters", "queryParameters"):
        if k in p:
            p[k] = redact_param_list(p[k])
    for k in ("jsonHeaders", "headers", "jsonQuery", "queryParametersJson",
              "headerParametersJson"):
        if k in p and p[k] not in (None, "", {}, []):
            p[k] = R
    if isinstance(p.get("options"), dict):
        o = dict(p["options"])
        for k in ("headers", "queryParameters"):
            if k in o:
                o[k] = redact_param_list(o[k]) if isinstance(o[k], dict) else R
        p["options"] = o
    return p


def scrub_credentials(creds):
    if not isinstance(creds, dict):
        return creds
    out = {}
    for ctype, ref in creds.items():
        if isinstance(ref, dict):
            out[ctype] = {"name": ref.get("name")}
        else:
            out[ctype] = {"name": None}
    return out


def walk(obj, key=None):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(v, str) and SECRET_KEY_RE.match(str(k)) and v and "{{" not in v:
                out[k] = R
            elif k == "credentials" and isinstance(v, dict):
                out[k] = scrub_credentials(v)
            elif k == "parameters" and isinstance(v, dict):
                out[k] = walk(scrub_node_parameters(v), k)
            else:
                out[k] = walk(v, k)
        return out
    if isinstance(obj, list):
        return [walk(v, key) for v in obj]
    if isinstance(obj, str):
        return scrub_string(obj)
    return obj


def summarise_blob(v):
    if v in (None, {}, [], ""):
        return v
    return R


def scrub(doc):
    if isinstance(doc, dict) and isinstance(doc.get("workflow"), dict):
        doc = doc["workflow"]  # connector wrapper
    if not isinstance(doc, dict):
        raise SystemExit("input is not a JSON object")
    wf = {k: doc[k] for k in KEEP_KEYS if k in doc}
    if "tags" in wf and isinstance(wf["tags"], list):
        wf["tags"] = sorted(t.get("name") if isinstance(t, dict) else t for t in wf["tags"])
    for k in ("pinData", "staticData"):
        if k in wf:
            wf[k] = summarise_blob(wf[k])
    if isinstance(wf.get("workflowData"), dict):
        wf["workflowData"] = scrub(wf["workflowData"])
    wf = walk(wf)
    if isinstance(wf.get("nodes"), list):
        wf["nodes"] = sorted(wf["nodes"], key=lambda n: str(n.get("name", "")))
    return wf


def dump(obj):
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


CHECK_PATTERNS = [p for p, _ in SECRET_PATTERNS] + [
    re.compile(r"(?i)\bBearer\s+(?!<redacted>|\{\{)\S{12,}"),
]


def check(path):
    """Return a list of (json_path, pattern_index) for leftover matches."""
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    hits = []

    def visit(o, where):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and SECRET_KEY_RE.match(str(k)) and v not in (R, "") \
                        and "{{" not in v:
                    hits.append((where + "." + str(k), "secret-key"))
                visit(v, where + "." + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                visit(v, "%s[%d]" % (where, i))
        elif isinstance(o, str):
            for i, pat in enumerate(CHECK_PATTERNS):
                for m in pat.finditer(o):
                    if R not in m.group(0):
                        hits.append((where, "pattern-%d" % i))
    visit(doc, "$")
    return hits


def main(argv):
    if len(argv) >= 2 and argv[0] == "--check":
        bad = 0
        for path in argv[1:]:
            hits = check(path)
            print("%s: %d leftover secret-looking strings" % (path, len(hits)))
            for where, why in hits[:50]:
                print("  %s (%s)" % (where, why))
            bad += len(hits)
        return 1 if bad else 0
    if len(argv) != 2:
        print(__doc__)
        return 2
    with open(argv[0], encoding="utf-8") as f:
        doc = json.load(f)
    with open(argv[1], "w", encoding="utf-8") as f:
        f.write(dump(scrub(doc)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
