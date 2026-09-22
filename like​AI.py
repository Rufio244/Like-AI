import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import requests
from flask import Flask, jsonify, request, render_template_string

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "likeai.db"
PORT = int(os.getenv("PORT", "8000"))

app = Flask(__name__)


# -----------------------------
# Database
# -----------------------------
def db_connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with db_connect() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS portals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                source TEXT NOT NULL,
                group_name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        db.commit()


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def json_error(message, status=400):
    return jsonify({
        "status": "error",
        "message": message
    }), status


# -----------------------------
# Embedded Frontend
# -----------------------------
HTML_PAGE = r"""
<!doctype html>
<html lang="th">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Like-AI Portal</title>
    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            font-family: Arial, Tahoma, sans-serif;
            background: #eef7ee;
            color: #203020;
        }

        .card {
            width: min(100%, 480px);
            background: white;
            border: 1px solid #dce9dc;
            border-radius: 18px;
            padding: 24px;
            box-shadow: 0 12px 40px #00000012;
        }

        h1 {
            margin-top: 0;
            font-size: 1.5rem;
        }

        .description {
            color: #607060;
            line-height: 1.5;
        }

        label {
            display: block;
            margin-top: 14px;
            margin-bottom: 6px;
            font-weight: bold;
        }

        input,
        button {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            font-size: 1rem;
        }

        input {
            border: 1px solid #cbdacb;
            background: #fbfefb;
        }

        button {
            border: 0;
            margin-top: 18px;
            background: #2e7d32;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }

        button:disabled {
            opacity: 0.6;
            cursor: wait;
        }

        #status,
        #result {
            margin-top: 16px;
            padding: 12px;
            border-radius: 10px;
            line-height: 1.6;
            white-space: pre-wrap;
        }

        #status {
            display: none;
            background: #edf7ed;
        }

        #result {
            min-height: 70px;
            background: #f7fbf7;
            border: 1px solid #dfebdf;
        }

        .error {
            background: #fff0f0 !important;
            color: #9d1c1c;
        }

        .copy-button {
            margin-top: 12px;
            background: #1565c0;
        }

        .health {
            margin-top: 15px;
            color: #557055;
            font-size: 0.85rem;
        }
    </style>
</head>
<body>
    <main class="card">
        <h1>🤖 Like-AI Portal</h1>
        <p class="description">
            ระบบ Portal แบบครบในไฟล์เดียว พร้อม API และฐานข้อมูล SQLite
        </p>

        <label for="name">ชื่อผู้ใช้ *</label>
        <input id="name" maxlength="120" placeholder="กรอกชื่อผู้ใช้">

        <label for="source">โค้ดต้นทาง</label>
        <input id="source" maxlength="120" placeholder="เช่น Cristal-ROOT">

        <label for="group">กลุ่ม / หมู่บ้าน *</label>
        <input id="group" maxlength="120" placeholder="กรอกกลุ่มหรือหมู่บ้าน">

        <button id="submitButton">สร้าง Portal</button>

        <div id="status"></div>
        <div id="result">ยังไม่มีรายการ</div>
        <div class="health" id="health">กำลังตรวจสอบระบบ...</div>
    </main>

<script>
const nameInput = document.getElementById("name");
const sourceInput = document.getElementById("source");
const groupInput = document.getElementById("group");
const submitButton = document.getElementById("submitButton");
const statusBox = document.getElementById("status");
const resultBox = document.getElementById("result");
const healthBox = document.getElementById("health");

function setStatus(message, error = false) {
    statusBox.textContent = message;
    statusBox.style.display = "block";
    statusBox.classList.toggle("error", error);
}

function addTextLine(parent, label, value) {
    const line = document.createElement("div");
    line.textContent = `${label}: ${value}`;
    parent.appendChild(line);
}

async function checkHealth() {
    try {
        const response = await fetch("/api/health");
        const data = await response.json();
        healthBox.textContent = data.status === "ok"
            ? "● Backend พร้อมใช้งาน"
            : "● Backend มีปัญหา";
    } catch (error) {
        healthBox.textContent = "● ติดต่อ Backend ไม่ได้";
    }
}

async function createPortal() {
    const payload = {
        name: nameInput.value.trim(),
        source: sourceInput.value.trim(),
        group: groupInput.value.trim()
    };

    if (!payload.name || !payload.group) {
        setStatus("กรุณากรอกชื่อและกลุ่มให้ครบ", true);
        return;
    }

    submitButton.disabled = true;
    setStatus("กำลังสร้าง Portal...");
    resultBox.textContent = "";

    try {
        const response = await fetch("/api/portal", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok || data.status !== "success") {
            setStatus(data.message || "สร้าง Portal ไม่สำเร็จ", true);
            return;
        }

        const record = data.record;
        const title = document.createElement("strong");
        title.textContent = "✅ สร้าง Portal สำเร็จ";
        resultBox.appendChild(title);

        addTextLine(resultBox, "รหัส", record.code);
        addTextLine(resultBox, "ชื่อ", record.name);
        addTextLine(resultBox, "กลุ่ม", record.group);
        addTextLine(resultBox, "ต้นทาง", record.source);
        addTextLine(resultBox, "เวลา", record.created_at);

        const copyButton = document.createElement("button");
        copyButton.className = "copy-button";
        copyButton.textContent = "คัดลอกรหัส Portal";
        copyButton.addEventListener("click", async () => {
            await navigator.clipboard.writeText(record.code);
            setStatus("คัดลอกรหัส Portal แล้ว");
        });

        resultBox.appendChild(copyButton);
        setStatus("ระบบพร้อมส่งข้อมูลต่อไปยังบริการภายนอก");
    } catch (error) {
        setStatus("เชื่อมต่อ Backend ไม่สำเร็จ", true);
    } finally {
        submitButton.disabled = false;
    }
}

submitButton.addEventListener("click", createPortal);
checkHealth();
</script>
</body>
</html>
"""


# -----------------------------
# Main Routes
# -----------------------------
@app.get("/")
def home():
    return render_template_string(HTML_PAGE)


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "like-ai",
        "version": "1.0.0",
        "time": utc_now(),
        "database": str(DB_PATH),
        "integrations": [
            "line",
            "facebook",
            "google_apps_script",
            "webhook"
        ]
    })


@app.get("/api/gems")
def gems():
    return jsonify({
        "status": "success",
        "data": [
            {
                "gem_id": "Creative-Post",
                "category": "Marketing",
                "description": "สร้างโพสต์และเนื้อหาการตลาด",
                "prompt_template": "สร้างเนื้อหาการตลาดตามกลุ่มเป้าหมาย"
            },
            {
                "gem_id": "Sales-Reply",
                "category": "CRM",
                "description": "ช่วยตอบข้อความลูกค้า",
                "prompt_template": "ตอบลูกค้าอย่างสุภาพและตรงประเด็น"
            },
            {
                "gem_id": "Brand-Voice",
                "category": "Branding",
                "description": "ควบคุมโทนเสียงของแบรนด์",
                "prompt_template": "ปรับเนื้อหาให้เหมาะกับเอกลักษณ์ของแบรนด์"
            }
        ]
    })


@app.get("/api/token/verify")
def verify_token():
    token = request.args.get("token", "")

    configured_tokens = os.getenv(
        "LIKEAI_TOKENS",
        "demo-token:demo@likeai.ai,admin-token:admin@likeai.ai"
    )

    tokens = {}

    for item in configured_tokens.split(","):
        if ":" in item:
            token_value, email = item.split(":", 1)
            tokens[token_value.strip()] = email.strip()

    email = tokens.get(token)

    if not email:
        return jsonify({
            "status": "invalid",
            "message": "Token ไม่ถูกต้อง"
        }), 401

    return jsonify({
        "status": "valid",
        "email": email
    })


@app.post("/api/portal")
def create_portal():
    payload = request.get_json(silent=True) or {}

    name = str(payload.get("name", "")).strip()
    source = str(payload.get("source", "ROOT")).strip() or "ROOT"
    group_name = str(payload.get("group", "")).strip()

    if not name:
        return json_error("กรุณากรอกชื่อผู้ใช้")

    if not group_name:
        return json_error("กรุณากรอกกลุ่ม")

    if len(name) > 120 or len(source) > 120 or len(group_name) > 120:
        return json_error("ข้อมูลยาวเกินกำหนด")

    code = "CR-" + secrets.token_hex(4).upper()
    created_at = utc_now()

    with db_connect() as db:
        db.execute(
            """
            INSERT INTO portals
            (code, name, source, group_name, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (code, name, source, group_name, created_at)
        )
        db.commit()

    return jsonify({
        "status": "success",
        "message": "สร้าง Portal สำเร็จ",
        "record": {
            "code": code,
            "name": name,
            "source": source,
            "group": group_name,
            "created_at": created_at
        }
    })


@app.get("/api/portals")
def list_portals():
    with db_connect() as db:
        rows = db.execute(
            """
            SELECT code, name, source, group_name, created_at
            FROM portals
            ORDER BY id DESC
            """
        ).fetchall()

    data = [
        {
            "code": row["code"],
            "name": row["name"],
            "source": row["source"],
            "group": row["group_name"],
            "created_at": row["created_at"]
        }
        for row in rows
    ]

    return jsonify({
        "status": "success",
        "data": data
    })


# -----------------------------
# LINE Integration
# -----------------------------
@app.post("/api/integrations/line/send")
def line_send():
    payload = request.get_json(silent=True) or {}

    recipient = payload.get("to") or os.getenv("LINE_DEFAULT_TO")
    message = str(payload.get("message", "สวัสดีจาก Like-AI"))[:5000]
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

    if not token or not recipient:
        return jsonify({
            "status": "demo",
            "provider": "line",
            "delivery": "simulated",
            "message": message,
            "reason": "ต้องกำหนด LINE_CHANNEL_ACCESS_TOKEN และ LINE_DEFAULT_TO"
        })

    response = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "to": recipient,
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        },
        timeout=20
    )

    if not response.ok:
        return json_error(
            f"LINE API Error: {response.text[:300]}",
            502
        )

    return jsonify({
        "status": "success",
        "provider": "line",
        "delivery": "sent"
    })


# -----------------------------
# Facebook Integration
# -----------------------------
@app.post("/api/integrations/facebook/post")
def facebook_post():
    payload = request.get_json(silent=True) or {}

    message = str(
        payload.get("message", "โพสต์จาก Like-AI")
    )[:63206]

    page_id = os.getenv("FACEBOOK_PAGE_ID")
    page_token = os.getenv("FACEBOOK_PAGE_TOKEN")

    if not page_id or not page_token:
        return jsonify({
            "status": "demo",
            "provider": "facebook",
            "delivery": "simulated",
            "message": message,
            "reason": "ต้องกำหนด FACEBOOK_PAGE_ID และ FACEBOOK_PAGE_TOKEN"
        })

    response = requests.post(
        f"https://graph.facebook.com/{page_id}/feed",
        params={
            "message": message,
            "access_token": page_token
        },
        timeout=20
    )

    if not response.ok:
        return json_error(
            f"Facebook API Error: {response.text[:300]}",
            502
        )

    return jsonify({
        "status": "success",
        "provider": "facebook",
        "delivery": "published",
        "data": response.json()
    })


# -----------------------------
# Google Apps Script Integration
# -----------------------------
@app.post("/api/integrations/google/sync")
def google_sync():
    google_url = os.getenv("GOOGLE_APPS_SCRIPT_URL")

    if not google_url:
        return jsonify({
            "status": "demo",
            "provider": "google_apps_script",
            "delivery": "simulated",
            "reason": "ยังไม่ได้กำหนด GOOGLE_APPS_SCRIPT_URL"
        })

    payload = request.get_json(silent=True) or {}

    response = requests.post(
        google_url,
        json=payload,
        timeout=20
    )

    if not response.ok:
        return json_error(
            f"Google Apps Script Error: {response.text[:300]}",
            502
        )

    try:
        result = response.json()
    except ValueError:
        result = {
            "raw": response.text
        }

    return jsonify({
        "status": "success",
        "provider": "google_apps_script",
        "data": result
    })


# -----------------------------
# Generic Webhook
# -----------------------------
@app.post("/api/integrations/webhook")
def webhook():
    payload = request.get_json(silent=True) or {}

    return jsonify({
        "status": "success",
        "provider": "webhook",
        "event": payload.get("event", "unknown"),
        "received": payload,
        "time": utc_now()
    })


# -----------------------------
# Start Application
# -----------------------------
init_db()

if __name__ == "__main__":
    print("Like-AI is running")
    print(f"Open: http://localhost:{PORT}")
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=os.getenv("FLASK_DEBUG", "0") == "1"
    )
