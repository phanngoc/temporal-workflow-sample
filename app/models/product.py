from sqlalchemy import Column, Integer, String, Float, Boolean, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum
import datetime


# Thêm relationship ngược lại cho User
from app.models.user import User
User.orders = relationship("Order", back_populates="user")

# Tạo model cho sản phẩm
class ProductCategory(str, enum.Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    BOOKS = "books"
    FOOD = "food"
    OTHER = "other"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    stock_quantity = Column(Integer, default=0)
    category = Column(String, default=ProductCategory.OTHER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) 