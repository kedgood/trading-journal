import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- ตั้งค่าหน้าเว็บแอปพลิเคชัน ---
st.set_page_config(page_title="Trade Journal Dashboard", layout="centered")
st.title("📊 My Trading Journal")
st.subheader("ระบบบันทึกประวัติการเทรดอัตโนมัติ")
st.markdown("---")

# ดึงลิงก์จากระบบ Secrets มาใช้งาน
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]

# เปิดการเชื่อมต่อด้วยปลั๊กอินของ Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

# อ่านข้อมูลเก่าขึ้นมาเตรียมพร้อมอัปเดต
try:
    existing_data = conn.read(spreadsheet=sheet_url)
except Exception:
    existing_data = pd.DataFrame(columns=["Date", "Pair", "Buy/Sell", "PnL", "Screenshot"])

# --- ฟอร์มกรอกข้อมูลหน้าเว็บ UI ---
col1, col2 = st.columns(2)
with col1:
    trade_date = st.date_input("📅 Date", datetime.now().date())
    side_input = st.selectbox("↕️ Buy/Sell", ["Buy", "Sell"])
with col2:
    pair_input = st.text_input("💱 Pair", placeholder="เช่น XAUUSD, EURUSD")
    pnl_input = st.number_input("💵 PnL (Profit/Loss)", value=0.0, step=0.01, format="%.2f")

screenshot_input = st.text_input("🖼️ Screenshot URL", placeholder="วางลิงก์รูปภาพกราฟเทรด (ไม่มีให้เว้นว่างได้)")

st.markdown("<br>", unsafe_allow_html=True)

# ปุ่มกดบันทึก
if st.button("บันทึกข้อมูล (Save Trade)", use_container_width=True):
    if pair_input:
        with st.spinner("กำลังบันทึกข้อมูลลงตาราง..."):
            
            # 1. จัดเตรียมข้อมูลใหม่
            new_row = pd.DataFrame([{
                "Date": trade_date.strftime("%Y-%m-%d"),
                "Pair": pair_input.upper().strip(),
                "Buy/Sell": side_input,
                "PnL": pnl_input,
                "Screenshot": screenshot_input.strip() if screenshot_input else ""
            }])
            
            # 2. รวมข้อมูลใหม่ต่อท้ายข้อมูลเดิม
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            
            try:
                # 3. อัปเดตข้อมูลกลับเข้า Google Sheets
                conn.update(spreadsheet=sheet_url, data=updated_df)
                st.success(f"🎉 บันทึกออเดอร์คู่ {pair_input.upper()} เรียบร้อยแล้ว!")
                st.balloons() # แสดงเอฟเฟกต์ลูกโป่งฉลองความสำเร็จ
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการเขียนข้อมูล: {e}")
                st.info("💡 คำแนะนำ: ตรวจสอบว่าใน Google Sheets ได้กดปุ่มแชร์ขวาบน และตั้งค่าให้ 'ทุกคนที่มีลิงก์' เป็น 'ผู้แก้ไข (Editor)' แล้วหรือยัง")
    else:
        st.warning("⚠️ กรุณาระบุชื่อคู่เงินหรือสินทรัพย์ (Pair) ก่อนกดบันทึก")
