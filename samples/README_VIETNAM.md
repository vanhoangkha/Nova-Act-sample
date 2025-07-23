# Nova Act Samples - Phiên bản Việt Nam

Bộ sưu tập mẫu Nova Act được tùy chỉnh cho thị trường Việt Nam, bao gồm các trang web thương mại điện tử, tin tức, việc làm và bất động sản phổ biến tại Việt Nam.

## 🇻🇳 Tính năng dành cho thị trường Việt Nam

- **Hỗ trợ tiếng Việt**: Tất cả mẫu đều sử dụng tiếng Việt trong giao tiếp với Nova Act
- **Trang web Việt Nam**: Tích hợp với các trang web phổ biến tại Việt Nam
- **Đơn vị tiền tệ VND**: Xử lý giá cả theo đơn vị Việt Nam Đồng
- **Văn hóa địa phương**: Tính năng phong thủy, pháp lý bất động sản Việt Nam

## 📁 Cấu trúc mẫu

```
samples/
├── ecommerce/                    # Thương mại điện tử
│   ├── vietnam_price_monitor.py          # Theo dõi giá sản phẩm
│   └── vietnam_competitor_analysis.py    # Phân tích đối thủ cạnh tranh
├── data_extraction/              # Trích xuất dữ liệu
│   ├── vietnam_news_aggregator.py        # Tổng hợp tin tức
│   └── vietnam_job_market_analyzer.py    # Phân tích thị trường việc làm
├── real_estate/                  # Bất động sản
│   └── vietnam_property_analyzer.py      # Phân tích thị trường BĐS
└── README_VIETNAM.md            # Tài liệu này
```

## 🛒 Thương mại điện tử

### Theo dõi giá sản phẩm (`vietnam_price_monitor.py`)
- **Trang web hỗ trợ**: Shopee, Lazada, Tiki, Sendo
- **Tính năng**:
  - Theo dõi giá sản phẩm theo thời gian thực
  - Phân tích khuyến mãi và giảm giá
  - Báo cáo deal tốt nhất
  - Hỗ trợ đơn vị VND

```python
# Ví dụ sử dụng
vietnam_products = [
    {'url': 'https://shopee.vn/product-url', 'expected_name': 'iPhone 15'},
    {'url': 'https://tiki.vn/product-url', 'expected_name': 'Laptop Dell'}
]

monitor = VietnamPriceMonitor(vietnam_products)
prices = monitor.monitor_prices()
```

### Phân tích đối thủ cạnh tranh (`vietnam_competitor_analysis.py`)
- **Trang web hỗ trợ**: Shopee, Lazada, Tiki, Sendo
- **Tính năng**:
  - So sánh sản phẩm trên nhiều sàn
  - Phân tích đánh giá và lượt bán
  - Khuyến nghị mua sắm thông minh
  - Báo cáo chi tiết bằng tiếng Việt

## 📈 Trích xuất dữ liệu

### Tổng hợp tin tức (`vietnam_news_aggregator.py`)
- **Nguồn tin**: VnExpress, Tuoi Tre, Thanh Nien, Dan Tri
- **Tính năng**:
  - Tổng hợp tin tức từ nhiều nguồn
  - Phân tích cảm xúc (tích cực/tiêu cực/trung tính)
  - Xác định chủ đề nổi bật
  - Thống kê theo chuyên mục

```python
# Ví dụ sử dụng
vietnam_news_sources = [
    {'name': 'VnExpress', 'url': 'https://vnexpress.net'},
    {'name': 'Tuoi Tre', 'url': 'https://tuoitre.vn'}
]

aggregator = VietnamNewsAggregator()
articles = aggregator.aggregate_vietnam_news("công nghệ AI", vietnam_news_sources)
```

### Phân tích thị trường việc làm (`vietnam_job_market_analyzer.py`)
- **Trang web**: TopCV, VietnamWorks, CareerBuilder, ITviec
- **Tính năng**:
  - Phân tích mức lương theo khu vực
  - Kỹ năng được yêu cầu nhiều nhất
  - Xu hướng tuyển dụng theo công ty
  - Phân tích quyền lợi và phúc lợi

## 🏠 Bất động sản

### Phân tích thị trường BĐS (`vietnam_property_analyzer.py`)
- **Trang web**: Batdongsan.com.vn, Nhadat24h.net, Alonhadat.com.vn
- **Tính năng**:
  - Phân tích giá theo quận/huyện
  - Tình trạng pháp lý (sổ đỏ, sổ hồng)
  - Yếu tố phong thủy (hướng nhà)
  - Tìm BĐS có giá trị tốt nhất

```python
# Ví dụ sử dụng
search_criteria = {
    'location': 'Quận 1, TP. Hồ Chí Minh',
    'min_price': '3 tỷ',
    'max_price': '8 tỷ',
    'property_type': 'nhà riêng'
}

analyzer = VietnamRealEstateAnalyzer()
properties = analyzer.analyze_vietnam_market(search_criteria, vietnam_sites)
```

## 🚀 Cách sử dụng

### 1. Cài đặt
```bash
pip install nova-act
pip install -r samples/requirements.txt
```

### 2. Thiết lập API Key
```bash
export NOVA_ACT_API_KEY="your_api_key"
```

### 3. Chạy mẫu
```bash
# Theo dõi giá sản phẩm
python samples/ecommerce/vietnam_price_monitor.py

# Tổng hợp tin tức
python samples/data_extraction/vietnam_news_aggregator.py

# Phân tích việc làm
python samples/data_extraction/vietnam_job_market_analyzer.py

# Phân tích bất động sản
python samples/real_estate/vietnam_property_analyzer.py
```

## 🔧 Tùy chỉnh cho doanh nghiệp

### Thay đổi trang web mục tiêu
```python
vietnam_sites = [
    {'name': 'Trang web của bạn', 'url': 'https://yoursite.vn'}
]
```

### Tùy chỉnh mô hình dữ liệu
```python
class YourVietnamDataModel(BaseModel):
    your_field: str
    price_vnd: float  # Giá bằng VND
    location_vietnam: str  # Địa điểm Việt Nam
```

### Điều chỉnh phân tích
```python
def your_vietnam_analysis(self, data):
    # Logic phân tích riêng cho thị trường Việt Nam
    pass
```

## 💡 Lưu ý quan trọng

### Tuân thủ pháp luật
- Tôn trọng robots.txt của các trang web
- Tuân thủ điều khoản sử dụng
- Thực hiện crawl có trách nhiệm

### Tối ưu hiệu suất
- Sử dụng max_workers phù hợp
- Thêm delay giữa các request
- Giám sát việc sử dụng bộ nhớ

### Bảo mật
- Không hardcode thông tin nhạy cảm
- Sử dụng biến môi trường cho API key
- Cẩn thận với dữ liệu xác thực

## 📊 Báo cáo mẫu

Tất cả mẫu đều tạo ra báo cáo JSON chi tiết bằng tiếng Việt:

```json
{
  "analysis_date": "2024-01-15T10:30:00",
  "summary": {
    "total_items": 50,
    "success_rate": 95.5
  },
  "vietnam_specific_insights": [
    "Thông tin phân tích dành riêng cho thị trường Việt Nam"
  ],
  "recommendations": [
    "Khuyến nghị cụ thể cho người dùng Việt Nam"
  ]
}
```

## 🤝 Đóng góp

Để thêm mẫu mới cho thị trường Việt Nam:

1. Tạo thư mục mới cho danh mục của bạn
2. Tuân theo cấu trúc code hiện có
3. Sử dụng tiếng Việt trong giao tiếp với Nova Act
4. Thêm xử lý đơn vị VND và địa chỉ Việt Nam
5. Bao gồm tài liệu và ví dụ

## 📞 Hỗ trợ

Để được hỗ trợ:
- Email: nova-act@amazon.com
- Xem README.md chính để biết tài liệu Nova Act tổng quát
- Kiểm tra FAQ.md cho các câu hỏi thường gặp

## 🎯 Kế hoạch phát triển

- [ ] Thêm hỗ trợ cho các trang web Việt Nam khác
- [ ] Tích hợp API thanh toán Việt Nam
- [ ] Phân tích xu hướng tiêu dùng Việt Nam
- [ ] Hỗ trợ đa ngôn ngữ (Việt-Anh)
- [ ] Tối ưu cho mobile commerce Việt Nam

Các mẫu Nova Act cho thị trường Việt Nam cung cấp nền tảng mạnh mẽ để xây dựng các giải pháp tự động hóa web phù hợp với văn hóa và thị trường Việt Nam.
