# Kiểm thử V2 PRO

Môi trường xác minh: Linux, Python 3.12. Kết quả cuối: 28 tests passed, 9 subtests passed. Chưa có bản EXE được dựng trên Windows.

Các nhóm đã kiểm tra tự động:

- Giữ nguyên kiểm thử từ V1.2/V1.3.
- 30 đặc trưng hữu hạn; đủ 100 số; thứ tự tái lập được.
- Backtest tính chi phí toàn nhóm và tiền trả theo nháy; thay kết quả tương lai không thay dự báo quá khứ; bỏ kỳ sau khoảng trống.
- Optimizer: chia thời gian, trọng số tổng bằng 1, tái lập; thay kết quả trong tập kiểm tra không làm thay trọng số được chọn.
- Sổ: thua, một nháy, nhiều nháy, chờ, nhập sai, lưu/mở lại/sửa/xóa; tổng tiền theo ngày/tuần/tháng/năm khớp nhau; vốn đầu kỳ theo bộ lọc.
- Nhật ký và card dự báo không đổi sau khi đổi mô hình; xếp hạng xem trước được phân biệt.
- Parser từ chối sai ngày hoặc thiếu giải; chuyển sang nguồn kế tiếp; nhiều bảng ngày không trộn kết quả; bảng không có ngày không mượn ngày bảng trước.
- CSV từ chối ngày lỗi, thiếu số, ngày trùng; xung đột với DB không ghi một phần.
- HTTP: truy cập trang, token, từ chối Origin bên ngoài, nhập sổ, trả dữ liệu và xuất ba định dạng.
- Excel: số 08 còn chuỗi, tiền là số, ghi chú công thức không trở thành công thức.
- PDF: trích xuất được tiếng Việt và số tiền; ghi chú dài chia trang.
- Kiểm thử DOM qua jsdom nối với máy chủ trên DB tạm: dashboard, 100 ô heatmap, 30 chỉ báo, sổ lưu/sửa, vốn, đồ thị, nhật ký, backtest, dữ liệu, đổi theme. Canvas được mô phỏng, không chứng minh hiển thị đúng bằng ảnh.
- Optimizer đã chạy hoàn tất 2.000 cấu hình trên 240 kỳ dữ liệu tổng hợp, chia 108/36/36 kỳ sau 60 kỳ khởi động. Không dùng kết quả này làm ví dụ lợi nhuận thật.

## Chưa xác minh

- Chạy EXE trên Windows, ảnh giao diện thực, thao tác zoom/pan bằng chuột thực và trình duyệt trên điện thoại.
- Tải trực tiếp từ website: các yêu cầu của môi trường xây dựng hết thời gian chờ. Các kiểm thử parser dùng fixture; không khẳng định đã tương thích toàn bộ HTML hiện hành.
- Không kiểm định khả năng dự đoán bằng một tập dữ liệu thực độc lập; không tuyên bố có lợi nhuận.

## Kiểm tra nhanh khi chạy trên máy người dùng

1. Dashboard mở và báo chưa có dữ liệu nếu DB trống.
2. Nhập khoản 15/09/2026, số 88, 100 điểm, đơn giá 23000/80000, 0 nháy: lỗ 2.300.000đ.
3. Sửa 1 nháy: lãi 5.700.000đ. Sửa 2 nháy: lãi 13.700.000đ.
4. Bỏ trống nháy: chỉ đối chiếu nếu đã có kết quả đúng ngày, còn không phải hiện Chờ.
5. Mở lại chương trình để kiểm tra lịch sử còn nguyên.
6. Nhập CSV thật/tải dữ liệu, rồi chạy backtest và kiểm tra một ngày bằng tay.
7. Xuất báo cáo Excel/PDF/CSV, đối chiếu tổng tiền với sổ.

Không phân phối DB kiểm thử hoặc dữ liệu tổng hợp vào hồ sơ thật.


## V2.1 — kiểm thử bổ sung

- Cặp không trùng chính nó hoặc đảo lặp; đúng 4.950 ứng viên.
- Tỷ lệ ít nhất một số/cả hai số khớp đếm trực tiếp.
- Không tuyển cặp khi thiếu dữ liệu; cầu ít mẫu không đóng góp điểm.
- Chỉ nối chuyển tiếp giữa ngày liền nhau; cửa sổ thiếu ngày được báo.
- Luồng tính rút gọn trong backtest chọn đúng cặp giống bảng hiển thị.
- Tiền mua gồm hai số; tiền nhận theo nháy; thay tương lai không đổi cặp quá khứ.
- Nhật ký giữ cặp khi đổi cấu hình, kể cả cấu hình mới thiếu mẫu; đối chiếu đủ nháy.
- API tab mới, tác vụ backtest nền, xuất ba định dạng; không sinh khoản vốn thật.

Kết quả V2.1: 39 bài kiểm thử và 9 subtests đạt. Kiểm thử DOM mới đạt: mở tab, 20 cặp, lọc cầu, giữ cặp khi đổi cấu hình, hiển thị backtest 30 ngày và số tiền, lựa chọn báo cáo. Canvas mô phỏng; không phải kiểm tra ảnh giao diện Windows.
