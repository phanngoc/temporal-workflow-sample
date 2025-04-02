from datetime import timedelta
from temporalio import workflow, activity
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.models.order import Order, OrderStatus, FailureReason
from app.schemas.order import OrderCreate, OrderResponse

# Activities

@activity.defn
async def validate_order(db: Session, order_id: int) -> Dict[str, Any]:
    """
    Validates the order by checking inventory, address, and price
    """
    print(f"Validating order {order_id}")
    
    # Lấy order từ database
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"success": False, "reason": "Order not found"}
    
    # Cập nhật trạng thái
    order.status = OrderStatus.VALIDATING
    db.commit()
    
    # Kiểm tra inventory (mô phỏng)
    has_inventory = order.quantity <= 100  # giả định tối đa 100 sản phẩm
    
    # Kiểm tra địa chỉ (mô phỏng)
    has_valid_address = len(order.shipping_address) > 10
    
    # Kiểm tra giá (mô phỏng)
    is_price_valid = order.price > 0 and order.total_amount == order.price * order.quantity
    
    if not has_inventory or not has_valid_address or not is_price_valid:
        order.status = OrderStatus.FAILED
        order.failure_reason = FailureReason.VALIDATION_FAILED
        db.commit()
        return {
            "success": False, 
            "reason": "Validation failed: " + 
                     (f"Insufficient inventory. " if not has_inventory else "") +
                     (f"Invalid address. " if not has_valid_address else "") +
                     (f"Invalid price. " if not is_price_valid else "")
        }
    
    return {"success": True}

@activity.defn
async def process_payment(db: Session, order_id: int) -> Dict[str, Any]:
    """
    Processes the payment for the order
    """
    print(f"Processing payment for order {order_id}")
    
    # Lấy order từ database
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"success": False, "reason": "Order not found"}
    
    # Cập nhật trạng thái
    order.status = OrderStatus.PROCESSING_PAYMENT
    db.commit()
    
    # Mô phỏng xử lý thanh toán (thành công nếu tổng tiền < 1000)
    payment_success = order.total_amount < 1000
    
    if not payment_success:
        order.status = OrderStatus.FAILED
        order.failure_reason = FailureReason.PAYMENT_FAILED
        db.commit()
        return {"success": False, "reason": "Payment failed: Amount too large"}
    
    return {"success": True}

@activity.defn
async def ship_order(db: Session, order_id: int) -> Dict[str, Any]:
    """
    Ships the order to the customer
    """
    print(f"Shipping order {order_id}")
    
    # Lấy order từ database
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"success": False, "reason": "Order not found"}
    
    # Cập nhật trạng thái
    order.status = OrderStatus.SHIPPING
    db.commit()
    
    # Mô phỏng gửi hàng (thành công nếu địa chỉ có chứa "Vietnam")
    shipping_success = "Vietnam" in order.shipping_address
    
    if not shipping_success:
        order.status = OrderStatus.FAILED
        order.failure_reason = FailureReason.SHIPPING_FAILED
        db.commit()
        return {"success": False, "reason": "Shipping failed: Invalid address"}
    
    return {"success": True}

@activity.defn
async def send_confirmation(db: Session, order_id: int) -> Dict[str, Any]:
    """
    Sends order confirmation to the customer
    """
    print(f"Sending confirmation for order {order_id}")
    
    # Lấy order từ database
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"success": False, "reason": "Order not found"}
    
    # Cập nhật trạng thái
    order.status = OrderStatus.SENDING_CONFIRMATION
    db.commit()
    
    # Mô phỏng gửi xác nhận (luôn thành công)
    
    # Đánh dấu đơn hàng đã hoàn thành
    order.status = OrderStatus.COMPLETED
    db.commit()
    
    return {"success": True}

@workflow.defn
class OrderWorkflow:
    def __init__(self):
        self.order_id: Optional[int] = None
    
    @workflow.run
    async def run(self, db: Session, order_id: int) -> OrderResponse:
        self.order_id = order_id
        
        # Step 1: Validate Order
        validation_result = await workflow.execute_activity(
            validate_order,
            args=[db, order_id],
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        if not validation_result["success"]:
            # Order failed validation
            print(f"Order {order_id} failed validation: {validation_result['reason']}")
            return self._get_order_response(db)
        
        # Step 2: Process Payment
        payment_result = await workflow.execute_activity(
            process_payment,
            args=[db, order_id],
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        if not payment_result["success"]:
            # Payment failed
            print(f"Order {order_id} payment failed: {payment_result['reason']}")
            return self._get_order_response(db)
        
        # Step 3: Ship Order
        shipping_result = await workflow.execute_activity(
            ship_order,
            args=[db, order_id],
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        if not shipping_result["success"]:
            # Shipping failed
            print(f"Order {order_id} shipping failed: {shipping_result['reason']}")
            return self._get_order_response(db)
        
        # Step 4: Send Confirmation
        confirmation_result = await workflow.execute_activity(
            send_confirmation,
            args=[db, order_id],
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        if not confirmation_result["success"]:
            # Confirmation failed (không cần cập nhật trạng thái thất bại vì đã thành công đến bước này)
            print(f"Order {order_id} confirmation failed but order is still completed")
        
        # Order completed successfully
        return self._get_order_response(db)
    
    def _get_order_response(self, db: Session) -> OrderResponse:
        order = db.query(Order).filter(Order.id == self.order_id).first()
        return OrderResponse.model_validate(order) 