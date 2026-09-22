import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("LIKEAI_API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Like-AI Ecosystem", page_icon="🤖", layout="wide")

st.title("🤖 Like-AI : AGI Multi-Gem & Platform Ecosystem")
st.markdown("ระบบที่สามารถเชื่อมต่อกับ Google Apps Script, LINE, Facebook, Webhook และระบบภายนอกอื่น ๆ ได้")

with st.sidebar:
    st.subheader("⚙️ Connectivity")
    api_url = st.text_input("API Base URL", value=API_BASE_URL, help="เชื่อมต่อ backend ที่รันอยู่ที่ localhost:8000")
    st.caption("ตัวอย่าง: http://localhost:8000")

menu = st.sidebar.selectbox("เลือกโหมดการใช้งาน", ["ใช้งาน Like-AI (User Portal)", "จัดการระบบและออกสิทธิ์ (Admin Portal)"])


def safe_get_json(url, timeout=10):
    try:
        r = requests.get(url, timeout=timeout)
        return r.json(), r.status_code
    except Exception as exc: 
        return {"status": "error", "message": str(exc)}, 500


if menu == "ใช้งาน Like-AI (User Portal)":
    st.header("✨ พื้นที่ใช้งาน Like-AI Workspace")
    col1, col2 = st.columns([1, 1])
    with col1:
        user_token = st.text_input("🔑 กรุณากรอก API Token ของคุณ", type="password")
    with col2:
        selected_platform = st.selectbox("🌐 ช่องทางใช้งาน", ["Web Portal", "Facebook Page", "Line OA", "TikTok Shop / Live", "Custom API"])

    health, status = safe_get_json(f"{api_url}/api/health")
    if status != 200:
        st.warning("⚠️ Backend ยังไม่เปิดหรือ URL ผิด กรุณาเปิด server.py ก่อนใช้งาน")

    if user_token:
        token_check, token_status = safe_get_json(f"{api_url}/api/token/verify?token={user_token}")
        if token_status == 200 and token_check.get("status") == "valid":
            st.success(f"✅ ยินดีต้อนรับ {token_check.get('email', 'ผู้ใช้')} | สิทธิ์ใช้งานพร้อมแล้ว")

            gems, gem_status = safe_get_json(f"{api_url}/api/gems")
            if gem_status == 200 and gems.get("status") == "success":
                gem_list = gems.get("data", [])
                if gem_list:
                    gem_names = [g["gem_id"] for g in gem_list]
                    selected_gem = st.selectbox("🚀 เลือก Gem ที่ต้องการใช้งาน", gem_names)
                    current_gem = next((g for g in gem_list if g["gem_id"] == selected_gem), None)

                    if current_gem:
                        st.info(f"📌 {current_gem.get('description', 'ไม่มีคำอธิบาย')} | หมวดหมู่: {current_gem.get('category', 'general')}")
                        user_prompt = st.text_area("✍️ ระบุโจทย์หรือรายละเอียดที่ต้องการ", "สร้างสรรค์โพสต์สำหรับผู้ประกอบการไทยที่มีประสบการณ์สูง")

                        if st.button("🚀 ประมวลผลด้วย Like-AI Engine"):
                            if user_prompt.strip():
                                st.subheader("📌 ผลลัพธ์จาก Like-AI")
                                result = f"### โหมดการทำงาน: {selected_gem}\n\n"
                                result += f"**โจทย์ของคุณ:** {user_prompt}\n\n"
                                result += f"**แม่แบบที่ใช้:** {current_gem.get('prompt_template', 'General Creative Workflow')}\n\n"
                                result += "**เนื้อหาที่สร้างเสร็จสมบูรณ์:**\n"
                                result += "- วิเคราะห์ข้อมูลและประเด็นที่ต้องการ\n"
                                result += "- สร้างแนวคิดให้ตรงกับสไตล์และวัตถุประสงค์\n"
                                result += "- จัดรูปแบบให้พร้อมใช้งานกับช่องทางที่เลือก\n"
                                result += f"- พร้อมส่งต่อช่องทาง: {selected_platform}\n"
                                st.markdown(result)
                                st.success("✨ สร้างสรรค์ผลงานสำเร็จเรียบร้อย!")
                            else:
                                st.warning("⚠️ กรุณากรอกรายละเอียดก่อนกดประมวลผล")
                else:
                    st.warning("⚠️ ยังไม่มี Gem ในระบบ กรุณาเพิ่มข้อมูลใน Google Sheet หรือ Mock API")
            else:
                st.error("❌ ไม่สามารถเรียกข้อมูล Gem จาก backend ได้")
        else:
            st.error("❌ Token ไม่ถูกต้อง หรือไม่มีสิทธิ์ใช้งาน")
    else:
        st.warning("⚠️ กรุณากรอก API Token เพื่อเริ่มใช้งาน")

elif menu == "จัดการระบบและออกสิทธิ์ (Admin Portal)":
    st.header("🛠️ Admin Dashboard")
    st.markdown("ตัวเชื่อมต่อภายนอกที่พร้อมใช้งาน:")
    st.markdown("1. Google Apps Script / Google Sheets")
    st.markdown("2. LINE OA")
    st.markdown("3. Facebook Page / Webhook")
    st.markdown("4. Custom API / External Services")

    health, status = safe_get_json(f"{api_url}/api/health")
    st.subheader("🔎 Health Check")
    if status == 200:
        st.json(health)
    else:
        st.warning("Backend ยังไม่พร้อมใช้งาน")

    st.subheader("🧩 Sample Integration Hooks")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if st.button("Test LINE Send"):
            payload = {"message": "สวัสดี จาก Like-AI - การทดสอบส่งข้อความไป LINE สำเร็จ"}
            resp, code = safe_get_json(f"{api_url}/api/integrations/line/send?message={payload['message']}")
            st.json(resp)

    with col_b:
        if st.button("Test Facebook Post"):
            resp, code = safe_get_json(f"{api_url}/api/integrations/facebook/post?message=Demo Post From Like-AI")
            st.json(resp)

    with col_c:
        if st.button("Test Webhook"):
            resp, code = safe_get_json(f"{api_url}/api/integrations/webhook/accept?event=portal_created")
            st.json(resp)

    st.subheader("📋 ระบบยืนยันสิทธิ์")
    st.code("LIKEAI_API_BASE_URL=http://localhost:8000\nLINE_CHANNEL_ACCESS_TOKEN=your_token_here\nFACEBOOK_PAGE_TOKEN=your_page_token_here")

    st.caption("แนะนำให้เก็บ Secret ทุกตัวไว้ใน Environment Variable ไม่ควรเขียนลงใน Source Code")

st.caption("Build status: ready | backend + frontend + connectors demo mode")
