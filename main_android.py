"""Kivy lifecycle with a real native Android WebView and local HTTP service."""
import os
import threading
import logging
from pathlib import Path

import android_paths
os.environ.setdefault('KIVY_NO_ARGS', '1')

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label


class XSMBApp(App):
    server = None
    browser = None
    stopping = False

    def build(self):
        self.title = 'XSMB Android'
        self.status = Label(text='Đang khởi động XSMB…',
                            font_name=str(Path(__file__).parent / 'assets' / 'DejaVuSans.ttf'))
        threading.Thread(target=self._start, daemon=True).start()
        return self.status

    def _start(self):
        try:
            from src.pro_server import make_server
            from src.paths import get_data_dir
            logging.basicConfig(filename=get_data_dir() / 'android.log', level=logging.INFO)
            # Bind once to port 0: no find-free-port race and no UI-thread blocking.
            self.server = make_server()
            if self.stopping:
                self.server.server_close()
                return
            Clock.schedule_once(self._show_browser, 0)
            self.server.serve_forever(poll_interval=0.2)
        except Exception as exc:
            logging.exception('Android startup failed')
            message = f'Không khởi động được XSMB:\n{exc}'
            Clock.schedule_once(lambda dt: setattr(self.status, 'text', message), 0)
        finally:
            if self.server:
                self.server.server_close()

    def _show_browser(self, dt):
        if self.stopping:
            return
        url = f'http://127.0.0.1:{self.server.server_port}/'
        if not android_paths.IS_ANDROID:
            self.status.text = f'XSMB: {url}'
            return
        try:
            from jnius import autoclass
            from android.runnable import run_on_ui_thread
            @run_on_ui_thread
            def attach():
                try:
                    activity = autoclass('org.kivy.android.PythonActivity').mActivity
                    self.browser = autoclass('com.thanhhajbgg.xsmb.NativeBrowser').attach(activity, url)
                except Exception as exc:
                    logging.exception('WebView startup failed')
                    message = f'Lỗi WebView:\n{exc}'
                    Clock.schedule_once(lambda dt: setattr(self.status, 'text', message), 0)
            attach()
        except Exception as exc:
            self.status.text = f'Lỗi Android: {exc}'

    def on_pause(self):
        return True

    def on_stop(self):
        self.stopping = True
        if self.server:
            self.server.app.cancel_event.set()
            threading.Thread(target=self.server.shutdown, daemon=True).start()
        if self.browser:
            from android.runnable import run_on_ui_thread
            run_on_ui_thread(self.browser.destroy)()


if __name__ == '__main__':
    XSMBApp().run()
