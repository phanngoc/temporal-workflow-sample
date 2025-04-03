from datetime import timedelta
from temporalio import workflow, activity
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List

from app.models.product import Product, ProductCategory
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.db.database import SessionLocal

# Activities

@activity.defn
async def create_product(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tạo sản phẩm mới trong hệ thống
    """
    print(f"Creating new product: {product_data['name']}")
    
    db = SessionLocal()
    try:
        # Tạo sản phẩm
        product = Product(
            name=product_data["name"],
            description=product_data["description"],
            price=product_data["price"],
            stock_quantity=product_data.get("stock_quantity", 0),
            category=product_data.get("category", ProductCategory.OTHER)
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        return {
            "success": True,
            "product_id": product.id
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "reason": f"Failed to create product: {str(e)}"
        }
    finally:
        db.close()

@activity.defn
async def update_product_stock(product_id: int, quantity_change: int) -> Dict[str, Any]:
    """
    Cập nhật số lượng tồn kho của sản phẩm
    """
    print(f"Updating stock for product {product_id} by {quantity_change}")
    
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return {"success": False, "reason": "Product not found"}
        
        # Kiểm tra số lượng tồn hợp lệ
        new_quantity = product.stock_quantity + quantity_change
        if new_quantity < 0:
            return {"success": False, "reason": "Insufficient stock"}
        
        # Cập nhật số lượng
        product.stock_quantity = new_quantity
        db.commit()
        
        return {"success": True, "current_stock": new_quantity}
    except Exception as e:
        db.rollback()
        return {"success": False, "reason": f"Failed to update stock: {str(e)}"}
    finally:
        db.close()

@activity.defn
async def check_low_stock_products(threshold: int = 10) -> Dict[str, Any]:
    """
    Kiểm tra và báo cáo các sản phẩm có lượng tồn kho thấp
    """
    print(f"Checking products with stock below {threshold}")
    
    db = SessionLocal()
    try:
        low_stock_products = db.query(Product).filter(
            Product.stock_quantity < threshold,
            Product.is_active == True
        ).all()
        
        result = []
        for product in low_stock_products:
            result.append({
                "id": product.id,
                "name": product.name,
                "current_stock": product.stock_quantity
            })
        
        return {
            "success": True,
            "low_stock_count": len(result),
            "products": result
        }
    finally:
        db.close()

# Workflows

@workflow.defn
class ProductCreateWorkflow:
    def __init__(self):
        self.product_id: Optional[int] = None
    
    @workflow.run
    async def run(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Workflow tạo sản phẩm mới
        """
        # Chỉ truyền primitive types qua workflow
        # Loại bỏ các loại dữ liệu phức tạp như datetime
        result = await workflow.execute_activity(
            create_product,
            args=[product_data],
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        if not result["success"]:
            return {"success": False, "reason": result["reason"]}
        
        self.product_id = result["product_id"]
        
        return {
            "success": True,
            "product_id": self.product_id,
            "message": f"Product '{product_data['name']}' created successfully"
        }

@workflow.defn
class ProductStockUpdateWorkflow:
    def __init__(self):
        self.product_id: Optional[int] = None
    
    @workflow.run
    async def run(self, product_id: int, quantity_change: int) -> Dict[str, Any]:
        """
        Workflow cập nhật số lượng tồn kho
        """
        self.product_id = product_id
        
        # Cập nhật số lượng tồn kho
        result = await workflow.execute_activity(
            update_product_stock,
            args=[product_id, quantity_change],
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        if not result["success"]:
            return {"success": False, "reason": result["reason"]}
        
        return {
            "success": True,
            "product_id": product_id,
            "current_stock": result["current_stock"],
            "message": f"Stock updated successfully"
        }

@workflow.defn
class ProductInventoryCheckWorkflow:
    @workflow.run
    async def run(self, threshold: int = 10) -> Dict[str, Any]:
        """
        Workflow kiểm tra tồn kho và tạo báo cáo
        """
        # Kiểm tra sản phẩm tồn kho thấp
        result = await workflow.execute_activity(
            check_low_stock_products,
            args=[threshold],
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        return result 