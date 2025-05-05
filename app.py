from flask import Flask, request
import json
import requests
from flask_cors import CORS

from ocr_utils import extract_text_from_image
from welcome_handler import is_greeting, generate_greeting_message, is_new_user, mark_user_greeted
from db_utils import get_product_by_sku
from product_api import product_api
from order_api import order_api

app = Flask(__name__)
CORS(app)

LINE_CHANNEL_ACCESS_TOKEN = "qwzQAyLRTVcsHmcxBUvyrSojIDdxm4tO8Wl/LWEtfUARGP/ntFGSblJL/wM958SoBnyWRFtWK13Un6hcZxXk/BqM8H5FjjJpT40orkVVLJeoKCk6Aebsu8yPT4Yw+9lOV8ZWnklsQ5ueLSsIkNBCowdB04t89/1O/w1cDnyilFU="
LINE_REPLY_ENDPOINT = "https://api.line.me/v2/bot/message/reply"
LINE_CONTENT_ENDPOINT = "https://api-data.line.me/v2/bot/message/{}/content"

def classify_intent(text: str) -> str:
    text = text.lower()
    if "ใบเสนอราคา" in text or "quote" in text or "เสนอราคา" in text:
        return "quotation"
    elif "มีของไหม" in text or "ของหมด" in text or "สต๊อก" in text:
        return "check_stock"
    else:
        return "search_product"

def reply_line(reply_token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post(LINE_REPLY_ENDPOINT, headers=headers, data=json.dumps(body))

def get_line_image(message_id):
    headers = {"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
    url = LINE_CONTENT_ENDPOINT.format(message_id)
    response = requests.get(url, headers=headers)
    return response.content

@app.route("/webhook", methods=["POST"])
def webhook():
    event_data = request.json
    for event in event_data.get("events", []):
        if event["type"] == "message":
            reply_token = event["replyToken"]
            if event["message"]["type"] == "text":
                user_text = event["message"]["text"].strip()
                user_id = event["source"].get("userId")

                if is_greeting(user_text) and user_id and is_new_user(user_id):
                    message = generate_greeting_message()
                    reply_line(reply_token, message)
                    mark_user_greeted(user_id)
                    return "OK", 200

                intent = classify_intent(user_text)
                if intent in ["search_product", "check_stock"]:
                    product = get_product_by_sku(user_text)
                    if product:
                        message = (
                            f"🔎 รหัส: {product.sku}\n"
                            f"📦 สินค้า: {product.name}\n"
                            f"💰 ราคา: {product.price} บาท\n"
                            f"📊 คงเหลือ: {product.stock_quantity} ชิ้น"
                        )
                    else:
                        message = "ขออภัยค่ะ ไม่พบข้อมูลสินค้าที่คุณสอบถามมาเลยค่ะ 🙏"
                elif intent == "quotation":
                    message = "📄 กรุณาระบุรหัสสินค้าและจำนวน เราจะจัดทำใบเสนอราคาให้ค่ะ 🙏"
                reply_line(reply_token, message)

            elif event["message"]["type"] == "image":
                image_id = event["message"]["id"]
                image_bytes = get_line_image(image_id)
                results = extract_text_from_image(image_bytes)
                if results:
                    sku = results[0].get("sku")
                    name = results[0].get("name")
                    if sku:
                        product = get_product_by_sku(sku)
                        if product:
                            message = (
                                f"🔎 รหัส: {product.sku}\n"
                                f"📦 สินค้า: {product.name}\n"
                                f"💰 ราคา: {product.price} บาท\n"
                                f"📊 คงเหลือ: {product.stock_quantity} ชิ้น"
                            )
                        else:
                            message = f"❌ ไม่พบรหัสสินค้า {sku} ในระบบค่ะ"
                    elif name:
                        message = f"ระบบตรวจพบชื่อสินค้า: {name} แต่ยังไม่มีรหัส กรุณาส่งรหัสอีกครั้งค่ะ 🙏"
                    else:
                        message = "ขออภัยค่ะ ระบบไม่สามารถอ่านข้อมูลจากภาพได้ค่ะ 😥"
                else:
                    message = "ไม่สามารถดึงข้อมูลจากภาพได้เลยค่ะ 😔"
                reply_line(reply_token, message)
    return "OK", 200

app.register_blueprint(product_api)
app.register_blueprint(order_api)

from auth_api import auth_api
app.register_blueprint(auth_api)

@app.route("/", methods=["GET"])
def index():
    return "✅ LINE AI Backend is running on Cloud Run", 200


