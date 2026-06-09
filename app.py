import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- ตั้งค่าหน้าเว็บแอปพลิเคชัน ---
st.set_page_config(page_title="Trade Journal Dashboard", layout="centered")
st.title("📊 My Trading Journal")
st.subheader("ระบบบันทึกประวัติการเทรดแบบง่าย (Direct Link)")
st.markdown("---")

# 1. ระบุลิงก์ Google Sheets ของคุณโดยตรง
sheet_url = "https://docs.google.com/spreadsheets/d/1jXnDcJUUxQ2yLUUNlJe7jWg__lErKtIBkRXrQA7hb8U/edit?usp=sharing"

# 2. เชื่อมต่อระบบกับ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# ดึงข้อมูลแถวเดิมขึ้นมาเช็กก่อนบันทึก
try:
    existing_data = conn.read(spreadsheet=sheet_url, usecols=[0, 1, 2, 3, 4])
except Exception:
    # หากเป็นครั้งแรกและไม่มีข้อมูล ให้สร้างตารางเปล่าที่มีหัวคอลัมน์เหมือนในชีตของคุณ
    existing_data = pd.DataFrame(columns=["Date", "Pair", "Buy/Sell", "PnL", "Screenshot"])

# --- ฟอร์มกรอกข้อมูลหน้าเว็บ ---
col1, col2 = st.columns(2)
with col1:
    trade_date = st.date_input("📅 Date", datetime.now().date())
    side_input = st.selectbox("↕️ Buy/Sell", ["Buy", "Sell"])
with col2:
    pair_input = st.text_input("💱 Pair", placeholder="เช่น XAUUSD, EURUSD")
    pnl_input = st.number_input("💵 PnL (Profit/Loss)", value=0.0, step=0.01, format="%.2f")

screenshot_input = st.text_input("🖼️ Screenshot URL", placeholder="วางลิงก์รูปภาพกราฟเทรด (ถ้ามี)")

st.markdown("<br>", unsafe_allow_html=True)

# ปุ่มกดสำหรับบันทึกข้อมูล
if st.button("บันทึกข้อมูล (Save Trade)", use_container_width=True):
    if pair_input:
        with st.spinner("กำลังบันทึกข้อมูลลงตารางของคุณ..."):
            # 1. จัดเตรียมข้อมูลใหม่ให้ชื่อหัวคอลัมน์ตรงกับในตาราง Google Sheets ทุกตัวอักษร
            new_row = pd.DataFrame([{
                "Date": trade_date.strftime("%Y-%m-%d"),
                "Pair": pair_input.upper().strip(),
                "Buy/Sell": side_input,
                "PnL": pnl_input,
                "Screenshot": screenshot_input.strip()
            }])
            
            # 2. นำข้อมูลใหม่ไปต่อท้ายข้อมูลที่มีอยู่เดิม
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            
            # 3. สั่งอัปเดตตารางกลับไปที่ Google Sheets ทันที
            conn.update(spreadsheet=sheet_url, data=updated_df)
            st.success(f"🎉 บันทึกคู่ {pair_input.upper()} ลง Google Sheets เรียบร้อยแล้ว!")
    else:
        st.warning("⚠️ กรุณาระบุชื่อคู่เงินหรือสินทรัพย์ (Pair) ก่อนกดบันทึก")
