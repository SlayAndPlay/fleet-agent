import base64, hashlib, json, os, urllib.parse, urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

URL = os.environ["SNOW_URL"].rstrip("/")
AUTH = base64.b64encode(f'{os.environ["SNOW_USER"]}:{os.environ["SNOW_PASS"]}'.encode()).decode()


def snow(method, path, body=None):
    req = urllib.request.Request(
        URL + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": "Basic " + AUTH,
                 "Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def handle(p):
    key = hashlib.sha256(p["groupKey"].encode()).hexdigest()[:32]
    alerts = p.get("alerts", [])
    note = "\n".join(
        f'{a["status"].upper()} {a["labels"].get("alertname")} host={a["labels"].get("host")} '
        f'{a["labels"].get("mountpoint", "")} - {a.get("annotations", {}).get("summary", "")}'
        for a in alerts)
    q = urllib.parse.quote(f"correlation_id={key}^state<6")
    found = snow("GET", f"/api/now/table/incident?sysparm_query={q}"
                        "&sysparm_fields=sys_id,number&sysparm_limit=1")["result"]
    if found:
        snow("PATCH", f'/api/now/table/incident/{found[0]["sys_id"]}', {"work_notes": note})
        return f'updated {found[0]["number"]}'
    if p["status"] != "firing":
        return "resolved with no open incident, ignored"
    common = p.get("commonLabels", {})
    r = snow("POST", "/api/now/table/incident", {
        "short_description": common.get("alertname", "alert"),
        "description": note, "work_notes": note, "correlation_id": key,
        "urgency": "1" if common.get("severity") == "critical" else "2", "impact": "2"})
    return f'created {r["result"]["number"]}'


class H(BaseHTTPRequestHandler):
    def _reply(self, code, text):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(text.encode())

    def do_GET(self):
        self._reply(200, "ok")

    def do_POST(self):
        try:
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            result = handle(payload)
            print(result, flush=True)
            self._reply(200, result)
        except Exception as e:
            print("ERROR", repr(e), flush=True)
            self._reply(500, "error")


HTTPServer(("", 8080), H).serve_forever()
