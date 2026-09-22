"""
Entry point cho APK Android.
Khởi động Python HTTP server trên localhost, sau đó hiển thị WebView.
"""
import os
import sys
import threading
import time
import socket

# PHẢI import android_paths TRƯỚC kivy
import android_paths  # noqa: F401  (tự động setup sys.path)

# Cấu hình Kivy trước khi import
os.environ.setdefault("KIVY_NO_ARGS", "1")
os.environ.setdefault("KIVY_LOG_LEVEL", "info")

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

try:
    from android.runnable import run_on_ui_thread  # type: ignore
except ImportError:
    def run_on_ui_thread(f):
        return f

try:
    from jnius import autoclass, cast  # type: ignore
    WebView = autoclass("android.webkit.WebView")
    WebViewClient = autoclass("android.webkit.WebViewClient")
    WebChromeClient = autoclass("android.webkit.WebChromeClient")
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    LayoutParams = autoclass("android.view.ViewGroup$LayoutParams")
    IS_ANDROID = True
except Exception:
    IS_ANDROID = False


def find_free_port(start=8765, end=8865):
    """Tìm cổng trống trong khoảng cho trước."""
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("Không tìm được cổng trống")


def start_server(port):
    """Chạy server trong thread riêng."""
    def _run():
        try:
            # Import ở đây để tránh lỗi khi build
            from src.pro_server import run_server  # type: ignore
            run_server(host="127.0.0.1", port=port)
        except Exception as e:
            print(f"[server] Lỗi khởi động server: {e}")
            import traceback
            traceback.print_exc()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t


def wait_for_server(port, timeout=15.0):
    """Đợi server sẵn sàng."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.2)
    return False


class RootWidget(BoxLayout):
    def __init__(self, url, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.url = url
        self.webview = None
        self.status = Label(
            text="Đang tải ứng dụng...",
            font_size="16sp",
            size_hint=(1, 1),
            halign="center",
            valign="middle",
        )
        self.add_widget(self.status)
        Clock.schedule_once(lambda dt: self._setup_webview(), 0.5)

    @run_on_ui_thread
    def _setup_webview(self):
        if not IS_ANDROID:
            self.status.text = f"Server sẵn sàng tại: {self.url}\n(WebView chỉ chạy trên Android)"
            return

        try:
            activity = PythonActivity.mActivity
            webview = WebView(activity)
            webview.getSettings().setJavaScriptEnabled(True)
            webview.getSettings().setDomStorageEnabled(True)
            webview.getSettings().setAllowFileAccess(True)
            webview.getSettings().setAllowContentAccess(True)
            webview.getSettings().setLoadWithOverviewMode(True)
            webview.getSettings().setUseWideViewPort(True)
            webview.setWebViewClient(WebViewClient())
            webview.setWebChromeClient(WebChromeClient())
            webview.loadUrl(self.url)

            # Thay Label bằng WebView
            self.clear_widgets()
            self.add_widget(webview)
            self.webview = webview
        except Exception as e:
            self.status.text = f"Lỗi WebView: {e}"


class XSMBApp(App):
    def build(self):
        self.title = "XSMB Android"
        port = find_free_port()
        url = f"http://127.0.0.1:{port}/"
        print(f"[main] Khởi động server tại {url}")

        start_server(port)

        if not wait_for_server(port, timeout=15.0):
            print("[main] Cảnh báo: server chưa sẵn sàng sau 15s")

        return RootWidget(url)

    def on_pause(self):
        # Cho phép app chạy nền
        return True

    def on_resume(self):
        pass


if __name__ == "__main__":
    XSMBApp().run()
