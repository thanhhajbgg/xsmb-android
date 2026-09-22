# Báo cáo sửa Android — 22/09/2026

Nguồn kiểm tra: `thanhhajbgg/xsmb-android`, commit
`e6e616024123af363033d343f5e2bfbe9724cc09`.

| Lỗi xác định | Thay đổi |
|---|---|
| Không có `main.py` tại gốc | Thêm entrypoint đúng tên, chỉ khởi động khi chạy trực tiếp |
| Đưa Java WebView vào `Kivy.add_widget` | Gắn native WebView bằng Activity.addContentView |
| Backend chỉ trả health/ping, bỏ các API nghiệp vụ | Khôi phục server đầy đủ từ commit `5dcff73`, chạy lại kiểm thử sẵn có |
| Token trong HTML không được thay | Server tạo và gắn token theo phiên; API kiểm tra token/Origin/Host |
| `XSMB_DATA_DIR` được đặt nhưng backend không dùng | Cho `src.paths` đọc đường dẫn lưu riêng Android |
| Chờ server đồng bộ làm khóa giao diện, chọn cổng rồi đóng socket gây race | Khởi động nền và để server bind cổng 0 trực tiếp |
| Icon/presplash tham chiếu file không tồn tại | Dùng tài nguyên mặc định của Buildozer |
| NumPy bị ép về phiên bản không phù hợp recipe trên nhánh develop | Khóa p4a bằng commit và dùng NumPy đi cùng recipe |
| Thiếu ReportLab dù giao diện cho xuất PDF | Thêm ReportLab và recipe Python hiện đại cùng Pillow |
| input file và Blob download không đủ để nhập/xuất trong WebView | Thêm bộ chọn tài liệu và bridge lưu file, xử lý hủy/lỗi |
| Đóng backend nhưng Activity vẫn tồn tại | Android đóng Activity qua bridge, lifecycle dừng backend |
| Quy trình CI tải libtinfo5 từ mirror phụ, container latest, xóa cache trước restore | Runner Ubuntu/JDK/Python xác định, cài package chính thức, cache công cụ |
| Lệnh pipeline có thể che exit code build | Bật pipefail; lỗi build làm job thất bại |
| Bản release không có cấu hình ký | Workflow tạo APK debug đã ký và xác minh chữ ký |
| Bytecode Python 3.14 nằm trong git | Bỏ bytecode khỏi index và thêm .gitignore |

## Kết quả

Trước sửa, pytest không thu thập được test server vì thiếu `make_server`.
Ba kiểm thử bổ sung tái hiện lỗi đường dẫn dữ liệu, thiếu entrypoint và health API.
Sau sửa, 50 test và 9 subtest đạt. Có một cảnh báo deprecation từ ReportLab 4.2.5
trên Python 3.12; không làm test thất bại.

Kiểm tra Java chỉ kiểm tra helper với Android API jar và stub giao diện p4a,
không thay cho build Gradle. Kiểm tra DOM không thay cho kiểm tra WebView thiết bị.
Build APK tại môi trường này chưa hoàn tất do tải công cụ thất bại; không có APK
được tạo để bàn giao. Các thay đổi chưa được đẩy lên GitHub từ phiên làm việc này.

## Kiểm tra trên điện thoại sau khi CI build thành công

1. Cài APK, mở lần đầu và xác nhận dashboard hiển thị, không treo ở màn hình tải.
2. Nhập CSV hợp lệ; đóng/mở ứng dụng, kiểm tra lịch sử được giữ.
3. Xem dự đoán/soi cầu và chạy kiểm tra lịch sử khi đã có đủ dữ liệu.
4. Nhập/sửa/xóa khoản trong sổ, đối chiếu tiền mua/tiền nhận/lãi lỗ.
5. Xuất CSV, XLSX, PDF; chọn nơi lưu, mở file; thử hủy hộp thoại.
6. Chuyển sang ứng dụng khác rồi quay lại; thử nút Back/đóng rồi mở lại.
7. Tải kết quả trực tuyến; khi mất mạng phải hiện lỗi và giữ nguyên dữ liệu đã lưu.
