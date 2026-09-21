XSMB INTELLIGENCE STUDIO — V2.2 PRO
================================
Nâng cấp từ V1.3 của bạn. Giao diện mới mở trong trình duyệt trên chính máy,
địa chỉ http://127.0.0.1:<cổng>. Không đưa sổ cá nhân lên website.


MỚI TRONG V2.1 — CẦU LÔ TÔ & TUYỂN CHỌN CẶP
• Tab Cầu & cặp lô tô: lô rơi, kép rơi, đảo, đầu, đuôi, theo thứ,
  chuyển tiếp; số mẫu, tỷ lệ trong mẫu, cận dưới và chênh so với nền.
• Xếp hạng 4.950 cặp hai số khác nhau, hiển thị Top 20 và lý do.
• Song thủ đánh riêng: không nhầm tỷ lệ ít nhất một số với cả hai số.
• Cặp đầu tiên của mỗi kỳ được lưu cố định; thay cấu hình chỉ xem trước.
• Backtest chọn lại cặp mỗi ngày, chỉ dùng dữ liệu trước; tính nháy,
  lãi/lỗ, ROI và biểu đồ; xuất Excel/PDF/CSV.
• Cần ≥60 kỳ, ≥40 cặp ngày liên tiếp. Mặc định 180 kỳ / ≥20 mẫu mỗi cầu.
• Chưa có bằng chứng độc lập cho lợi thế dự báo; không bảo đảm trúng.
Hướng dẫn/công thức: docs/CAU_LO_TO.md.

SỬA LỖI KHÔNG NHẬN PY — BẢN FIX LAUNCHER
Bộ chạy và bộ tạo EXE tự tìm Python qua môi trường cũ, PATH, các thư mục
cài phổ biến và đăng ký cài đặt Windows. py chỉ là phương án dự phòng.
Nếu máy chưa cài Python, vẫn cần cài Python trước; quyền Administrator
không thay thế việc cài Python. Không tự tải hoặc cài Python lên máy.
Bản sửa launcher chưa được chạy xác minh bằng PowerShell trên Windows.

BẮT ĐẦU TRÊN WINDOWS
1. Giải nén toàn bộ ZIP vào thư mục có quyền ghi.
2. Cài Python 3.11 hoặc 3.12 từ python.org, không bắt buộc Python Launcher.
3. Nhấp đúp CHAY_UNG_DUNG.bat.
   Lần đầu cần Internet để tải thư viện; những lần sau dùng môi trường đã cài.
4. Giữ cửa sổ chạy mở. Để dừng, bấm “Đóng ứng dụng” trong dashboard.
   Chỉ đóng tab trình duyệt sẽ không dừng tiến trình nền.
5. Nếu trình duyệt không tự mở, sao chép địa chỉ 127.0.0.1 in trong cửa sổ chạy.

TẠO FILE EXE TRÊN WINDOWS
Nhấp đúp TAO_FILE_EXE.bat. Script cài thư viện, chạy kiểm thử rồi đóng gói.
Khi thành công, file nằm tại dist\XSMB_AI_Indicator_V2_2_PRO.exe.
Sau khi đóng gói, máy dùng EXE không cần Python.
Gói bạn nhận là mã nguồn hoàn chỉnh + bộ chạy/đóng gói; CHƯA chứa EXE.
Chưa biên dịch hay xác nhận chạy thực tế trên Windows.

DỮ LIỆU CŨ
Giữ cùng thư mục dữ liệu của V1.3:
%LOCALAPPDATA%\XSMB_AI_Indicator\xsmb.db
Lần chạy V2 đầu tiên tạo xsmb_before_v2.db nếu đã có cơ sở dữ liệu cũ.
V2 thêm bảng nhật ký/mô hình; không xóa sổ thắng/thua, kết quả hoặc dự báo cũ.
Đóng V1.3 trước khi mở V2. Không chép đè xsmb.db bằng dữ liệu thử nghiệm.
Nếu muốn giao diện V1.3: chạy python run_classic.py (cần Tcl/Tk).

CÁC MODULE
• Dashboard AI: Bạch thủ, Song thủ, Top 3/5/10, AI Score, heatmap 00–99,
  đồng hồ AI Confidence và bảng chi tiết.
• Phân tích: 30 chỉ báo; lọc từng số; sắp xếp chỉ báo; K-means 4 cụm;
  20 cặp xiên 2 đồng xuất hiện nhiều nhất trong tối đa 90 kỳ.
• Backtest PRO: Top 1/2/3/5/10, Hit, ROI, lãi/lỗ, ngày thắng/thua,
  sụt giảm lớn nhất và biểu đồ lũy kế. Nhóm số được chọn khi chạy.
• Quản lý vốn: sổ khoản thực tế, sửa/xóa, ngày/tuần/tháng/năm, lọc ngày,
  vốn ban đầu, vốn khả dụng, tiền nhận, lãi/lỗ, ROI, khoản chờ, biểu đồ.
• Nhật ký AI: lưu lựa chọn ĐẦU TIÊN mỗi kỳ, đối chiếu kết quả và số nháy.
  Tiền nhật ký là mô phỏng, tách hoàn toàn khỏi vốn thực tế.
• Đồ thị: lịch sử từng số, nháy từng kỳ hoặc lũy kế; zoom, pan, tooltip.
• AI Optimizer: 10–10.000 cấu hình, mặc định 2.000; chia theo thời gian
  60% chọn trọng số / 20% xác nhận / 20% kiểm tra. Có nút áp dụng mô hình.
• Dữ liệu: Đại Phát, Minh Ngọc, Xổ số KT, KQXS (Ketqua.net), CSV;
  nguồn lỗi hoặc sai ngày sẽ thử nguồn tiếp theo; chỉ lưu đủ 27 giải.
• Báo cáo: chọn nội dung và xuất Excel/PDF/CSV. Excel/PDF có biểu đồ
  khi dữ liệu phù hợp, font PDF hỗ trợ tiếng Việt.
• Giao diện: sidebar, card, dark/light mode, bố cục co giãn.

CÁCH TÍNH TIỀN
Điểm là số nguyên dương, áp dụng RIÊNG cho từng số.
Mặc định mua 23.000đ/điểm; trả 80.000đ/điểm/lần xuất hiện.
Tiền mua = số điểm × đơn giá mua.
Tiền nhận = số điểm × đơn giá trả × số nháy.
Lãi/lỗ = tiền nhận − tiền mua.
100 điểm: 0 nháy lỗ 2.300.000đ; 1 nháy lãi 5.700.000đ;
2 nháy lãi 13.700.000đ.
Trong backtest Top 5, 100 điểm/số: tiền mua mỗi kỳ = 11.500.000đ.
Hit là ngày có ít nhất một nháy, KHÔNG đồng nghĩa ngày có lãi.
ROI = tổng lãi/lỗ đã chốt / tổng tiền mua đã chốt × 100%.
Vốn khả dụng trừ cả tiền mua đang chờ; lãi/lỗ không tính khoản chờ là thua.
Vốn ban đầu không phải hạn mức tự chặn; phần mềm không đặt cược.

NHẬP SỔ THẮNG/THUA
Vào Quản lý vốn, điền ngày, số 00–99, điểm và đơn giá.
Số lần trúng để trống: tự đếm trong kết quả đã tải của đúng ngày.
Nhập 0: xác nhận thua; nhập 1, 2...: xác nhận số nháy thủ công.
Kết quả nhập tay được ưu tiên. Xóa ô này và lưu để tự đối chiếu lại.
Ngày chưa có kết quả vẫn “Chờ”; không tự kết luận thua.
Bấm Sửa ở dòng cần sửa; bấm Nhập mới để thoát chế độ sửa.
Đơn giá lưu riêng từng khoản, thay đơn giá khoản mới không đổi khoản cũ.

DỮ LIỆU CSV
Mẫu cột có thể tải trong tab Dữ liệu:
day,numbers,special_prize
• day: YYYY-MM-DD hoặc DD/MM/YYYY.
• numbers: đúng 27 số hai chữ số, cách nhau bằng dấu cách, cả ô trong
  dấu ngoặc kép; giữ số trùng vì dùng để tính nháy.
• special_prize: 5 chữ số, hoặc để trống nếu không có.
Đọc toàn bộ CSV và kiểm tra trước khi ghi. Ngày trùng đúng được bỏ qua;
ngày trùng nhưng khác kết quả sẽ dừng lần nhập, không ghi đè lịch sử.
CSV không có giải ĐB vẫn dùng được; các chỉ báo ĐB khi đó thiếu thông tin.
Muốn phân tích đầy đủ nên nhập giải ĐB ở tất cả các kỳ.

CÁC GIỚI HẠN ĐÃ BIẾT
• Chưa kiểm thử bản EXE trên Windows hay kiểm tra hình ảnh giao diện bằng
  trình duyệt thật trong môi trường xây dựng này. Kiểm thử DOM đã chạy,
  nhưng API Canvas được mô phỏng trong kiểm thử, không phải kiểm tra ảnh.
• Tải trực tiếp các website trong môi trường này bị timeout. Bộ chuyển
  nguồn và parser đã kiểm tra bằng fixture; không cam kết các website
  đang tương thích hoặc truy cập được từ mọi máy. KQXS có thể đổi tên miền.
• Kỳ phân tích là ngày sau dữ liệu mới nhất, không tự gọi dữ liệu cũ là
  “ngày mai”. Nếu thiếu kết quả mới, dashboard hiển thị cảnh báo.
• AI Score/Confidence không phải xác suất trúng. Không có tỷ lệ thắng,
  ROI dương hay mức lãi nào được cam kết.
• Optimizer tối ưu trọng số của thuật toán thống kê, không tạo AI có
  khả năng đảm bảo dự đoán. Thử nhiều lần cùng tập kiểm tra làm giảm
  tính độc lập của phép kiểm tra; nên đánh giá tiếp trên ngày mới.
• Backtest dùng điểm cố định và trọng số gốc V2, chưa xét hạn mức cược,
  thiếu vốn, nợ, phí ngoài đơn giá hay tăng/giảm điểm theo chuỗi.
• Nhật ký V2 bắt đầu khi dùng V2; không biến dự báo V1.3 cũ thành dự báo
  đã xác minh trước giờ quay. Bản ghi hồi cứu được gắn nhãn rõ ràng.
• Xóa khoản thực tế cần xác nhận và không có nút hoàn tác; sao lưu DB
  định kỳ sau khi đóng chương trình. File sao lưu trước V2 chỉ là mốc đầu.

TÀI LIỆU
Xem docs/PHUONG_PHAP.md và docs/KIEM_THU.md.
Chạy kiểm thử: python -m pip install -r requirements-dev.txt
               python -m pytest -q
Log vận hành: %LOCALAPPDATA%\XSMB_AI_Indicator\app_v2.log

MỚI TRONG V2.2 — DỰ ĐOÁN TỪ CẦU
Mở Dự đoán & soi cầu. Dashboard lấy bạch thủ / song thủ từ mô-đun này.
- 20 cầu ghép hai vị trí khác nhau của 5 chữ số giải đặc biệt.
- Pascal: cộng từng cặp chữ số liền nhau, lấy hàng đơn vị, lặp đến còn 2 chữ số; có cầu đảo.
- Kép từ tổng chữ số ĐB; lô rơi và chuyển tiếp có điều kiện (ít nhất 10 lần nguồn xuất hiện).
- Mỗi cầu được kiểm tra trên tối đa 60 kỳ đã kết thúc, ít nhất 30 mẫu.
- Đối chứng: số có tần suất cao nhất 30 kỳ trước, kiểm tra trên đúng cùng các ngày.
- Cầu được đánh dấu vượt đối chứng khi cận dưới Wilson 95% cao hơn tỷ lệ đúng của đối chứng.
- Gộp phiếu theo số; trong cùng một nhóm cầu chỉ lấy trọng số lớn nhất để giảm đếm trùng.
  Trọng số = cận dưới Wilson + 1 nếu vượt đối chứng. Ưu tiên số có cầu vượt đối chứng,
  sau đó điểm nhóm cộng lại; hòa điểm chọn số nhỏ hơn. Đây không phải xác suất.
- Khi chưa vượt đối chứng vẫn có thể hiển thị ứng viên THĂM DÒ. Số thứ hai của song thủ
  có thể là thăm dò ngay cả khi bạch thủ có tín hiệu; xem cột Bằng chứng cho từng số.
- Thiếu mẫu không tạo dự đoán. Không ghép chuyển tiếp qua ngày thiếu dữ liệu.
- Nhật ký dự đoán lưu lần đầu cho từng kỳ; tính lại không sửa bản đã lưu.
  Bản tạo sau thời điểm dự kiến quay được đánh dấu hồi cứu, không phải dự đoán trực tiếp.
- Backtest tính lại toàn bộ bộ chọn theo từng ngày, chỉ dùng dữ liệu trước ngày đó.
  Mặc định 100 điểm/mỗi số: bạch thủ 2.300.000đ/kỳ; song thủ 4.600.000đ/kỳ.
  Tiền nhận = số nháy × 100 × 80.000đ; lãi = tiền nhận − tiền mua.
  Không tăng điểm sau thua, không ghi tiền mô phỏng vào vốn thực tế, chưa mô phỏng hết vốn.
- Xuất nhật ký dự đoán CSV/Excel/PDF tại Xuất báo cáo.
Chỉ có chữ số đầy đủ của giải đặc biệt trong dữ liệu hiện tại. Không giả lập cầu vị trí
của các giải khác. Nếu CSV không có giải đặc biệt, các cầu ĐB không hoạt động.
Thử nhiều cầu dễ quá khớp; kết quả lịch sử không đảm bảo ngày tiếp theo và chưa chứng minh
lợi thế thực tế. Chưa kiểm định hiệu quả trên dữ liệu thực độc lập; cần theo dõi dự đoán
được ghi trước kỳ quay. Top 3/5/10, heatmap và đồng hồ cũ vẫn là thống kê tham khảo.
