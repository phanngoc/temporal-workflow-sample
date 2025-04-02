# Workflow Orchestration với Temporal

Ứng dụng mẫu sử dụng Python, FastAPI và Temporal.io để triển khai các quy trình nghiệp vụ dưới dạng workflows.

## Tính năng

1. **Xác thực người dùng**
   - Đăng ký
   - Đăng nhập

2. **Xử lý đơn hàng**
   - Quy trình xử lý đơn hàng hoàn chỉnh: xác thực đơn hàng, xử lý thanh toán, vận chuyển và xác nhận
   - Xử lý lỗi tại mỗi bước của quy trình

## Kiến trúc

Ứng dụng sử dụng Temporal.io làm công cụ điều phối và theo dõi workflows. Ứng dụng được xây dựng với:

- **FastAPI**: API framework
- **SQLAlchemy**: ORM (Object-Relational Mapping)
- **Temporal**: Điều phối workflows
- **PostgreSQL**: Cơ sở dữ liệu

## Cài đặt

### Yêu cầu

- Python 3.10+
- Docker và Docker Compose
- PostgreSQL

### Bước 1: Cài đặt các gói phụ thuộc

```bash
pip install -r requirements.txt
```

### Bước 2: Khởi động dịch vụ với Docker Compose

```bash
docker-compose up -d
```

Lệnh này sẽ khởi động:
- PostgreSQL
- Temporal server

### Bước 3: Khởi động worker

```bash
python -m app.workers.worker
```

### Bước 4: Chạy ứng dụng

```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Xác thực

- **POST /api/auth/register**: Đăng ký người dùng mới
  ```json
  {
    "email": "user@example.com",
    "username": "username",
    "password": "password"
  }
  ```

- **POST /api/auth/login**: Đăng nhập
  ```json
  {
    "email": "user@example.com",
    "username": "username",
    "password": "password"
  }
  ```

### Đơn hàng

- **POST /api/orders**: Tạo đơn hàng mới
  ```json
  {
    "product_name": "Product Name",
    "quantity": 2,
    "price": 100.0,
    "shipping_address": "123 Street, District, Vietnam"
  }
  ```

- **GET /api/orders**: Lấy danh sách đơn hàng

- **GET /api/orders/{order_id}**: Lấy thông tin đơn hàng

## Workflow Đơn hàng

Workflow đơn hàng bao gồm các bước sau:

1. **Xác thực đơn hàng (ValidateOrder Activity)**
   - Kiểm tra tồn kho
   - Xác thực địa chỉ
   - Kiểm tra giá

2. **Xử lý thanh toán (ProcessPayment Activity)**
   - Xử lý thanh toán 

3. **Vận chuyển đơn hàng (ShipOrder Activity)**
   - Gửi đơn hàng đến địa chỉ khách hàng

4. **Gửi xác nhận (SendConfirmation Activity)**
   - Gửi email xác nhận đơn hàng thành công

5. **Kết thúc (OrderCompleted hoặc OrderFailed)**
   - Đơn hàng hoàn thành thành công hoặc thất bại

## Phát triển

1. Thêm tính năng xác thực JWT cho các API endpoints
2. Thêm tính năng quản lý sản phẩm
3. Thêm tính năng tracking đơn hàng

