import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- ตั้งค่าการเชื่อมต่อ Google Sheets API ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # ดึงค่า JSON Web Token Credentials จากระบบ Secrets ของ Streamlit Cloud (แนะนำสำหรับความปลอดภัย)
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
except Exception:
    # บรรทัดนี้เปิดไว้รองรับกรณีรันในเครื่องคอมพิวเตอร์ตัวเองที่มีไฟล์ JSON เก็บไว้
    # creds = ServiceAccountCredentials.from_json_keyfile_name('your-secret-file.json', scope)
    pass

def append_trade_data(date_val, pair_val, side_val, pnl_val, screenshot_val):
    try:
        # เปิดการเชื่อมต่อ
        client = gspread.authorize(creds)
        # เปิดไปยังสมุดงานที่ชื่อ "Trade Journal" และเลือกแผ่นงานแรก
        sheet = client.open("Trade Journal").sheet1
        
        # จัดรูปแบบชุดข้อมูลเป็นแถวให้ตรงกับคอลัมน์ A, B, C, D, E ในตารางของคุณพอดี
        row_to_insert = [date_val, pair_val, side_val, pnl_val, screenshot_val]
        
        # ทำการเพิ่มข้อมูลลงแถวใหม่ล่างสุดต่อจากข้อมูลเดิม
        sheet.append_row(row_to_insert)
        return True
    except Exception as e:
        st.error(f"ระบบไม่สามารถเขียนข้อมูลลง Google Sheets ได้: {e}")
        return False

# --- การออกแบบหน้าตาเว็บแอปพลิเคชัน (Web UI Layout) ---
st.set_page_config(page_title="Trade Journal Dashboard", layout="centered")

st.title("📊 My Trading Journal")
st.subheader("ระบบบันทึกประวัติการเทรดอัตโนมัติ")
st.markdown("---")

# แบ่งช่องกรอกข้อมูลออกเป็นฝั่งซ้ายและฝั่งขวาเพื่อความสวยงาม
col1, col2 = st.columns(2)

with col1:
    # ช่องระบุวันที่ (เลือกได้จากปฏิทิน เริ่มต้นที่วันปัจจุบัน)
    trade_date = st.date_input("📅 Date", datetime.now().date())
    
    # ช่องเลือกประเภทการออกออเดอร์
    side_input = st.selectbox("↕️ Buy/Sell", ["Buy", "Sell"])

with col2:
    # ช่องกรอกชื่อคู่เงินหรือสินทรัพย์
    pair_input = st.text_input("💱 Pair", placeholder="เช่น XAUUSD, EURUSD, BTC")
    
    # ช่องใส่จำนวนเงินกำไร/ขาดทุน
    pnl_input = st.number_input("💵 PnL (Profit/Loss)", value=0.0, step=0.01, format="%.2f")

# ช่องใส่ลิงก์รูปภาพแผนภาพหรือกราฟสำหรับเก็บไว้ดูย้อนหลัง
screenshot_input = st.text_input("🖼️ Screenshot URL", placeholder="วางลิงก์รูปภาพบันทึกหน้าจอ (ถ้ามี)")

st.markdown("<br>", unsafe_allow_html=True)

# ปุ่มกดสำหรับประมวลผลและบันทึก
if st.button("บันทึกข้อมูล (Save Trade)", use_container_width=True):
    if pair_input:
        with st.spinner("กำลังทำการส่งข้อมูลไปยัง Google Sheets..."):
            # แปลงรูปแบบวันที่เป็นปี-เดือน-วัน (ข้อความ) เพื่อนำไปหยอดลงช่องเซลล์ตาราง
            formatted_date = trade_date.strftime("%Y-%m-%d")
            
            # บันทึกข้อมูล
            is_success = append_trade_data(
                formatted_date, 
                pair_input.upper().strip(), # ปรับให้เป็นอักษรพิมพ์ใหญ่เพื่อความเป็นระเบียบ
                side_input, 
                pnl_input, 
                screenshot_input.strip()
            )
            
            if is_success:
                st.success(f"🎉 บันทึกข้อมูลการเทรดคู่ {pair_input.upper()} ลง Google Sheets เรียบร้อยแล้ว!")
    else:
        st.warning("⚠️ กรุณาระบุชื่อคู่เงินหรือสินทรัพย์ (Pair) ในช่องว่างก่อนกดบันทึก")
