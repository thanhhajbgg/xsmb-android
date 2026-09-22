"""
HTTP server backend cho ứng dụng XSMB.
Cung cấp API và phục vụ file tĩnh từ thư mục web/.
"""
import os
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

# Thư mục gốc dự án
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(ROOT, "web")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[http] {fmt % args}")

    def _send_file(self, path, content_type=None):
        try:
            with open(path, "rb") as f:
                data = f.read()
        except FileNotFoundError:
            self.send_error(404, "Not Found")
            return
        self.send_response(200)
        if content_type is None:
            content_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # API mẫu
        if path == "/api/health":
            self._send_json({"status": "ok"})
            return

        if path == "/api/ping":
            self._send_json({"pong": True})
            return

        # Phục vụ file tĩnh
        if path == "/" or path == "":
            path = "/index.html"

        # Bảo mật: chặn path traversal
        safe = os.path.normpath(path).lstrip("/\\")
        full = os.path.join(WEB_DIR, safe)
        if not os.path.abspath(full).startswith(os.path.abspath(WEB_DIR)):
            self.send_error(403, "Forbidden")
            return

        if os.path.isdir(full):
            full = os.path.join(full, "index.html")

        if os.path.isfile(full):
            self._send_file(full)
        else:
            # SPA fallback
            index = os.path.join(WEB_DIR, "index.html")
            if os.path.isfile(index):
                self._send_file(index)
            else:
                self.send_error(404, "Not Found")

    def _send_json(self, obj, status=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run_server(host="127.0.0.1", port=8765):
    """Khởi động HTTP server. Hàm này được gọi từ main_android.py."""
    if not os.path.isdir(WEB_DIR):
        print(f"[server] Cảnh báo: không tìm thấy thư mục web/ tại {WEB_DIR}")

    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"[server] Đang lắng nghe tại http://{host}:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print("[server] Đã dừng.")


if __name__ == "__main__":
    run_server()
