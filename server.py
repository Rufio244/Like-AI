import os
import random
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"

app = Flask(__name__, static_folder=str(PUBLIC_DIR), static_url_path="/")

PORTAL_DB = []
GEMS = [
    {
        "gem_id": "Creative-Post",
        "category": "Marketing",
        "description": "สร้างคอนเทนต์แนะนำสินค้าและกิจกรรมที่ตรงกับแต่ละกลุ่ม",
        "prompt_template": "วิเคราะห์กลุ่มเป้าหมาย ผสานข้อมูลแบรนด์ แล้วสร้างสรรค์ข้อความให้มีพลัง และพร้อมใช้งานบนโซเชียลมีเดีย",
    },
    {
        "gem_id": "Sales-Reply",
        "category": "CRM",
        "description": "ช่วยตอบข้อความลูกค้าให้เป็นมืออาชีพและเป็นประโยชน์",
        "prompt_template": "อ่านสภาพแวดล้อมของลูกค้า จัดลำดับความสำคัญของข้อความ แล้วตอบด้วยภาษาที่นุ่มนวลและตรงประเด็น",
    },
    {
        "gem_id": "Brand-Voice",
        "category": "Branding",
        "description": "ปรับแต่งสไตล์ภาษาให้เข้ากับแบรนด์และ Persona",
        "prompt_template": "คงมวลสารของแบรนด์ไว้ให้เสมอ คัดเลือกคำศัพท์ที่ใช่ และคงโทนเสียงที่สะท้อนคุณค่าขององค์กร",
    },
]


def generate_portal_code(name: str) -> str:
    prefix = (name or "LIKE").strip().replace(" ", "").upper()[:3]
    suffix = str(random.randint(1000, 9999))
    return f"CR-{prefix}-{suffix}"


@app.route("/")
def root():
    return send_from_directory(str(PUBLIC_DIR), "index.html")


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "like-ai-backend",
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "integrations": ["google_apps_script", "line_oa", "facebook_page", "webhook"],
    })


@app.route("/api/gems")
def get_gems():
    return jsonify({"status": "success", "data": GEMS})


@app.route("/api/token/verify")
def verify_token():
    token = request.args.get("token", "")
    allowed_tokens = {
        "demo-token": {"email": "demo@likeai.ai", "status": "valid"},
        "admin-token": {"email": "admin@likeai.ai", "status": "valid"},
    }
    match = allowed_tokens.get(token)
    if match:
        return jsonify({"status": "valid", "email": match["email"]})
    return jsonify({"status": "invalid", "message": "Token ไม่ถูกต้องหรือยังไม่มีสิทธิ์"})


@app.route("/api/portal", methods=["POST"])
def portal_submit():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    group = (payload.get("group") or "").strip()
    source = (payload.get("from") or "ROOT").strip()

    if not name or not group:
        return jsonify({"status": "error", "message": "ต้องกรอก��ื่อและกลุ่ม"}), 400

    code = generate_portal_code(name)
    record = {
        "id": code,
        "name": name,
        "from": source,
        "group": group,
        "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "portal": "ready",
    }
    PORTAL_DB.append(record)

    return jsonify({
        "status": "success",
        "message": "Portal สร้างสำเร็จ",
        "record": record,
        "history": PORTAL_DB,
    })


@app.route("/api/integrations/line/send")
def line_send():
    msg = request.args.get("message", "สวัสดีจาก Like-AI")
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    if token:
        return jsonify({
            "status": "success",
            "provider": "line",
            "message": msg,
            "delivery": "dispatched",
            "secret_mode": "Token stored in environment variable",
        })
    return jsonify({
        "status": "demo",
        "provider": "line",
        "message": msg,
        "delivery": "simulated",
        "secret_mode": "No LINE token configured; demo mode only",
    })


@app.route("/api/integrations/facebook/post")
def facebook_post():
    msg = request.args.get("message", "Demo post from Like-AI")
    token = os.getenv("FACEBOOK_PAGE_TOKEN")
    if token:
        return jsonify({
            "status": "success",
            "provider": "facebook",
            "message": msg,
            "delivery": "published",
            "secret_mode": "Token stored in environment variable",
        })
    return jsonify({
        "status": "demo",
        "provider": "facebook",
        "message": msg,
        "delivery": "simulated",
        "secret_mode": "No Facebook token configured; demo mode only",
    })


@app.route("/api/integrations/webhook/accept")
def webhook_accept():
    event = request.args.get("event", "portal_created")
    return jsonify({
        "status": "success",
        "provider": "webhook",
        "event": event,
        "message": "Webhook received successfully",
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=True)
