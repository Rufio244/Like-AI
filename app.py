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
import streamlit as st
import requests

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(
    page_title="Like-AI Ecosystem : Multi-Gem & Token Gateway",
    page_icon="🤖",
    layout="wide"
)

# Sidebar สำหรับตั้งค่าระบบเชื่อมต่อ Google Apps Script API
st.sidebar.title("⚙️ Like-AI Control Center")
api_url_input = st.sidebar.text_input(
    "Google Apps Script Web App URL:",
    value="https://script.google.com/macros/s/YOUR_DEPLOYED_SCRIPT_ID/exec",
    help="ใส่ Web App URL ที่ได้จากการ Deploy Google Apps Script ของคุณ"
)

st.title("🤖 Like-AI : AGI Multi-Gem & Platform Ecosystem")
st.markdown("พัฒนาและควบคุมระบบโดย **คุณธันวา (Vider Ecosystem)** | ระบบจัดการ Gem แยกตามประเภท เชื่อมต่อทุกแพลตฟอร์ม และระบบออก Token ปลดล็อกรายตัว")

# แบ่งโหมดการทำงาน
menu = st.sidebar.selectbox("เลือกโหมดการใช้งาน", ["ใช้งาน Like-AI (User Portal)", "จัดการระบบและออกสิทธิ์ (Admin Portal)"])

if menu == "ใช้งาน Like-AI (User Portal)":
    st.header("✨ พื้นที่ใช้งาน Like-AI Workspace (Multi-Gem)")
    
    col1, col2 = st.columns(2)
    with col1:
        user_token = st.text_input("🔑 กรุณากรอก API Token ของคุณ (รับรหัสปลดล็อกตัวต่อตัวจากแอดมิน):", type="password")
    with col2:
        selected_platform = st.selectbox("🌐 ช่องทางใช้งาน / แพลตฟอร์ม:", ["Web Portal", "Facebook Page", "Line OA", "TikTok Shop / Live", "Custom API"])

    if user_token and "YOUR_DEPLOYED_SCRIPT_ID" not in api_url_input:
        try:
            with st.spinner("กำลังตรวจสอบสิทธิ์ Token กับระบบกลาง..."):
                gems_res = requests.get(f"{api_url_input}?action=getGems", timeout=10).json()
                
            if gems_res.get("status") == "success":
                gems_list = gems_res.get("data", [])
                
                if gems_list:
                    gem_names = [g["gem_id"] for g in gems_list]
                    selected_gem_id = st.selectbox("🚀 เลือก Gem อัจฉริยะที่คุณต้องการเรียกใช้งาน:", gem_names)
                    
                    current_gem = next((g for g in gems_list if g["gem_id"] == selected_gem_id), None)
                    
                    if current_gem:
                        st.info(f"📌 **รายละเอียด Gem:** {current_gem.get('description', 'ไม่มีคำอธิบาย')} | **หมวดหมู่:** {current_gem.get('category', 'General')}")
                        
                        auth_check = requests.get(f"{api_url_input}?action=verifyToken&token={user_token}&gem_id={selected_gem_id}", timeout=10).json()
                        
                        if auth_check.get("status") == "valid":
                            st.success(f"✅ ปลดล็อกสำเร็จ! ผู้ใช้งาน: {auth_check.get('email')} | ได้รับสิทธิ์ใช้งาน Gem: **{selected_gem_id}** ผ่านระบบ [{selected_platform}]")
                            
                            user_prompt = st.text_area("✍️ ระบุโจทย์หรือรายละเอียดที่คุณต้องการให้ Like-AI ประมวลผล:", placeholder="พิมพ์ข้อมูลรายละเอียดที่คุณต้องการที่นี่...")
                            
                            if st.button("🚀 ประมวลผลด้วย Like-AI Engine"):
                                if user_prompt.strip():
                                    st.info(f"กำลังประมวลผลข้อมูลผ่าน Gem: [{selected_gem_id}]...")
                                    base_template = current_gem.get('prompt_template', '')
                                    
                                    st.subheader("📌 ผลลัพธ์จาก Like-AI:")
                                    simulated_result = f"### โหมดการทำงาน: {selected_gem_id} (ผ่าน {selected_platform})\n\n" \
                                                       f"**โจทย์ของคุณ:** {user_prompt}\n\n" \
                                                       f"**แม่แบบที่ใช้ประมวลผล (Template):** {base_template}\n\n" \
                                                       f"**เนื้อหาที่สร้างเสร็จสมบูรณ์:**\n" \
                                                       f"- ระบบได้ทำการวิเคราะห์และสังเคราะห์ข้อมูลตามโครงสร้างของ Gem ตัวนี้เรียบร้อยแล้ว\n" \
                                                       f"- คุณสามารถแก้ไขหรือเพิ่มเงื่อนไขได้ตลอดเวลาจาก Google Sheets ส่วนกลางของคุณ!"
                                    st.markdown(simulated_result)
                                    st.success("✨ สร้างสรรค์ผลงานสำเร็จเรียบร้อย!")
                                else:
                                    st.warning("⚠️ กรุณากรอกรายละเอียดโจทย์ก่อนกดประมวลผล")
                        else:
                            st.error(f"❌ Token นี้ยังไม่ได้รับสิทธิ์เข้าใช้งาน Gem [{selected_gem_id}] กรุณาติดต่อชำระเงินเพื่อขอรหัสปลดล็อกตัวต่อตัว")
                else:
                    st.warning("⚠️ ยังไม่มี Gem ในระบบ กรุณาเพิ่มข้อมูลใน Google Sheet (Sheet: Gem_Registry)")
            else:
                st.error("❌ ไม่สามารถดึงข้อมูลรายการ Gem จากระบบกลางได้")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อระบบ API: {e}")
    else:
        st.warning("⚠️ กรุณากรอก API Token และระบุ Google Apps Script Web App URL ให้ถูกต้องที่ Sidebar ด้านซ้าย")

elif menu == "จัดการระบบและออกสิทธิ์ (Admin Portal)":
    st.header("🛠️ Admin Dashboard (สำหรับคุณธันวา)")
    st.markdown("ควบคุมระบบหลังบ้านทั้งหมดของ **Like-AI Ecosystem**:")
    st.markdown("1. **จัดการ Gem (`Google Sheet: Gem_Registry`):** เพิ่มแถวเพื่อสร้าง Gem ใหม่และกำหนด Prompt Template")
    st.markdown("2. **ออกรหัส Token (`Google Sheet: Users_Tokens`):** กำหนดสิทธิ์อีเมล, Token และสิทธิ์เข้าถึง Gem แล้วเปลี่ยนสถานะเป็น `Approved`")
    st.markdown("3. **เชื่อมต่อ Omni-Platform:** รองรับ Webhook จาก Facebook Page, Line OA และ Web พลังงานสูง")
