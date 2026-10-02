# Like-AI

Like-AI เป็นระบบเวิร์กโฟลว์อัจฉริยะที่สามารถทำหน้าที่เป็น
- User Portal
- Admin Dashboard
- API Integration Gateway
- Mock/Production-ready connector สำหรับ Google Apps Script, LINE, Facebook, Webhook และบริการภายนอกอื่น ๆ

## วิธีใช้งาน

1. ติดตั้ง dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. เปิด backend

```bash
python server.py
```

3. เปิด Streamlit

```bash
streamlit run app.py
```

4. เปิดหน้าเว็บ static portal

```bash
http://localhost:8000/
```

## สิ่งที่ระบบมี

- `server.py` สำหรับ API และ static website
- `app.py` สำหรับ Streamlit dashboard
- `public/index.html` สำหรับหน้าเว็บ portal
- `Meta_pa.py` สำหรับ launcher / setup helper
- `requirements.txt` สำหรับ dependency

## ตัวอย่าง Environment Variables

```bash
export LIKEAI_API_BASE_URL=http://localhost:8000
export LINE_CHANNEL_ACCESS_TOKEN=your_line_token
export FACEBOOK_PAGE_TOKEN=your_facebook_token
export GOOGLE_APPS_SCRIPT_URL=your_google_script_url
```

## หมายเหตุ

- โหมดปัจจุบันเป็น demo-ready integration layer
- หากต้องใช้งานจริงให้กำหนด URL และ Secret ของระบบภายนอกให้ถูกต้อง
- ควรเก็บ Secret ใน environment variable ไม่ควรไว้ใน repo
