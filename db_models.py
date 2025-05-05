# db_models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DECIMAL, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime  

Base = declarative_base()

# 🔐 ตารางผู้ใช้ (สำหรับระบบ Login/Register)
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# 📦 ตารางสินค้า
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    sku = Column(String(100), unique=True, nullable=False) 
    name = Column(Text)
    description = Column(Text)
    category = Column(String)
    cost_price = Column(DECIMAL(10, 2))
    price = Column(DECIMAL(10, 2))
    stock_quantity = Column(Integer)
    available_stock = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # ✅ ความสัมพันธ์กับรูปภาพ
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")

# 🖼️ ตารางรูปภาพสินค้า
class ProductImage(Base):
    __tablename__ = 'product_images'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    url = Column(Text, nullable=False)

    product = relationship("Product", back_populates="images")

# 👤 ตารางลูกค้า
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    phone = Column(String(20))
    line_user_id = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# 🧾 ตารางออเดอร์
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_number = Column(String(100))
    channel = Column(String(100))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    total_amount = Column(DECIMAL(10, 2))
    status = Column(String(50))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# 📄 รายการสินค้าในออเดอร์
class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    price = Column(DECIMAL(10, 2))
    cost_at_sale = Column(DECIMAL(10, 2))

# 🔁 การเปลี่ยนแปลงสต๊อก
class StockLog(Base):
    __tablename__ = 'stock_logs'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    change_qty = Column(Integer) 
    reason = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

