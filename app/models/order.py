from sqlalchemy import Column, Integer, String, Float, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum

class OrderStatus(str, enum.Enum):
    RECEIVED = "received"
    VALIDATING = "validating"
    PROCESSING_PAYMENT = "processing_payment"
    SHIPPING = "shipping"
    SENDING_CONFIRMATION = "sending_confirmation"
    COMPLETED = "completed"
    FAILED = "failed"

class FailureReason(str, enum.Enum):
    VALIDATION_FAILED = "validation_failed"
    PAYMENT_FAILED = "payment_failed"
    SHIPPING_FAILED = "shipping_failed"
    NONE = "none"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_name = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
    total_amount = Column(Float)
    shipping_address = Column(String)
    status = Column(String, default=OrderStatus.RECEIVED)
    failure_reason = Column(String, default=FailureReason.NONE)
    
    user = relationship("User", back_populates="orders")

# Thêm relationship ngược lại cho User
from app.models.user import User
User.orders = relationship("Order", back_populates="user") 