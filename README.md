# XSMB Android 1.1.0

Mã nguồn Android của XSMB: dữ liệu kết quả, dự đoán/soi cầu, kiểm tra lịch sử,
nhật ký, sổ thu chi và xuất CSV/XLSX/PDF. Backend Python chạy trên loopback;
giao diện HTML được mở trong WebView Android thật.

## Build APK bằng GitHub Actions

1. Chép toàn bộ mã nguồn này vào repository `thanhhajbgg/xsmb-android`, bao gồm
   `.github/workflows/build-apk.yml`, `android_src`, `android_config` và `p4a-recipes`.
2. Commit và push lên `main` hoặc `master`.
3. Vào **Actions → Build Android APK**. Workflow tự chạy khi push; cũng có thể
   chọn **Run workflow** để chạy thủ công.
4. Chờ cả hai job **test** và **build** thành công.
5. Mở lần chạy đó → **Artifacts → XSMB-Android-debug** → tải ZIP và giải nén.
6. Chép file `.apk` sang điện thoại và mở để cài. Đây là APK debug có chữ ký,
   không phải AAB hay bản release chưa ký.

APK dành cho **Android 7.0 trở lên, CPU ARM 64-bit**. Không chứa dữ liệu mẫu giả.
Nhập CSV hoặc tải kết quả ở mục Dữ liệu sau khi mở ứng dụng.

Nếu lần build bị lỗi, tải artifact **XSMB-build-log** để xem nguyên nhân.
Không lấy việc job test thành công làm bằng chứng APK đã build thành công.

## Build trên Ubuntu / WSL2

Dùng Python 3.12, JDK 17 và thư mục nằm trong filesystem Linux của WSL2:

```bash
sudo apt-get update
sudo apt-get install -y git zip unzip openjdk-17-jdk autoconf automake \
  autopoint gettext libtool libltdl-dev pkg-config zlib1g-dev libncurses-dev \
  libtinfo6 cmake libffi-dev libssl-dev build-essential ccache python3-venv
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-build.txt
buildozer -v android debug
```

APK nằm trong `bin/`. Lần build đầu phải tải Android SDK, NDK, Gradle và mã
nguồn các thư viện; cần kết nối mạng đến các kho tương ứng.

## Kiểm thử backend

```bash
python -m pip install -r requirements-test.txt
python -m pytest -q
node --check web/app.js
```

Xem giao diện trên máy tính:

```bash
python -m src.pro_server
```

## Thành phần quan trọng

- `main.py`: entrypoint bắt buộc của python-for-android.
- `main_android.py`: vòng đời Kivy, khởi động backend trên luồng nền.
- `android_src/.../NativeBrowser.java`: WebView, Back, nhập CSV, lưu báo cáo.
- `src/pro_server.py`: đầy đủ API, token phiên và kiểm tra Origin/Host.
- `src/paths.py`, `android_paths.py`: dữ liệu trong vùng riêng của ứng dụng.
- `p4a-recipes/reportlab`: recipe ReportLab 4 thay recipe Mercurial cũ.
- `buildozer.spec`: Python 3.12.10, p4a 2026.05.09 được khóa bằng commit,
  NumPy 2.3.0 theo recipe, NDK r28c, API 35 / min API 24.

Không đổi NumPy về `v1.22.4` trong cấu hình này: recipe NumPy mới dùng Meson.
Không thêm Cython vào requirements của APK: Cython là công cụ build trên máy.

Nhập/xuất dùng bộ chọn tài liệu của Android, không cần quyền đọc toàn bộ bộ nhớ.
File xuất chỉ báo **Đã lưu file** khi Android đã ghi xong. Hủy hộp thoại sẽ
không báo lưu thành công. Dữ liệu ứng dụng bị xóa khi gỡ cài đặt hoặc xóa dữ liệu.

Các APK debug từ hai máy build có thể có chữ ký khác nhau. Để phát hành và cập
nhật ổn định, cần dùng keystore release riêng, giữ nguyên qua các phiên bản.
Không đưa keystore hoặc mật khẩu lên GitHub. Workflow hiện chỉ xuất bản debug.

## Trạng thái xác minh bản sửa

- 50 kiểm thử Python và 9 subtest đạt; đã thử với NumPy 2.3.0 / ReportLab 4.2.5.
- JavaScript hợp lệ; kiểm tra DOM với backend thật mở được 7 trang và gọi bridge xuất file.
- Java helper qua kiểm tra biên dịch với Android API 35 và stub chữ ký của PythonActivity;
  đây không phải kiểm thử thiết bị hay biên dịch toàn bộ APK.
- Đã thử `buildozer -v android debug`; môi trường sửa mã dừng khi tải Apache Ant
  (`ValueError: read of closed file`). **Chưa có APK hoàn chỉnh hoặc kết quả kiểm thử
  trên điện thoại trong bản bàn giao này.** Workflow GitHub cần chạy để xác nhận build.

Chi tiết lỗi đã sửa ở `ANDROID_FIX_REPORT.md`.
