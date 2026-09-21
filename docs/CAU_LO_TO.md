# V2.1 — Cầu lô tô & tuyển chọn cặp

## Cách dùng

1. Cập nhật kết quả trong mục Dữ liệu hoặc nhập CSV thật.
2. Mở **Cầu & cặp lô tô**. Mặc định xét 180 kỳ, tối thiểu 20 mẫu cho mỗi cầu.
3. Xem **Cặp đã lưu** và ngày mục tiêu. Đây là hai số song thủ đánh riêng; không phải cược xiên. Phần mềm không tự đặt cược hoặc thêm khoản vào sổ.
4. Đọc Top 20 cặp, số mẫu và các cầu hỗ trợ. “Ít nhất 1 số” khác “cả hai số”. Chúng là tỷ lệ mô tả trong cửa sổ lịch sử, không phải xác suất ngày tới.
5. Bấm **Kiểm tra song thủ** để đánh giá cách tuyển chọn theo từng ngày. Nhập điểm/đơn giá thực tế; mỗi số trong cặp dùng số điểm đã nhập.
6. Có thể xuất Top cặp và kết quả kiểm tra sang Excel/PDF/CSV ở mục Xuất báo cáo.

Cần ít nhất 60 kỳ và 40 cặp ngày liên tiếp để đưa ra lựa chọn mới. Ngày mục tiêu là ngày sau kết quả mới nhất; nếu dữ liệu cũ, ứng dụng cảnh báo. Không có dữ liệu thật đi kèm gói phần mềm nên không có cặp dự đoán dựng sẵn.

## Các loại cầu

| Loại | Điều kiện đang có | Kiểm tra lịch sử |
|---|---|---|
|Lô rơi|Số đích xuất hiện kỳ cuối|Trong những lần số đó xuất hiện, ngày liền sau có tiếp tục ra không|
|Kép rơi|Giống lô rơi, số đích là 00, 11, …, 99|Tương tự lô rơi; không cộng điểm trùng hai lần|
|Đảo|Số đảo của số đích xuất hiện kỳ cuối|Nguồn 12 → đích 21, ví dụ; hai ngày phải liền nhau|
|Theo đầu|Kỳ cuối có ít nhất một số cùng hàng chục với số đích|Ngày có đầu này → ngày sau có số đích|
|Theo đuôi|Kỳ cuối có ít nhất một số cùng hàng đơn vị với số đích|Ngày có đuôi này → ngày sau có số đích|
|Theo thứ|Thứ của ngày mục tiêu|Số kỳ có số đích trong các kỳ trước cùng thứ|
|Chuyển tiếp|Một số nguồn xuất hiện kỳ cuối|Số nguồn hôm trước → số đích ngày sau; loại các quan hệ đã tính như rơi/đảo trong bảng này|
|Đồng xuất hiện của cặp|Hai số khác nhau|Số kỳ có cả hai và số kỳ có ít nhất một số trong cửa sổ|

Không nối cầu qua ngày lịch bị thiếu. “Mẫu” của cầu chuyển tiếp là số lần điều kiện nguồn xảy ra với ngày kế tiếp có dữ liệu, không phải toàn bộ số kỳ. Một số nguồn ra nhiều nháy vẫn chỉ tính một lần có điều kiện; tiền thưởng sau đó vẫn tính đủ số nháy.

Các cầu ở đây là định nghĩa thống kê minh bạch của V2.1, không khẳng định bao phủ mọi trường phái “soi cầu”. Chưa dựng cầu vị trí chữ số từ toàn bộ giải, Pascal hoặc quy tắc truyền miệng vì bộ dữ liệu hiện chủ yếu giữ 27 đuôi hai chữ số.

## Giảm ảnh hưởng mẫu nhỏ

Cầu chỉ đóng góp điểm nếu số mẫu đạt ngưỡng. Bảng vẫn hiển thị cầu ít mẫu để người dùng thấy lý do loại. Cận dưới Wilson với z=1,96 được dùng như một thước đo thận trọng của tỷ lệ lịch sử:

`(p + z²/(2n) − z × sqrt(p(1−p)/n + z²/(4n²))) / (1+z²/n)`

n=0 cho 0. Đây là công thức khoảng tin cậy dưới mô hình nhị thức độc lập, không phải xác suất trúng của ngày mai. Nó không xử lý đầy đủ phụ thuộc theo thời gian hoặc thiên lệch khi tìm trên hàng nghìn cầu/cặp.

## Cách xếp hạng

Mọi chuẩn hóa dưới đây là min–max trên các ứng viên cùng lần tính; cột không biến thiên cho 0.

Điểm mỗi số gồm:

- 35% tần suất 30 kỳ.
- 15% tần suất 7 kỳ.
- 20% trung bình cận dưới của các cầu đủ mẫu ngoài nhóm Chuyển tiếp.
- 20% trung bình cận dưới chuyển tiếp từ các số nguồn kỳ cuối đủ mẫu.
- 10% chênh tần suất/ngày 7 kỳ so với 30 kỳ.

Xét đủ **4.950 cặp hai số khác nhau**, không tính lặp 12–21 và 21–12. Điểm cặp thô gồm 65% trung bình điểm hai số, 25% thống kê có ít nhất một số và 10% thống kê có cả hai; hai thành phần thống kê dùng cận dưới đã chuẩn hóa. Điểm cuối chuẩn hóa 0–100. Nếu hòa, ưu tiên thứ tự số tăng dần.

Điểm 100 nghĩa là đứng đầu tương đối của lần tính, không có nghĩa chắc chắn trúng. Các tỷ lệ của cặp đứng đầu là tỷ lệ **trong mẫu đã được dùng tuyển chọn**, nên không nên xem là thành tích dự báo độc lập. Không có tối ưu gấp thếp, tăng điểm sau thua hoặc tự động đánh.

## Backtest theo thời gian

Bắt đầu sau 60 kỳ; tại mỗi ngày, phân tích lại chỉ với kết quả trước đó, dùng cùng cấu hình cửa sổ/ngưỡng và cùng thuật toán với bảng hiển thị. Ngày sau khoảng trống hoặc không đủ mẫu được bỏ qua, có đếm riêng. Cặp chọn ngày nào được ghi đúng cho ngày đó, không lấy cặp hôm nay soi ngược toàn bộ lịch sử.

Tổng điểm = 2 × điểm mỗi số. 100 điểm/số, mua 23.000đ/điểm, trả 80.000đ/điểm/nháy: tiền mua 4.600.000đ/kỳ. Tiền nhận tính tổng nháy của hai số. ROI = tổng lãi/lỗ / tổng tiền mua; Thắng/Thua theo lãi ròng, khác ngày có số xuất hiện. Chưa mô phỏng thiếu vốn, hạn mức hoặc phí ngoài đơn giá.

Bộ trọng số cố định trong bản này, không được chọn bằng kết quả tương lai. Tuy nhiên, nếu điều chỉnh cửa sổ/ngưỡng nhiều lần rồi chọn cấu hình có lịch sử đẹp nhất, vẫn có thiên lệch lựa chọn. Cần theo dõi tiếp những ngày mới chưa được dùng để chỉnh phương pháp. Không có cam kết đạt kết quả cao nhất.

## Lựa chọn đã lưu và xem trước

Cặp đầu tiên đủ điều kiện được ghi riêng cho từng ngày mục tiêu, kèm thời gian và cấu hình. Card **Cặp đã lưu** luôn dùng bản ghi này. Thay cấu hình chỉ thay Top 20 xem trước; kể cả khi cửa sổ mới thiếu mẫu, cặp đã lưu vẫn hiện. Các bản ghi không có trước 18:00 ngày mục tiêu được gắn Hồi cứu, không coi là dự báo thật trước giờ quay.

Nhật ký cặp chỉ đối chiếu kết quả/nháy; không cộng tiền vào Quản lý vốn. Sổ vốn thật vẫn yêu cầu người dùng nhập từng khoản với điểm/đơn giá của mình.

## Giới hạn triển khai

V2.1 bổ sung thuật toán, API, giao diện và xuất báo cáo. Kiểm thử sử dụng dữ liệu tổng hợp tách biệt. Chưa kiểm định lợi thế trên dữ liệu xổ số thực độc lập, chưa xác minh tải trực tiếp website và chưa xây dựng/kiểm tra EXE Windows. Các giới hạn V2 trong README tiếp tục áp dụng.
