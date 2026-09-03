#!/usr/bin/env python3
import json, os, shutil, tempfile, webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("MCIT_DATA_DIR", ROOT / "data")).resolve()
DATA = DATA_DIR / "MCITProjects.json"
HISTORY = DATA_DIR / "ProjectHistoryLog.txt"
DIRECT_WRITE = os.environ.get("MCIT_DIRECT_WRITE", "false").lower() in ("1", "true", "yes")

def initialize_data_files():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA.exists(): shutil.copyfile(ROOT / "data" / "MCITProjects.json", DATA)
    if not HISTORY.exists():
        source = ROOT / "data" / "ProjectHistoryLog.txt"
        shutil.copyfile(source, HISTORY) if source.exists() else HISTORY.touch()

def write_text_file(path, content):
    if DIRECT_WRITE:
        with path.open("w", encoding="utf-8", newline="\n") as f: f.write(content)
        return
    fd, temp_path = tempfile.mkstemp(prefix="mcit_data_", suffix=path.suffix, dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f: f.write(content)
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path): os.unlink(temp_path)

def encode_history_field(value):
    return str(value).replace("\\", "\\\\").replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\\n")

def decode_history_field(value):
    return value.replace("\\n", "\n").replace("\\\\", "\\")

def read_history(project_code):
    if not HISTORY.exists(): return []
    records = []
    with HISTORY.open("r", encoding="utf-8") as f:
        for index, line in enumerate(f, 1):
            parts = line.rstrip("\n").split("||")
            if len(parts) != 4 or parts[0] != project_code: continue
            records.append({"id": index, "projectCode": parts[0], "logText": decode_history_field(parts[1]), "user": decode_history_field(parts[2]), "timestamp": parts[3]})
    return records

def append_history(project_code, log_text, user, timestamp):
    if "||" in project_code or "||" in log_text or "||" in user: raise ValueError('The value "||" is reserved as the history-file delimiter.')
    with HISTORY.open("a", encoding="utf-8", newline="\n") as f:
        f.write("||".join((project_code, encode_history_field(log_text), encode_history_field(user), timestamp)) + "\n")

def delete_history(project_code, record_id):
    if not HISTORY.exists(): return False
    lines = HISTORY.read_text(encoding="utf-8").splitlines(keepends=True)
    index = record_id - 1
    if index < 0 or index >= len(lines) or lines[index].split("||", 1)[0] != project_code: return False
    lines.pop(index)
    write_text_file(HISTORY, "".join(lines))
    return True

def reply_history(project_code, record_id, reply_text, reply_timestamp):
    if not HISTORY.exists(): return None
    if "||" in reply_text: raise ValueError('The value "||" is reserved as the history-file delimiter.')
    lines = HISTORY.read_text(encoding="utf-8").splitlines(keepends=True)
    index = record_id - 1
    if index < 0 or index >= len(lines): return None
    parts = lines[index].rstrip("\n").split("||")
    if len(parts) != 4 or parts[0] != project_code: return None
    combined_text = decode_history_field(parts[1]) + f"\n[{reply_timestamp}] {reply_text.strip()}"
    lines[index] = "||".join((parts[0], encode_history_field(combined_text), parts[2], parts[3])) + "\n"
    write_text_file(HISTORY, "".join(lines))
    return {"id": record_id, "projectCode": parts[0], "logText": combined_text, "user": decode_history_field(parts[2]), "timestamp": parts[3]}

def edit_history_text(project_code, record_id, log_text):
    if not HISTORY.exists(): return None
    if "||" in log_text: raise ValueError('The value "||" is reserved as the history-file delimiter.')
    lines = HISTORY.read_text(encoding="utf-8").splitlines(keepends=True)
    index = record_id - 1
    if index < 0 or index >= len(lines): return None
    parts = lines[index].rstrip("\n").split("||")
    if len(parts) != 4 or parts[0] != project_code: return None
    edited_text = log_text.strip()
    lines[index] = "||".join((parts[0], encode_history_field(edited_text), parts[2], parts[3])) + "\n"
    write_text_file(HISTORY, "".join(lines))
    return {"id": record_id, "projectCode": parts[0], "logText": edited_text, "user": decode_history_field(parts[2]), "timestamp": parts[3]}

def read_projects():
    with DATA.open("r", encoding="utf-8") as f:
        return json.load(f)

def write_projects(payload):
    write_text_file(DATA, json.dumps(payload, ensure_ascii=False, indent=2))

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def json_response(self, body, status=200):
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)

    def request_body(self):
        return json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))).decode("utf-8"))

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/projects": return self.json_response(read_projects())
        if path.startswith("/api/history/"): return self.json_response({"logs": read_history(unquote(path[len("/api/history/"):]))})
        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path.startswith("/api/history/"):
            from datetime import datetime, timezone
            project_code, payload = unquote(path[len("/api/history/"):]), self.request_body()
            log_text, user = str(payload.get("logText", "")).strip(), str(payload.get("user", "")).strip()
            if not log_text or not user: return self.json_response({"error":"Log text and user are required"}, 400)
            timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            try: append_history(project_code, log_text, user, timestamp)
            except ValueError as e: return self.json_response({"error":str(e)}, 400)
            return self.json_response({"log":{"projectCode":project_code,"logText":log_text,"user":user,"timestamp":timestamp}}, 201)
        if path != "/api/projects": return self.send_error(404)
        data, project = read_projects(), self.request_body()
        project["id"] = max([p.get("id", 0) for p in data["projects"]] + [0]) + 1
        for field in ("actualCompletionRate", "plannedCompletionRate", "actualImplementationRate", "plannedImplementationRate", "actualOperationRate", "plannedOperationRate"):
            project[field] = max(0, min(100, int(project.get(field, 0))))
        data["projects"].append(project); write_projects(data); self.json_response({"project": project}, 201)

    def do_PUT(self):
        parts = urlparse(self.path).path.strip("/").split("/")
        if len(parts) == 4 and parts[:2] == ["api", "history"]:
            from datetime import datetime, timezone
            try: record_id = int(parts[3])
            except ValueError: return self.send_error(400)
            payload = self.request_body()
            is_edit = "logText" in payload
            text = str(payload.get("logText" if is_edit else "replyText", "")).strip()
            if not text: return self.json_response({"error":"Log text is required" if is_edit else "Reply text is required"}, 400)
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
            try: log = edit_history_text(unquote(parts[2]), record_id, text) if is_edit else reply_history(unquote(parts[2]), record_id, text, timestamp)
            except ValueError as e: return self.json_response({"error":str(e)}, 400)
            if not log: return self.json_response({"error":"History entry not found"}, 404)
            return self.json_response({"log":log})
        self.change_project(False)
    def do_DELETE(self):
        parts = urlparse(self.path).path.strip("/").split("/")
        if len(parts) == 4 and parts[:2] == ["api", "history"]:
            try: record_id = int(parts[3])
            except ValueError: return self.send_error(400)
            if not delete_history(unquote(parts[2]), record_id): return self.json_response({"error":"History entry not found"}, 404)
            self.send_response(204); self.end_headers(); return
        self.change_project(True)

    def change_project(self, delete):
        parts = urlparse(self.path).path.strip("/").split("/")
        if len(parts) != 3 or parts[:2] != ["api", "projects"]: return self.send_error(404)
        try: project_id = int(parts[2])
        except ValueError: return self.send_error(400)
        data = read_projects(); index = next((i for i,p in enumerate(data["projects"]) if p.get("id") == project_id), None)
        if index is None: return self.json_response({"error":"Project not found"}, 404)
        if delete:
            data["projects"].pop(index); write_projects(data); self.send_response(204); self.end_headers(); return
        project = self.request_body(); project["id"] = project_id
        for field in ("actualCompletionRate", "plannedCompletionRate", "actualImplementationRate", "plannedImplementationRate", "actualOperationRate", "plannedOperationRate"):
            project[field] = max(0, min(100, int(project.get(field, 0))))
        data["projects"][index] = project; write_projects(data); self.json_response({"project":project})

if __name__ == "__main__":
    initialize_data_files()
    host = os.environ.get("MCIT_HOST", "0.0.0.0")
    port = int(os.environ.get("MCIT_PORT", "8768"))
    browser_url = f"http://127.0.0.1:{port}"
    print(f"MCIT PMO Dashboard: {browser_url}")
    print("Keep this window open. Press Ctrl+C to stop.")
    if os.environ.get("MCIT_AUTO_OPEN", "true").lower() in ("1", "true", "yes"): webbrowser.open(browser_url)
    ThreadingHTTPServer((host, port), Handler).serve_forever()
