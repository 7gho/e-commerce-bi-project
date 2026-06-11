# Data Dictionary — TMDT_BI

Mô tả chi tiết các bảng trong Data Warehouse.

---

## Star Schema Diagram

```
                    ┌─────────────┐
                    │  dim_time   │
                    │─────────────│
                    │ time_key PK │
                    │ full_date   │
                    │ day         │
                    │ month       │
                    │ month_name  │
                    │ quarter     │
                    │ year        │
                    │ day_of_week │
                    │ is_weekend  │
                    └──────┬──────┘
                           │
┌──────────────┐    ┌──────┴──────────┐    ┌─────────────┐
│ dim_customer │    │   fact_orders   │    │ dim_product │
│──────────────│    │─────────────────│    │─────────────│
│customer_key  ├────│ order_key    PK │────┤ product_key │
│customer_id   │    │ invoice_no      │    │ stock_code  │
│country       │    │ customer_key FK │    │ description │
│region        │    │ product_key  FK │    │ category    │
└──────────────┘    │ time_key     FK │    └─────────────┘
                    │ region_key   FK │
                    │ quantity        │    ┌─────────────┐
                    │ unit_price      │    │ dim_region  │
                    │ total_amount    ├────│─────────────│
                    │ is_return       │    │ region_key  │
                    └─────────────────┘    │ country     │
                                           │ region      │
                                           │ continent   │
                                           └─────────────┘
```

---

## Bảng: `fact_orders`

| Cột | Kiểu | Mô tả |
|---|---|---|
| `order_key` | SERIAL PK | Surrogate key tự tăng |
| `invoice_no` | VARCHAR(20) | Mã hóa đơn gốc |
| `customer_key` | INT FK | Khóa ngoại → dim_customer |
| `product_key` | INT FK | Khóa ngoại → dim_product |
| `time_key` | INT FK | Khóa ngoại → dim_time |
| `region_key` | INT FK | Khóa ngoại → dim_region |
| `quantity` | INT | Số lượng sản phẩm |
| `unit_price` | NUMERIC(10,2) | Đơn giá (GBP) |
| `total_amount` | NUMERIC(12,2) | Thành tiền = quantity × unit_price |
| `is_return` | BOOLEAN | TRUE nếu là đơn hoàn trả (InvoiceNo bắt đầu 'C') |

---

## Bảng: `dim_customer`

| Cột | Kiểu | Mô tả |
|---|---|---|
| `customer_key` | SERIAL PK | Surrogate key |
| `customer_id` | VARCHAR(20) | ID khách hàng gốc; "GUEST" nếu không đăng nhập |
| `country` | VARCHAR(100) | Quốc gia của khách hàng |
| `region` | VARCHAR(50) | Vùng địa lý (Western Europe, North America…) |

---

## Bảng: `dim_product`

| Cột | Kiểu | Mô tả |
|---|---|---|
| `product_key` | SERIAL PK | Surrogate key |
| `stock_code` | VARCHAR(20) | Mã sản phẩm gốc |
| `description` | VARCHAR(255) | Tên sản phẩm (đã chuẩn hóa Title Case) |
| `category` | VARCHAR(100) | Phân loại sản phẩm |

---

## Bảng: `dim_time`

| Cột | Kiểu | Mô tả |
|---|---|---|
| `time_key` | SERIAL PK | Surrogate key |
| `full_date` | DATE | Ngày đầy đủ |
| `day` | SMALLINT | Ngày trong tháng (1–31) |
| `month` | SMALLINT | Tháng (1–12) |
| `month_name` | VARCHAR(15) | Tên tháng (January…December) |
| `quarter` | SMALLINT | Quý (1–4) |
| `year` | SMALLINT | Năm |
| `day_of_week` | VARCHAR(10) | Thứ trong tuần (Monday…Sunday) |
| `is_weekend` | BOOLEAN | TRUE nếu là cuối tuần |

---

## Bảng: `dim_region`

| Cột | Kiểu | Mô tả |
|---|---|---|
| `region_key` | SERIAL PK | Surrogate key |
| `country` | VARCHAR(100) | Tên quốc gia |
| `region` | VARCHAR(50) | Vùng (Western Europe, East Asia…) |
| `continent` | VARCHAR(50) | Châu lục (Europe, Asia, Americas…) |

---

## Views

| View | Mục đích |
|---|---|
| `vw_revenue_by_month` | Doanh thu, số đơn theo tháng/quý/năm |
| `vw_top_products` | Top sản phẩm theo doanh thu và số lượng |
| `vw_revenue_by_region` | Doanh thu theo quốc gia và vùng |
| `vw_customer_behavior` | Tần suất, giá trị mua của từng khách |
| `vw_return_analysis` | Tỷ lệ hoàn trả theo tháng |

---

## Nguồn Dataset

**Online Retail II** (UCI Machine Learning Repository)
- URL: https://archive.ics.uci.edu/dataset/502/online+retail+ii
- Thời gian: 01/12/2009 – 09/12/2011
- Dòng gốc: ~1,067,371
- Quốc gia: 43 quốc gia
- Cột: Invoice, StockCode, Description, Quantity, InvoiceDate, Price, Customer ID, Country
