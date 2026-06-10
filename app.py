import streamlit as st
import gspread
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- ตั้งค่าหน้าเว็บแอปพลิเคชัน ---
st.set_page_config(page_title="Professional Trade Journal", layout="wide")
st.title("📈 Professional Trading Journal & Analytics")
st.markdown("ระบบบันทึกและวิเคราะห์สถิติการเทรดระดับมืออาชีพ")
st.markdown("---")

# ลิงก์ Google Sheets ของคุณ
SHEET_URL = "https://docs.google.com/spreadsheets/d/1jXnDcJUUxQ2yLUUNlJe7jWg__lErKtIBkRXrQA7hb8U/edit?usp=sharing"

# ฟังก์ชันเชื่อมต่อ Google Sheets
def get_google_sheet():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        client = gspread.service_account_from_dict(creds_dict)
        sheet = client.open_by_url(SHEET_URL).sheet1
        return sheet
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อ Google Sheets ได้: {e}")
        return None

# ฟังก์ชันดึงข้อมูลจากชีต
def load_data():
    sheet = get_google_sheet()
    if sheet:
        data = sheet.get_all_records()
        if data:
            return pd.DataFrame(data)
    return pd.DataFrame(columns=["Date", "Pair", "TimeFrame", "Buy/Sell", "LotSize", "Points", "Strategy", "Risk/Reward", "PnL", "Result", "Entry_Screenshot", "Exit_Screenshot", "Entry_Type", "Note"])

# --- สร้างแท็บเมนูการใช้งาน 4 แท็บ ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📥 บันทึกออเดอร์ใหม่", 
    "📜 สมุดประวัติและสถิติรวม", 
    "🔍 ค้นหาและคัดกรอง", 
    "📈 กราฟแนวโน้มเงินทุน (Equity Curve)"
])

# ================= TAB 1: กรอกข้อมูล =================
with tab1:
    st.header("🗂️ บันทึกรายละเอียดการเข้าเทรด (Trade Entry)")
    
    with st.form("trade_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            trade_date = st.date_input("📅 วันที่เข้าเทรด", datetime.now().date())
            
            pair_selection = st.selectbox("💱 เลือกคู่เงิน / สินทรัพย์", ["XAUUSD", "USDJPY", "GBPUSD", "อื่นๆ (กรอกเองด้านล่าง)"])
            if pair_selection == "อื่นๆ (กรอกเองด้านล่าง)":
                pair_input = st.text_input("✍️ พิมพ์ชื่อคู่เงินเอง", placeholder="เช่น EURUSD").upper().strip()
            else:
                pair_input = pair_selection
                
            tf_input = st.selectbox("⏱️ หน้าเทรดใช้ Time Frame อะไร?", ["M1", "M5", "M15", "H1", "H4", "D1", "อื่นๆ"])
            side_input = st.selectbox("↕️ ฝั่งออเดอร์", ["Buy", "Sell"])
            
        with col2:
            lotsize_input = st.number_input("📊 ขนาดสัญญา (Lot Size)", value=0.01, step=0.01, format="%.2f")
            points_input = st.number_input("🎯 จำนวนจุดที่ ชนะ/แพ้ (Points)", value=0, step=10)
            pnl_input = st.number_input("💵 กำไร / ขาดทุนสุทธิ (PnL $)", value=0.0, step=1.0, format="%.2f")
            
            entry_type_input = st.selectbox("📌 ประเภทการเข้าเทรด (Entry Type)", [
                "ตามเทรนด์ขาขึ้น (Up-Trend)", 
                "ตามเทรนด์ขาลง (Down-Trend)", 
                "เล่นในกรอบ/กลับตัว (Sideway/Reversal)"
            ])
            
        with col3:
            strategy_input = st.selectbox("🧠 แผนระบบเทรด (Setup/Strategy)", 
                                          ["Price Action", "Fair Value Gap (FVG)", "Volume Profile (POC/HVN/LVN)", "Break of Structure (BOS)", "Indicator Sign", "อื่นๆ"])
            rr_input = st.selectbox("⚖️ Risk / Reward Ratio", ["1:1", "1:1.5", "1:2", "1:3", "มากกว่า 1:3", "ไม่ได้ตั้ง (No RR)"])
            
            entry_screenshot = st.text_input("📸 ลิงก์รูปภาพตอน 'เข้าออเดอร์' (Entry Link)", placeholder="วางลิงก์รูปกล้อง TradingView")
            exit_screenshot
