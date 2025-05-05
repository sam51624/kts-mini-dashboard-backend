from datetime import datetime
import pytz

def is_greeting(text: str) -> bool:
    greetings = ["สวัสดี", "hello", "hi", "ทักทาย", "สวัสดีค่ะ", "สวัสดีครับ"]
    return any(greet in text.lower() for greet in greetings)

def generate_greeting_message() -> str:
    # ใช้เวลาตามโซนประเทศไทย
    tz = pytz.timezone("Asia/Bangkok")
    hour = datetime.now(tz).hour

    if 5 <= hour < 12:
        greeting = "สวัสดีตอนเช้าค่ะ"
    elif 12 <= hour < 17:
        greeting = "สวัสดีตอนบ่ายค่ะ"
    elif 17 <= hour < 22:
        greeting = "สวัสดีตอนเย็นค่ะ"
    else:
        greeting = "สวัสดีค่ะ"

    return f"""{greeting}
ดิฉันคือแอดมิน AI พร้อมให้บริการข้อมูลเบื้องต้นค่ะ
คุณสามารถส่งรหัสสินค้า หรือรูปภาพสินค้ามาให้ตรวจสอบได้นะคะ"""

# ✅ สำหรับเช็คว่าผู้ใช้ทักใหม่หรือไม่
GREETED_USERS = set()

def is_new_user(user_id: str) -> bool:
    return user_id not in GREETED_USERS

def mark_user_greeted(user_id: str):
    GREETED_USERS.add(user_id)
