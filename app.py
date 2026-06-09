import streamlit as st
import gspread
import pandas as pd
from datetime import datetime

# --- ตั้งค่าหน้าเว็บแอปพลิเคชัน ---
st.set_page_config(page_title="Trade Journal Dashboard", layout="centered")
st.title("📊 My Trading Journal")
st.subheader("ระบบบันทึกประวัติการเทรด (เสถียรและปลอดภัย)")
st.markdown("---")

# ฟังก์ชันสำหรับบันทึกข้อมูล
def save_to_google_sheets(date_val, pair_val, side_val, pnl_val, screenshot_val):
    try:
        # ดึงค่าสิทธิ์การเข้าถึงจาก Streamlit Secrets 
        # (ระบบจะเปลี่ยน Service Account ของ Google ให้ล็อกอินอัตโนมัติ)
        creds_dict = st.secrets["gcp_service_account"]
        
        # ทำการล็อกอินเข้าสู่ Google Sheets
        client = gspread.service_account_from_dict(creds_dict)
        
        # เปิดไฟล์ Google Sheets ผ่านลิงก์ของคุณโดยตรง
        sheet_url = "https://docs.google.com/spreadsheets/d/1jXnDcJUUxQ2yLUUNlJe7jWg__lErKtIBkRXrQA7hb8U/edit?usp=sharing"
        sheet = client.open_by_url(sheet_url).sheet1
        
        # จัดเรียงข้อมูลให้ตรงกับตารางหัวข้อของคุณพอดี (Date, Pair, Buy/Sell, PnL, Screenshot)
        row_to_insert = [date_val, pair_val, side_val, pnl_val, screenshot_val]
        
        # เพิ่มข้อมูลแถวใหม่ล่างสุด
        sheet.append_row(row_to_insert)
        return True
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดหลังบ้าน: {e}")
        return False

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
            # เปลี่ยนข้อมูลวันที่ให้เป็นตัวหนังสือ (ปี-เดือน-วัน)
            formatted_date = trade_date.strftime("%Y-%m-%d")
            
            # บันทึกข้อมูล (หากไม่มีการกรอกช่องรูปภาพ ระบบจะส่งค่าเป็นช่องว่างให้โดยไม่ออก Error)
            img_link = screenshot_input.strip() if screenshot_input else ""
            
            success = save_to_google_sheets(
                formatted_date, 
                pair_input.upper().strip(), 
                side_input, 
                pnl_input, 
                img_link
            )
            
            if success:
                st.success(f"🎉 บันทึกออเดอร์คู่ {pair_input.upper()} ลง Google Sheets สำเร็จแล้ว!")
    else:
        st.warning("⚠️ กรุณาระบุชื่อคู่เงินหรือสินทรัพย์ (Pair) ก่อนกดบันทึก")
