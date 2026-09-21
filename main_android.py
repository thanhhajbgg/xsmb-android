"""Entry point APK: chạy server Python nền + hiển thị WebView."""
import os, socket, threading, time, sys

from android_paths import setup_android_paths
setup_android_paths()

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import platform

PREFERRED_PORT = 8765


def _free_port(start):
    for p in range(start, start + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("No free port")


def _start_backend(port):
    os.environ["XSMB_PORT"] = str(port)
    os.environ["XSMB_NO_BROWSER"] = "1"
    os.environ["XSMB_BIND"] = "127.0.0.1"
    try:
        from src.pro_server import main as server_main
        server_main()
    except Exception as e:
        print("BACKEND CRASH:", e, file=sys.stderr)
        import traceback; traceback.print_exc()


if platform == "android":
    from jnius import autoclass
    from android.runnable import run_on_ui_thread

    WebView = autoclass("android.webkit.WebView")
    WebViewClient = autoclass("android.webkit.WebViewClient")
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    LayoutParams = autoclass("android.view.ViewGroup$LayoutParams")


class AndroidWebView(BoxLayout):
    def __init__(self, url, **kw):
        super().__init__(**kw)
        self.url = url
        Clock.schedule_once(self._install, 0)

    def _install(self, *_):
        self._install_on_ui()

    @run_on_ui_thread
    def _install_on_ui(self):
        activity = PythonActivity.mActivity
        web = WebView(activity)
        s = web.getSettings()
        s.setJavaScriptEnabled(True)
        s.setDomStorageEnabled(True)
        s.setAllowFileAccess(True)
        s.setMixedContentMode(0)
        web.setWebViewClient(WebViewClient())
        web.loadUrl(self.url)
        lp = LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT)
        activity.addContentView(web, lp)


class XsmbApp(App):
    def build(self):
        self.port = _free_port(PREFERRED_PORT)
        self.url = f"http://127.0.0.1:{self.port}/"
        threading.Thread(target=_start_backend, args=(self.port,), daemon=True).start()
        for _ in range(150):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("127.0.0.1", self.port)) == 0:
                    break
            time.sleep(0.1)
        if platform == "android":
            return AndroidWebView(self.url)
        return Label(text=f"Server: {self.url}")


if __name__ == "__main__":
    XsmbApp().run()