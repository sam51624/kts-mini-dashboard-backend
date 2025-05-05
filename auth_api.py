from flask import Blueprint, request, jsonify
from db_config import SessionLocal
from db_models import User
from sqlalchemy.exc import IntegrityError
import bcrypt

auth_api = Blueprint("auth_api", __name__)

# ✅ สมัครสมาชิกใหม่
@auth_api.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "กรุณากรอกข้อมูลให้ครบ"}), 400

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    session = SessionLocal()

    try:
        existing_user = session.query(User).filter(User.username == username).first()
        if existing_user:
            return jsonify({"error": "ชื่อผู้ใช้นี้มีอยู่แล้ว"}), 400

        user = User(username=username, password=hashed_pw)
        session.add(user)
        session.commit()
        return jsonify({"message": "สมัครสมาชิกสำเร็จ"}), 201

    except IntegrityError as e:
        session.rollback()
        print("⚠️ IntegrityError:", e)
        return jsonify({"error": "ชื่อผู้ใช้นี้มีอยู่แล้ว หรือข้อมูลไม่ถูกต้อง"}), 400

    except Exception as e:
        session.rollback()
        print("🔥 Unexpected error:", e)
        return jsonify({"error": "เกิดข้อผิดพลาดในระบบ", "detail": str(e)}), 500

    finally:
        session.close()


# ✅ เข้าสู่ระบบ
@auth_api.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "กรุณากรอกข้อมูลให้ครบ"}), 400

    session = SessionLocal()
    try:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            return jsonify({"error": "ชื่อผู้ใช้ไม่ถูกต้อง"}), 401

        if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            return jsonify({"message": "เข้าสู่ระบบสำเร็จ", "user_id": user.id}), 200
        else:
            return jsonify({"error": "รหัสผ่านไม่ถูกต้อง"}), 401

    except Exception as e:
        print("🔥 Unexpected error during login:", e)
        return jsonify({"error": "เกิดข้อผิดพลาดในระบบ", "detail": str(e)}), 500

    finally:
        session.close()

