"""
Entry point cho APK Android.
- Khởi động Python HTTP server trên localhost.
- Hiển thị WebView Android phủ lên trên giao diện Kivy.
"""
import os
import sys
import threading
import time
import socket

# PHẢI import android_paths TRƯỚC kivy để setup sys.path và môi trường
import android_paths  # noqa: F401

# Cấu hình Kivy trước khi import
os.environ.setdefault("KIVY_NO_ARGS", "1")
os.environ.setdefault("KIVY_LOG_LEVEL", "info")

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp

# Thử import các module Android
try:
    from android.runnable import run_on_ui_thread  # type: ignore
    from jnius import autoclass, cast  # type: ignore
    from android import mActivity  # type: ignore

    WebView = autoclass("android.webkit.WebView")
    WebViewClient = autoclass("android.webkit.WebViewClient")
    WebChromeClient = autoclass("android.webkit.WebChromeClient")
    LayoutParams = autoclass("android.view.ViewGroup$LayoutParams")
    FrameLayout = autoclass("android.widget.FrameLayout")
    Gravity = autoclass("android.view.Gravity")
    IS_ANDROID = True
except Exception as e:
    print(f"[main] Không phải môi trường Android: {e}")
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
            from src.pro_server import run_server  # type: ignore
            run_server(host="127.0.0.1", port=port)
        except Exception as e:
            print(f"[server] Lỗi khởi động server: {e}")
            import traceback
            traceback.print_exc()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t


def wait_for_server(port, timeout=20.0):
    """Đợi server sẵn sàng."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.3)
    return False


class LoadingScreen(BoxLayout):
    """Màn hình chờ trong lúc server khởi động."""
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.add_widget(Label(
            text="Đang khởi động XSMB...\nVui lòng đợi trong giây lát",
            font_size="18sp",
            halign="center",
            valign="middle",
        ))


class XSMBApp(App):
    def build(self):
        self.title = "XSMB Android"
        self.port = find_free_port()
        self.url = f"http://127.0.0.1:{self.port}/"
        print(f"[main] Khởi động server tại {self.url}")

        # Khởi động server trong background
        start_server(self.port)

        # Hiển thị màn hình chờ
        return LoadingScreen()

    def on_start(self):
        """Sau khi Kivy khởi động xong, đợi server rồi mở WebView."""
        threading.Thread(target=self._wait_and_show_webview, daemon=True).start()

    def _wait_and_show_webview(self):
        """Đợi server sẵn sàng rồi gọi hiển thị WebView trên UI thread."""
        if wait_for_server(self.port, timeout=20.0):
            print("[main] Server đã sẵn sàng, đang mở WebView...")
            Clock.schedule_once(lambda dt: self._show_webview(), 0.5)
        else:
            print("[main] Server không phản hồi sau 20s, vẫn thử mở WebView...")
            Clock.schedule_once(lambda dt: self._show_webview(), 0.5)

    @run_on_ui_thread
    def _show_webview(self):
        """Thêm WebView vào Android Activity (chạy trên UI thread)."""
        if not IS_ANDROID:
            print("[main] Không phải Android, bỏ qua WebView.")
            return

        try:
            activity = mActivity

            # Tạo WebView
            webview = WebView(activity)
            settings = webview.getSettings()
            settings.setJavaScriptEnabled(True)
            settings.setDomStorageEnabled(True)
            settings.setAllowFileAccess(True)
            settings.setAllowContentAccess(True)
            settings.setLoadWithOverviewMode(True)
            settings.setUseWideViewPort(True)
            settings.setBuiltInZoomControls(False)
            settings.setDisplayZoomControls(False)
            settings.setMediaPlaybackRequiresUserGesture(False)

            webview.setWebViewClient(WebViewClient())
            webview.setWebChromeClient(WebChromeClient())

            # Layout params: match parent
            params = LayoutParams(
                LayoutParams.MATCH_PARENT,
                LayoutParams.MATCH_PARENT,
            )
            webview.setLayoutParams(params)

            # Lấy root view của Activity và thêm WebView lên trên
            root_view = activity.findViewById(android.R.id.content)
            root_view.addView(webview)

            # Load URL
            webview.loadUrl(self.url)
            print(f"[main] WebView đã load: {self.url}")

        except Exception as e:
            print(f"[main] Lỗi khi tạo WebView: {e}")
            import traceback
            traceback.print_exc()

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == "__main__":
    XSMBApp().run()
