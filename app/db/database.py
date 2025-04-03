from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load biến môi trường từ file .env
load_dotenv('../.env')

# Lấy DATABASE_URL từ biến môi trường hoặc sử dụng giá trị mặc định
DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/temporal_auth"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
print('SQLALCHEMY_DATABASE_URL', SQLALCHEMY_DATABASE_URL)

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError(
        "DATABASE_URL không được cấu hình. "
        "Vui lòng thiết lập biến môi trường DATABASE_URL trong file .env "
        f"hoặc sử dụng giá trị mặc định: {DEFAULT_DATABASE_URL}"
    )

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    # Kiểm tra kết nối
    with engine.connect() as conn:
        pass
except Exception as e:
    raise Exception(
        f"Không thể kết nối đến database. Lỗi: {str(e)}. "
        f"URL đang sử dụng: {SQLALCHEMY_DATABASE_URL}"
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 