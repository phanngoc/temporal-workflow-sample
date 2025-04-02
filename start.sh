#!/bin/bash

# Đảm bảo script sẽ dừng nếu có lỗi
set -e

echo "=== Workflow Orchestration với Temporal ==="
echo "Bắt đầu khởi động các services..."

# Kiểm tra Docker
if ! command -v docker &> /dev/null; then
    echo "Docker không được cài đặt. Vui lòng cài đặt Docker và thử lại."
    exit 1
fi

# Kiểm tra Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose không được cài đặt. Vui lòng cài đặt và thử lại."
    exit 1
fi

echo "1. Khởi động PostgreSQL và Temporal server..."
docker-compose up -d

echo "2. Chờ các services khởi động hoàn tất..."
sleep 10

echo "3. Cài đặt các gói phụ thuộc Python..."
pip install -r requirements.txt

echo "4. Khởi động worker (trong terminal riêng)..."
# Khởi động worker trong một terminal riêng
gnome-terminal -- bash -c "python -m app.workers.worker; exec bash" || \
    xterm -e "python -m app.workers.worker; exec bash" || \
    echo "Không thể mở terminal mới. Vui lòng khởi động worker thủ công: python -m app.workers.worker"

echo "5. Khởi động ứng dụng FastAPI..."
uvicorn app.main:app --reload

# Lưu ý: Script không kết thúc ở đây vì uvicorn sẽ chạy liên tục 