from flask import Blueprint, request, jsonify
from db_config import SessionLocal
from db_models import Product, ProductImage
from sqlalchemy.exc import SQLAlchemyError

product_api = Blueprint('product_api', __name__)

# 🔍 ดึงสินค้าทั้งหมด
@product_api.route('/products', methods=['GET'])
def get_all_products():
    session = SessionLocal()
    try:
        products = session.query(Product).all()
        result = [
            {
                "sku": p.sku,
                "name": p.name,
                "price": float(p.price),
                "stock_quantity": p.stock_quantity,
                "images": [img.url for img in p.images]
            }
            for p in products
        ]
        return jsonify(result), 200
    finally:
        session.close()

# ➕ เพิ่มสินค้าใหม่
@product_api.route('/products', methods=['POST'])
def add_product():
    data = request.json
    session = SessionLocal()

    # ✅ Validation เบื้องต้น
    sku = data.get("sku", "").strip()
    name = data.get("name", "").strip()
    price = data.get("price", None)

    if not sku:
        return jsonify({"error": "กรุณาระบุรหัสสินค้า (SKU)"}), 400
    if not name or len(name) < 3:
        return jsonify({"error": "ชื่อสินค้าต้องมีอย่างน้อย 3 ตัวอักษร"}), 400
    if price is None:
        return jsonify({"error": "กรุณาระบุราคาสินค้า"}), 400
    try:
        price = float(price)
        if price < 0:
            return jsonify({"error": "ราคาสินค้าต้องไม่ติดลบ"}), 400
    except ValueError:
        return jsonify({"error": "ราคาสินค้าต้องเป็นตัวเลข"}), 400

    try:
        product = Product(
            sku=sku,
            name=name,
            description=data.get("description", ""),
            category=data.get("category", ""),
            cost_price=float(data.get("cost_price", 0)),
            price=price,
            stock_quantity=int(data.get("stock_quantity", 0)),
            available_stock=int(data.get("available_stock", 0)),
            image_url=""
        )

        # ✅ เพิ่มรูปภาพถ้ามี
        image_urls = data.get("images", [])
        for url in image_urls:
            product.images.append(ProductImage(url=url))

        session.add(product)
        session.commit()
        return jsonify({"message": "เพิ่มสินค้าสำเร็จ ✅", "product_id": product.id}), 201

    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

# 📦 ดึงข้อมูลสินค้าแค่ 1 รายการตาม SKU
@product_api.route('/products/<sku>', methods=['GET'])
def get_product_by_sku(sku):
    session = SessionLocal()
    try:
        product = session.query(Product).filter(Product.sku == sku).first()
        if product:
            return jsonify({
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "cost_price": float(product.cost_price),
                "price": float(product.price),
                "stock_quantity": product.stock_quantity,
                "available_stock": product.available_stock,
                "images": [img.url for img in product.images],
                "created_at": product.created_at.strftime("%Y-%m-%d %H:%M:%S") if product.created_at else None
            }), 200
        else:
            return jsonify({"error": "ไม่พบสินค้า"}), 404
    finally:
        session.close()

