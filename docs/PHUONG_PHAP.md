# XSMB V2 PRO — phương pháp

## Dữ liệu và thời gian

Mỗi ngày chứa 27 đuôi hai chữ số, bảo toàn số trùng. Đặc trưng tần suất đếm số lần xuất hiện; đặc trưng presence đếm số kỳ có xuất hiện. “Gan” và “chu kỳ” tính theo **kỳ dữ liệu**, không thay thế bằng ngày lịch khi lịch sử thiếu. Lịch Việt Nam được dùng cho thời điểm tạo nhật ký. Nguồn chưa tải được không được thay bằng dữ liệu giả.

Nhật ký đóng băng 10 lựa chọn đầu tiên khi tính cho một kỳ; các card Bạch thủ/Song thủ/Top tại dashboard dùng đúng bản ghi này. Heatmap và bảng xếp hạng phía dưới là xem trước mô hình hiện tại, có thể khác khi thay trọng số; không tự sửa dự báo đã lưu. Nếu được ghi khi ngày mục tiêu đã qua, hoặc từ 18:00 ngày mục tiêu trở đi, bản ghi mang nhãn hồi cứu. Đây là quy ước thời điểm của ứng dụng, không phải chứng thực độc lập. Chưa có cơ chế ký số hoặc kiểm toán giờ máy.

## 30 chỉ báo

| STT | Chỉ báo | Cách tính |
|---|---|---|
|1–6|Tần suất 7, 14, 30, 60, 90, 180 kỳ|Tổng số nháy trong cửa sổ có sẵn|
|7–8|Presence 7, 30 kỳ|Số kỳ có ít nhất một nháy|
|9|Gan hiện tại|Số kỳ sau lần xuất hiện gần nhất; nếu chưa thấy, bằng số kỳ quan sát|
|10|Khoảng cách lớn nhất|Khoảng cách lớn nhất giữa hai kỳ xuất hiện liên tiếp|
|11–12|Chu kỳ trung bình, độ lệch|Trung bình và độ lệch chuẩn khoảng cách giữa các kỳ xuất hiện|
|13|Nháy kỳ cuối|Số lần xuất hiện ở kỳ cuối|
|14|Chuỗi xuất hiện|Số kỳ liên tiếp có xuất hiện tính lùi từ kỳ cuối|
|15–16|Đầu, đuôi 30 kỳ|Tần suất tổng của chữ số hàng chục/hàng đơn vị|
|17|Kép 30 kỳ|Tần suất nếu hai chữ số giống nhau; số không kép bằng 0|
|18|Đảo 14 kỳ|Tần suất số đảo trong 14 kỳ; số kép là chính nó|
|19|Đồng xuất hiện|Trung bình số kỳ cùng xuất hiện với mỗi số có ở kỳ cuối, tối đa 90 kỳ; bỏ tự ghép|
|20|Markov hai trạng thái|Ước lượng có/không xuất hiện kỳ tiếp sau trạng thái hiện tại; làm trơn (số chuyển sang có + 1)/(số lần trạng thái + 2)|
|21|Theo thứ|Nháy trung bình các kỳ cùng thứ với ngày dự báo|
|22|Theo tháng|Nháy trung bình các kỳ cùng tháng với ngày dự báo|
|23|Theo năm|Nháy trung bình năm dữ liệu gần nhất|
|24|Đặc biệt 30 kỳ|Số lần là đuôi giải ĐB|
|25|Gan ĐB|Số kỳ từ lần làm đuôi giải ĐB gần nhất|
|26|Momentum|Tần suất/ngày 7 kỳ trừ tần suất/ngày 30 kỳ|
|27|EMA|Trung bình mũ số nháy, alpha=0,1, khởi tạo 0|
|28|Nhiều nháy 30 kỳ|Số kỳ có hơn một nháy|
|29|Độ gần chu kỳ|exp(−abs(gan+1−chu kỳ TB)/(độ lệch+1)); cần ít nhất 2 khoảng cách|
|30|Entropy|Entropy nhị phân của có/không xuất hiện|

Khi không đủ cửa sổ, dùng số kỳ có sẵn. Không đủ khoảng cách thì chỉ báo chu kỳ bằng 0. Dữ liệu không có giải ĐB không được tự suy diễn giải ĐB; chỉ báo liên quan cần đọc cùng chất lượng nguồn.

K-means phân 100 số theo năm đặc trưng chuẩn hóa: tần suất 7/30 kỳ, gan, momentum, EMA. Bốn tâm khởi tạo xác định, tối đa 20 vòng. Số cụm chỉ là nhãn mô tả, không có thứ bậc “tốt/xấu”. Xiên 2 là số ngày cùng xuất hiện của hai số khác nhau, không mô phỏng cược xiên.

## Ensemble Score

Chuẩn hóa min–max từng đặc trưng trên 100 số ở thời điểm tính. Nếu cột không biến thiên thì cho 0. Tạo 8 nhóm:

- Frequency: 28/23/20/14/10/5% của các cửa sổ 7/14/30/60/90/180 kỳ.
- Recency: EMA.
- Cycle: độ gần chu kỳ.
- Transition: trung bình Markov và đồng xuất hiện.
- Calendar: trung bình theo thứ, tháng, năm.
- Structure: trung bình đầu, đuôi và tần suất ĐB.
- Reverse: tần suất số đảo.
- Momentum: thay đổi tần suất ngắn hạn.

Trọng số nhóm gốc lần lượt 30%, 15%, 10%, 15%, 10%, 8%, 5%, 7%. Tổng có trọng số tiếp tục chuẩn hóa về 0–100 để hiển thị. Điểm 100 chỉ là đứng đầu tương đối trong lần tính. Nếu bằng điểm, số nhỏ hơn đứng trước.

## Confidence

Confidence = 100 × (0,4 × min(số kỳ/365,1) + 0,3 × độ đầy đủ lịch + 0,3 × đồng thuận).

Độ đầy đủ = số ngày có dữ liệu / số ngày giữa ngày đầu và cuối. Đồng thuận = trung bình tỷ lệ giao nhau giữa Top 10 Ensemble đang dùng và Top 10 của mỗi nhóm đặc trưng. Chỉ số không dùng tần suất thắng để hiệu chuẩn nên **không được đọc là xác suất trúng**. Nó cũng không xác nhận tính đúng của dữ liệu được nhập tay.

## Backtest và Optimizer

Backtest khởi động 60 kỳ. Ở mỗi ngày đánh giá, chỉ tính đặc trưng từ các kỳ trước; nếu ngày đó không liền sau ngày dữ liệu trước, bỏ qua và đếm trong skipped_gaps. Tính tiền theo nháy, điểm cố định cho mỗi số, có tính giá mua của toàn bộ nhóm số.

Hit = tỷ lệ ngày có nháy trong nhóm đã chọn. Thắng/thua = số ngày có lãi/lỗ ròng. Drawdown = mức giảm lớn nhất từ đỉnh lãi lũy kế, bắt đầu đỉnh ở 0. ROI = lãi/tổng chi ×100. Không giả định điểm gấp thếp, tái đầu tư, giới hạn vốn hoặc phí ngoài đơn giá.

Optimizer tạo trước các đặc trưng walk-forward. Chia các kỳ đủ điều kiện theo thời gian thành 60% chọn trọng số, 20% xác nhận, 20% kiểm tra. Có ít nhất 120 kỳ đánh giá. Tập ứng viên gồm mô hình gốc, Frequency ở 15/20/25/30/35% (các nhóm khác co giãn giữ tỷ lệ), và trọng số ngẫu nhiên Dirichlet alpha=2. Seed 20260916 để tái lập.

Ứng viên có ROI cao nhất trên tập chọn được giữ; hòa ROI thì giữ ứng viên trước. Tập xác nhận và kiểm tra chỉ báo cáo, không chọn lại mô hình. Các tập sau được dự báo tuần tự, có thể dùng kết quả đã xảy ra ở các ngày trước trong cùng tập để cập nhật đặc trưng, nhưng không thay trọng số. Đây là walk-forward với trọng số cố định.

Mỗi lần chạy lưu một mô hình; phải bấm Áp dụng để dùng cho dashboard. Dù gọi là tập kiểm tra, nếu người dùng chạy đi chạy lại rồi chọn bằng ROI tập này thì không còn là kiểm tra độc lập. Sử dụng ngày mới chưa xem để đánh giá tiếp.

## Tiền thực tế và báo cáo

Từng khoản giữ đơn giá riêng. Kết quả thủ công ưu tiên hơn dữ liệu nguồn. Chưa có dữ liệu đúng ngày không coi là 0 nháy. Không có dự đoán AI nào tự sinh khoản thực tế.

Tổng hợp tuần dùng ISO week-year. Bộ lọc ngày bao gồm cả hai đầu. Vốn đầu kỳ = vốn ban đầu + dòng tiền các khoản trước khoảng lọc; vốn khả dụng = vốn đầu kỳ + tiền nhận − tiền mua (kể cả khoản đang chờ). ROI chỉ tính tiền mua của khoản đã có kết quả.

Nhật ký tính tiền mô phỏng theo thông số hiện tại khi xem/xuất; không đại diện khoản đã đặt và không ghi nhận đơn giá lịch sử. Sổ thực tế mới là nơi lưu điểm/đơn giá thực từng khoản. Báo cáo sổ và vốn theo khoảng lọc; backtest theo lần chạy hoàn tất gần nhất.

## Nguồn

Adapter cấu hình cho [Đại Phát](https://xosodaiphat.com/), [Minh Ngọc](https://www.minhngoc.net.vn/ket-qua-xo-so/mien-bac.html), [Xổ số KT](https://xskt.com.vn/xsmb) và [KQXS](https://ketqua.net/xo-so-mien-bac.php). Có thể cần chỉnh adapter khi website đổi cấu trúc, địa chỉ hoặc chặn truy cập. Tình trạng tải trực tiếp chưa được xác minh trong môi trường xây dựng; xem README.
