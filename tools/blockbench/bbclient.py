"""Tiny client for the Blockbench MCP plugin (streamable HTTP at localhost:3000/bb-mcp)."""
import base64
import json
import urllib.error
import urllib.request

URL = "http://localhost:3000/bb-mcp"
_sid = None
_id = 0


def _post(payload, sid=None):
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if sid:
        headers["Mcp-Session-Id"] = sid
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=300) as r:
        body = r.read().decode("utf-8", "replace")
        new_sid = r.headers.get("Mcp-Session-Id")
    if "data:" in body[:64] or body.lstrip().startswith("event:"):
        msgs = [json.loads(l[5:].strip()) for l in body.splitlines() if l.startswith("data:")]
        return (msgs[-1] if msgs else None), new_sid
    return (json.loads(body) if body.strip() else None), new_sid


def _session():
    global _sid
    if _sid is None:
        _, sid = _post({"jsonrpc": "2.0", "id": 0, "method": "initialize",
                        "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                                   "clientInfo": {"name": "bugslife-tools", "version": "1"}}})
        _sid = sid
        if sid:
            _post({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
    return _sid


def call(tool, args=None):
    """Calls a tool; returns list of content blocks. Raises on error."""
    global _id
    _id += 1
    res, _ = _post({"jsonrpc": "2.0", "id": _id, "method": "tools/call",
                    "params": {"name": tool, "arguments": args or {}}}, _session())
    if "error" in res:
        raise RuntimeError(f"{tool}: {res['error']}")
    result = res["result"]
    if result.get("isError"):
        raise RuntimeError(f"{tool}: " + "".join(c.get("text", "") for c in result.get("content", []))[:4000])
    return result.get("content", [])


def text(tool, args=None):
    return "".join(c.get("text", "") for c in call(tool, args) if c.get("type") == "text")


def js(code):
    """Evaluates JS in Blockbench and returns the decoded JSON result."""
    out = text("risky_eval", {"code": code})
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return out


def save_image(tool, args, path):
    for c in call(tool, args):
        if c.get("type") == "image":
            open(path, "wb").write(base64.b64decode(c["data"]))
            return path
    raise RuntimeError("no image returned")
