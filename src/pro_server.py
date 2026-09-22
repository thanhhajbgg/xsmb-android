"""
HTTP server backend cho ứng dụng XSMB.
- Phục vụ file tĩnh từ thư mục web/.
- Cung cấp các API endpoint cho frontend.
"""
import os
import json
import mimetypes
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

# Thư mục gốc dự án
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(ROOT, "web")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[http] {fmt % args}")

    # ---------- Helpers ----------
    def _send_json(self, obj, status=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

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

    def _read_json_body(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length == 0:
                return {}
            raw = self.rfile.read(length)
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    # ---------- Routing ----------
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # ----- API endpoints -----
        if path == "/api/health":
            return self._send_json({"status": "ok", "version": "1.0.0"})

        if path == "/api/ping":
            return self._send_json({"pong": True})

        # Ví dụ: API lấy dữ liệu XSMB (bạn thay bằng logic thật của mình)
        if path == "/api/xsmb/latest":
            try:
                data = self._get_latest_xsmb()
                return self._send_json({"success": True, "data": data})
            except Exception as e:
                traceback.print_exc()
                return self._send_json({"success": False, "error": str(e)}, status=500)

        # Ví dụ: API dự đoán (bạn thay bằng logic thật của mình)
        if path == "/api/xsmb/predict":
            try:
                data = self._predict_xsmb()
                return self._send_json({"success": True, "data": data})
            except Exception as e:
                traceback.print_exc()
                return self._send_json({"success": False, "error": str(e)}, status=500)

        # Ví dụ: API xuất Excel (bạn thay bằng logic thật của mình)
        if path == "/api/export/excel":
            try:
                filepath = self._export_excel()
                return self._send_file(filepath, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception as e:
                traceback.print_exc()
                return self._send_json({"success": False, "error": str(e)}, status=500)

        # ----- Static files -----
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
            # SPA fallback: trả về index.html cho các route của frontend
            index = os.path.join(WEB_DIR, "index.html")
            if os.path.isfile(index):
                self._send_file(index)
            else:
                self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        if path == "/api/xsmb/save":
            try:
                result = self._save_data(body)
                return self._send_json({"success": True, "data": result})
            except Exception as e:
                traceback.print_exc()
                return self._send_json({"success": False, "error": str(e)}, status=500)

        return self._send_json({"success": False, "error": "Unknown endpoint"}, status=404)

    # ---------- Business Logic (bạn thay bằng code thật) ----------
    def _get_latest_xsmb(self):
        """Trả về dữ liệu XSMB mới nhất. Thay bằng logic thật."""
        # Ví dụ: đọc từ file Excel trong thư mục data/
        data_dir = os.environ.get("XSMB_DATA_DIR", os.path.join(ROOT, "data"))
        return {
            "date": "2026-09-22",
            "special": "12345",
            "prize1": "67890",
            "note": "Dữ liệu mẫu - hãy thay bằng logic thật của bạn",
            "data_dir": data_dir,
        }

    def _predict_xsmb(self):
        """Trả về dự đoán XSMB. Thay bằng logic thật."""
        return {
            "predictions": ["12", "34", "56", "78", "90"],
            "confidence": 0.85,
            "note": "Dự đoán mẫu - hãy thay bằng logic thật của bạn",
        }

    def _export_excel(self):
        """Xuất file Excel. Thay bằng logic thật."""
        exports_dir = os.environ.get("XSMB_EXPORTS_DIR", os.path.join(ROOT, "exports"))
        os.makedirs(exports_dir, exist_ok=True)
        filepath = os.path.join(exports_dir, "xsmb_export.xlsx")

        try:
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "XSMB"
            ws.append(["Ngày", "Giải đặc biệt", "Giải nhất"])
            ws.append(["2026-09-22", "12345", "67890"])
            wb.save(filepath)
        except ImportError:
            # Nếu openpyxl không có, tạo file text đơn giản
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("date,special,prize1\n2026-09-22,12345,67890\n")
        return filepath

    def _save_data(self, body):
        """Lưu dữ liệu do frontend gửi lên. Thay bằng logic thật."""
        data_dir = os.environ.get("XSMB_DATA_DIR", os.path.join(ROOT, "data"))
        os.makedirs(data_dir, exist_ok=True)
        filepath = os.path.join(data_dir, "saved_data.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(body, f, ensure_ascii=False, indent=2)
        return {"saved_to": filepath}


def run_server(host="127.0.0.1", port=8765):
    """Khởi động HTTP server. Hàm này được gọi từ main.py."""
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
