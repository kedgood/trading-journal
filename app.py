import streamlit as st
import gspread
import pandas as pd
from datetime import datetime

# --- ตั้งค่าหน้าเว็บแอปพลิเคชัน ---
st.set_page_config(page_title="Trade Journal Dashboard", layout="wide")
st.title("📊 My Trading Journal Dashboard")
st.markdown("---")

# ลิงก์ Google Sheets ของคุณ
SHEET_URL = "https://docs.google.com/spreadsheets/d/1jXnDcJUUxQ2yLUUNlJe7jWg__lErKtIBkRXrQA7hb8U/edit?usp=sharing"

# ฟังก์ชันเชื่อมต่อ Google Sheets หลังบ้านด้วยระบบคีย์ลับ
def get_google_sheet():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        client = gspread.service_account_from_dict(creds_dict)
        sheet = client.open_by_url(SHEET_URL).sheet1
        return sheet
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อ Google Sheets ได้: {e}")
        return None

# ฟังก์ชันดึงข้อมูลจากชีตมาแสดงเป็นตาราง
def load_data():
    sheet = get_google_sheet()
    if sheet:
        data = sheet.get_all_records()
        if data:
            return pd.DataFrame(data)
    return pd.DataFrame(columns=["Date", "Pair", "Buy/Sell", "PnL", "Screenshot"])

# --- สร้างแท็บเมนูการใช้งาน 3 แท็บ ---
tab1, tab2, tab3 = st.tabs(["📥 กรอกข้อมูลการเทรด", "📜 สมุดบันทึกประวัติทั้งหมด", "🔍 ค้นหาและคัดกรอง"])

# ================= TAB 1: กรอกข้อมูล =================
with tab1:
    st.header("บันทึกออเดอร์ใหม่")
    col1, col2 = st.columns(2)
    with col1:
        trade_date = st.date_input("📅 วันที่", datetime.now().date())
        side_input = st.selectbox("↕️ ฝั่งออเดอร์", ["Buy", "Sell"])
    with col2:
        pair_input = st.text_input("💱 คู่เงิน / สินทรัพย์", placeholder="เช่น XAUUSD, EURUSD")
        pnl_input = st.number_input("💵 กำไร / ขาดทุน (PnL)", value=0.0, step=0.01, format="%.2f")
    
    screenshot_input = st.text_input("🖼️ ลิงก์รูปภาพบันทึกกราฟ (Screenshot URL)", placeholder="วางลิงก์รูปภาพ (เช่น ลิงก์รูปกล้องจาก TradingView)")
    
    if st.button("บันทึกข้อมูล (Save)", use_container_width=True):
        if pair_input:
            sheet = get_google_sheet()
            if sheet:
                with st.spinner("กำลังบันทึกข้อมูลลงตาราง..."):
                    formatted_date = trade_date.strftime("%Y-%m-%d")
                    new_row = [formatted_date, pair_input.upper().strip(), side_input, pnl_input, screenshot_input.strip()]
                    sheet.append_row(new_row)
                    st.success(f"🎉 บันทึกคู่ {pair_input.upper()} ลง Google Sheets เรียบร้อยแล้ว!")
                    st.rerun()
        else:
            st.warning("⚠️ กรุณากรอกชื่อคู่เงินก่อนกดปุ่มบันทึก")

# ================= TAB 2: แสดงข้อมูลทั้งหมดพร้อมรูปภาพ =================
with tab2:
    st.header("ประวัติการเทรดในสมุดบันทึก")
    df = load_data()
    
    if not df.empty:
        # คำนวณสถิติภาพรวม
        total_trades = len(df)
        total_pnl = df["PnL"].astype(float).sum()
        
        c1, c2 = st.columns(2)
        c1.metric("จำนวนออเดอร์สะสม", f"{total_trades} ไม้")
        c2.metric("กำไร/ขาดทุนสุทธิ", f"${total_pnl:,.2f}", delta=f"{total_pnl:,.2f}")
        
        st.markdown("### ตารางบันทึกข้อมูล")
        
        # คัดลอกตารางเพื่อนำมาปรับแต่งการแสดงผลรูปภาพ
        display_df = df.copy()
        
        # เพิ่มคอลัมน์ดึงรูปภาพมาแสดง (Preview) รองรับลิงก์ภาพทั่วไปและ TradingView
        if "Screenshot" in display_df.columns:
            display_df["ภาพกราฟ (Preview)"] = display_df["Screenshot"]
        
        # แสดงผลตารางแบบดึงรูปภาพขึ้นมาโชว์ทันที
        st.data_editor(
            display_df,
            column_config={
                "Screenshot": st.column_config.LinkColumn("ลิงก์รูปภาพต้นฉบับ"), # แสดงเป็นลิงก์ให้กดคลิกได้ง่ายๆ
                "ภาพกราฟ (Preview)": st.column_config.ImageColumn("ภาพกราฟ (Preview)", help="รูปภาพกราฟแผนภูมิที่บันทึกไว้") # สั่งให้แสดงเป็นรูปภาพในตารางเลย
            },
            use_container_width=True,
            disabled=True # ล็อกตารางไว้ดูอย่างเดียว ไม่ให้เผลอกดแก้ไขข้อมูล
        )
    else:
        st.info("ยังไม่มีประวัติการเทรดในระบบตารางของคุณ")

# ================= TAB 3: ค้นหาข้อมูล =================
with tab3:
    st.header("ค้นหาและคัดกรองข้อมูลประวัติ")
    df = load_data()
    
    if not df.empty:
        search_col1, search_col2 = st.columns(2)
        with search_col1:
            unique_pairs = ["ทั้งหมด"] + sorted(df["Pair"].unique().tolist())
            select_pair = st.selectbox("เลือกกรองตามชื่อคู่เงิน", unique_pairs)
        with search_col2:
            select_side = st.selectbox("เลือกกรองตามฝั่ง Buy หรือ Sell", ["ทั้งหมด", "Buy", "Sell"])
            
        filtered_df = df.copy()
        if select_pair != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df["Pair"] == select_pair]
        if select_side != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df["Buy/Sell"] == select_side]
            
        st.markdown(f"🔍 ค้นพบข้อมูลทั้งหมด **{len(filtered_df)}** รายการ")
        
        # ค้นหาแล้วโชว์รูปภาพในแท็บค้นหาด้วยเช่นกัน
        if "Screenshot" in filtered_df.columns:
            filtered_df["ภาพกราฟ (Preview)"] = filtered_df["Screenshot"]
            
        st.data_editor(
            filtered_df,
            column_config={
                "Screenshot": st.column_config.LinkColumn("ลิงก์รูปภาพต้นฉบับ"),
                "ภาพกราฟ (Preview)": st.column_config.ImageColumn("ภาพกราฟ (Preview)")
            },
            use_container_width=True,
            disabled=True
        )
    else:
        st.info("ยังไม่มีข้อมูลในสมุดบันทึกสำหรับการค้นหา")
