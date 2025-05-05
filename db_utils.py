# db_utils.py
from db_config import SessionLocal
from db_models import Product, Customer, Order, OrderItem
from sqlalchemy.exc import SQLAlchemyError

# 🔍 ค้นหาสินค้าด้วย SKU (Return แบบ JSON dict)
def get_product_by_sku(sku: str):
    session = SessionLocal()
    try:
        product = session.query(Product).filter(Product.sku == sku).first()
        if product:
            return {
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "cost_price": float(product.cost_price),
                "price": float(product.price),
                "stock_quantity": product.stock_quantity,
                "available_stock": product.available_stock,
                "image_url": product.image_url,
                "created_at": product.created_at.strftime("%Y-%m-%d %H:%M:%S") if product.created_at else None
            }
        else:
            return None
    finally:
        session.close()

# 🧾 เพิ่มออเดอร์ใหม่
def create_order(order_number, channel, customer_id, items: list):
    session = SessionLocal()
    try:
        total = sum(item['price'] * item['quantity'] for item in items)
        order = Order(
            order_number=order_number,
            channel=channel,
            customer_id=customer_id,
            total_amount=total,
            status='new'
        )
        session.add(order)
        session.flush()  # ให้ได้ order.id ก่อน

        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price=item['price'],
                cost_at_sale=item.get('cost_at_sale', 0)
            )
            session.add(order_item)

        session.commit()
        return order.id
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()

# 👤 ค้นหาหรือสร้างลูกค้าจาก LINE userId
def get_or_create_customer_by_line_id(line_user_id: str, name: str = None):
    session = SessionLocal()
    try:
        customer = session.query(Customer).filter(Customer.line_user_id == line_user_id).first()
        if not customer:
            customer = Customer(line_user_id=line_user_id, name=name)
            session.add(customer)
            session.commit()
        return customer
    finally:
        session.close()

