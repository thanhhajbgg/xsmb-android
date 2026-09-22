"""
Thiết lập sys.path và thư mục làm việc cho môi trường Android.
Phải được import TRƯỚC kivy và các module khác.
"""
import os
import sys

def setup_android_paths():
    """Thiết lập đường dẫn cho Android. Gọi hàm này ngay đầu main_android.py."""
    try:
        from android.storage import app_storage_path  # type: ignore
        from jnius import autoclass  # type: ignore

        # Lấy context ứng dụng
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = PythonActivity.mActivity
        app_dir = activity.getFilesDir().getAbsolutePath()

        # Thư mục dữ liệu riêng của app
        data_dir = os.path.join(app_dir, "data")
        os.makedirs(data_dir, exist_ok=True)

        # Thư mục cho file xuất Excel/CSV
        exports_dir = os.path.join(app_dir, "exports")
        os.makedirs(exports_dir, exist_ok=True)

        # Đặt biến môi trường cho app biết
        os.environ["XSMB_DATA_DIR"] = data_dir
        os.environ["XSMB_EXPORTS_DIR"] = exports_dir

        # Thêm thư mục gốc vào sys.path để import src.* và web.*
        root = os.path.dirname(os.path.abspath(__file__))
        if root not in sys.path:
            sys.path.insert(0, root)

        return True
    except Exception as e:
        print(f"[android_paths] Không phải môi trường Android hoặc lỗi: {e}")
        # Fallback cho desktop
        root = os.path.dirname(os.path.abspath(__file__))
        if root not in sys.path:
            sys.path.insert(0, root)
        os.environ.setdefault("XSMB_DATA_DIR", os.path.join(root, "data"))
        os.environ.setdefault("XSMB_EXPORTS_DIR", os.path.join(root, "exports"))
        return False


# Tự động chạy khi import
IS_ANDROID = setup_android_paths()
