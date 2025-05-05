from flask import Blueprint, request, jsonify
from db_utils import create_order, get_or_create_customer_by_line_id
from db_models import Customer, Order, OrderItem
from sqlalchemy.exc import SQLAlchemyError
from db_config import SessionLocal

order_api = Blueprint('order_api', __name__)

# 🛒 สร้างคำสั่งซื้อใหม่
@order_api.route('/orders', methods=['POST'])
def create_new_order():
    data = request.json
    session = SessionLocal()
    try:
        customer = session.query(Customer).filter(Customer.line_user_id == data["line_user_id"]).first()
        if not customer:
            customer = Customer(
                line_user_id=data["line_user_id"],
                name=data.get("name")
            )
            session.add(customer)
            session.flush()

        total = sum(item['price'] * item['quantity'] for item in data["items"])
        order = Order(
            order_number=data["order_number"],
            channel=data.get("channel", "line"),
            customer_id=customer.id,
            total_amount=total,
            status='new'
        )
        session.add(order)
        session.flush()

        for item in data["items"]:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                price=item["price"],
                cost_at_sale=item.get("cost_at_sale", 0)
            )
            session.add(order_item)

        session.commit()

        return jsonify({
            "message": "สร้างออเดอร์สำเร็จ ✅",
            "order_id": order.id
        }), 201

    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

# 📦 ดึงออเดอร์ทั้งหมด
@order_api.route('/orders', methods=['GET'])
def get_all_orders():
    session = SessionLocal()
    try:
        orders = session.query(Order).all()
        result = []
        for order in orders:
            result.append({
                "order_number": order.order_number,
                "channel": order.channel,
                "customer_id": order.customer_id,
                "total_amount": float(order.total_amount),
                "status": order.status,
                "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else None
            })
        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

# 📦 ดึงรายละเอียดออเดอร์ + สินค้าในออเดอร์
@order_api.route('/orders/<int:order_id>', methods=['GET'])
def get_order_detail(order_id):
    session = SessionLocal()
    try:
        order = session.query(Order).filter(Order.id == order_id).first()
        if not order:
            return jsonify({"error": "ไม่พบออเดอร์"}), 404

        items = session.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        item_list = []
        for item in items:
            item_list.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": float(item.price),
                "cost_at_sale": float(item.cost_at_sale)
            })

        return jsonify({
            "order_id": order.id,
            "order_number": order.order_number,
            "channel": order.channel,
            "customer_id": order.customer_id,
            "total_amount": float(order.total_amount),
            "status": order.status,
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else None,
            "items": item_list
        }), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

# ✏️ อัปเดตสถานะออเดอร์
@order_api.route('/orders/<int:order_id>', methods=['PATCH'])
def update_order_status(order_id):
    session = SessionLocal()
    data = request.json
    try:
        order = session.query(Order).filter(Order.id == order_id).first()
        if not order:
            return jsonify({"error": "ไม่พบออเดอร์"}), 404

        new_status = data.get("status")
        if not new_status:
            return jsonify({"error": "กรุณาระบุสถานะใหม่ (status)"}), 400

        # ✅ ตรวจสอบว่าสถานะใหม่ต้องอยู่ในรายการที่กำหนด
        allowed_statuses = ["new", "waiting_payment", "paid", "shipped", "cancelled", "completed", "refunded"]
        if new_status not in allowed_statuses:
            return jsonify({"error": f"สถานะ '{new_status}' ไม่อนุญาต กรุณาเลือกจาก {allowed_statuses}"}), 400

        order.status = new_status
        session.commit()

        return jsonify({
            "message": f"อัปเดตสถานะออเดอร์เป็น {new_status} สำเร็จ ✅"
        }), 200

    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

