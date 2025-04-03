from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash
from app.db.database import SessionLocal, engine
from app.models import user, order as order_model

def seed_users(db: Session):
    # Kiểm tra nếu bảng users đã có dữ liệu
    user_count = db.query(User).count()
    if user_count > 0:
        print(f"Đã có {user_count} users trong database, bỏ qua seed.")
        return
    
    # Tạo user mẫu
    users = [
        {
            "email": "user1@example.com",
            "username": "user1",
            "hashed_password": get_password_hash("password123"),
            "is_active": True
        },
        {
            "email": "user2@example.com",
            "username": "user2",
            "hashed_password": get_password_hash("password123"),
            "is_active": True
        },
        {
            "email": "admin@example.com",
            "username": "admin",
            "hashed_password": get_password_hash("admin123"),
            "is_active": True
        }
    ]
    
    # Thêm users vào database
    for user_data in users:
        db_user = User(**user_data)
        db.add(db_user)
    
    # Commit các thay đổi
    db.commit()
    print("Đã seed thành công dữ liệu users!")

def main():
    # Đảm bảo các bảng đã được tạo
    user.Base.metadata.create_all(bind=engine)
    order_model.Base.metadata.create_all(bind=engine)
    
    # Khởi tạo session
    db = SessionLocal()
    try:
        # Seed dữ liệu
        seed_users(db)
    finally:
        db.close()

if __name__ == "__main__":
    main() 