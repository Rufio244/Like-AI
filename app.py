import streamlit as st
import requests

# ตั้งค่า URL ของ Google Apps Script Web App ที่ได้จากการ Deploy
API_URL = "YOUR_GOOGLE_APPS_SCRIPT_WEB_APP_URL"

st.title("🤖 likeAI - AGI Content & Creative Engine")
st.markdown("ระบบผู้ช่วยอัจฉริยะเฉพาะทาง ออกแบบและควบคุมโดยคุณธันวา")

# Sidebar: แยกส่วนผู้ใช้และส่วนแอดมิน
menu = st.sidebar.selectbox("เลือกโหมดการใช้งาน", ["ใช้งาน likeAI (User Mode)", "จัดการระบบ (Admin Mode)"])

if menu == "ใช้งาน likeAI (User Mode)":
    st.header("✨ ยินดีต้อนรับสู่ likeAI")
    
    # ช่องกรอก API Token สำหรับผู้ชำระเงิน
    user_token = st.text_input("กรุณากรอก API Token ของคุณเพื่อปลดล็อกระบบ:", type="password")
    
    if user_token:
        # ตรวจสอบ Token ผ่าน API
        try:
            res = requests.get(f"{API_URL}?action=verifyToken&token={user_token}").json()
            if res.get("status") == "valid":
                st.success(f"✅ ปดล็อกสำเร็จ! ยินดีต้อนรับผู้ใช้งาน: {res.get('email')}")
                
                # ดึงรายการสไตล์จาก Google Sheets
                styles_res = requests.get(f"{API_URL}?action=getStyles").json()
                if styles_res.get("status") == "success":
                    styles = styles_res.get("data")
                    
                    # ให้ผู้ใช้คลิกเลือกประเภทและสไตล์ตามต้องการ
                    categories = list(set([s["category"] for s in styles]))
                    selected_cat = st.selectbox("เลือกหมวดหมู่:", categories)
                    
                    filtered_styles = [s["styleName"] for s in styles if s["category"] == selected_cat]
                    selected_style = st.selectbox("เลือกสไตล์/ประเภทเฉพาะ:", filtered_styles)
                    
                    user_prompt = st.text_area("ระบุรายละเอียดสิ่งที่คุณต้องการสร้าง (เช่น โครงเรื่องย่อ ตัวละครหลัก):")
                    
                    if st.button("🚀 ประมวลผลด้วย likeAI"):
                        st.info(f"กำลังสร้างสรรค์ผลงานในสไตล์ [{selected_style}]...")
                        # จำลองการประมวลผล Prompt ตามข้อมูลที่ดึงมาจาก Google Sheets กลาง
                        selected_template = [s["promptTemplate"] for s in styles if s["styleName"] == selected_style][0]
                        st.write(f"**Template ที่ใช้:** {selected_template}")
                        st.success("สร้างผลงานเรียบร้อย! (คุณสามารถปรับแต่งเพิ่มได้ตลอดเวลาจาก Google Sheets กลาง)")
            else:
                st.error("❌ Token ไม่ถูกต้อง หรือยังไม่ได้รับการอนุมัติจากผู้ดูแลระบบ กรุณาติดต่อชำระเงินเพื่อรับ Token ตัวต่อตัว")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อระบบ: {e}")
    else:
        st.warning("⚠️ กรุณากรอก API Token เพื่อเริ่มต้นใช้งาน likeAI แบบชำระเงิน")

elif menu == "จัดการระบบ (Admin Mode)":
    st.header("🛠️ Admin Panel (สำหรับคุณธันวา)")
    st.info("ควบคุมและปรับปรุงแก้ไข likeAI จากส่วนกลาง อัปเดตสไตล์และจัดการ Token ได้ทันที")
    st.markdown("- **จัดการสไตล์:** แก้ไขที่ Google Sheet (`Settings`) ระบบจะอัปเดตให้ผู้ใช้ภายนอกทันทีโดยไม่ต้องแก้โค้ดใหม่")
    st.markdown("- **ออก Token:** เพิ่มอีเมลและออกรหัส Token ให้ลูกค้าใน Google Sheet (`Users_Tokens`) แล้วกดอนุมัติแบบตัวต่อตัว")
