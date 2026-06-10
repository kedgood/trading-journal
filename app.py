import streamlit as st
import gspread
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- ตั้งค่าหน้าเว็บแอปพลิเคชัน ---
st.set_page_config(page_title="Professional Trade Journal", layout="wide")
st.title("📊 Professional Trading Journal & Dashboard")
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

# ฟังก์ชันดึงข้อมูล
def load_data():
    sheet = get_google_sheet()
    if sheet:
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            # แปลงคอลัมน์ Date ให้เป็นรูปแบบวันที่ของ Python
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            # ตรวจสอบว่ามีคอลัมน์ PnL ไหม
            if 'PnL' in df.columns:
                df['PnL'] = pd.to_numeric(df['PnL'], errors='coerce').fillna(0)
            return df
    return pd.DataFrame(columns=["Date", "Pair", "Buy/Sell", "Strategy", "Risk/Reward", "PnL", "Result", "Note", "Screenshot"])

# --- สร้างแท็บเมนูการใช้งาน 4 แท็บ ---
tab1, tab2, tab3, tab4 = st.tabs(["📥 บันทึกออเดอร์ใหม่", "📜 สมุดประวัติ", "🔍 ค้นหาข้อมูล", "📈 วิเคราะห์พอร์ต (Analytics)"])

# ================= TAB 1: บันทึกข้อมูล =================
with tab1:
    st.header("🗂️ บันทึกรายการเทรด")
    with st.form("trade_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            trade_date = st.date_input("📅 วันที่เข้าเทรด", datetime.now().date())
            pair_input = st.text_input("💱 คู่เงิน / สินทรัพย์", placeholder="เช่น XAUUSD").upper().strip()
            side_input = st.selectbox("↕️ ฝั่งออเดอร์", ["Buy", "Sell"])
        with col2:
            strategy_input = st.selectbox("🧠 ระบบเทรด", ["Price Action", "FVG", "SMC", "Indicator", "อื่นๆ"])
            rr_input = st.selectbox("⚖️ R:R Ratio", ["1:1", "1:2", "1:3", "อื่นๆ"])
            pnl_input = st.number_input("💵 กำไร/ขาดทุน ($)", value=0.0)
        with col3:
            screenshot_input = st.text_input("🖼️ Screenshot URL", placeholder="TradingView Link")
            note_input = st.text_area("📝 บันทึก", placeholder="เหตุผลในการเข้าเทรด")

        if st.form_submit_button("บันทึกข้อมูล (Save)"):
            sheet = get_google_sheet()
            if sheet and pair_input:
                result_status = "Win" if pnl_input > 0 else ("Loss" if pnl_input < 0 else "Breakeven")
                new_row = [str(trade_date), pair_input, side_input, strategy_input, rr_input, pnl_input, result_status, note_input, screenshot_input]
                sheet.append_row(new_row)
                st.success("บันทึกสำเร็จ!")
                st.rerun()

# ================= TAB 2: สมุดประวัติ =================
with tab2:
    st.header("📜 ประวัติการเทรดทั้งหมด")
    df = load_data()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูล")

# ================= TAB 3: ค้นหา =================
with tab3:
    st.header("🔍 ค้นหาข้อมูล")
    df = load_data()
    if not df.empty:
        search_pair = st.multiselect("เลือกคู่เงิน", options=df['Pair'].unique())
        if search_pair:
            st.dataframe(df[df['Pair'].isin(search_pair)], use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

# ================= TAB 4: Dashboard & Analytics (เพิ่มใหม่!) =================
with tab4:
    st.header("📈 วิเคราะห์แนวโน้มเงินทุน (Equity Curve)")
    df = load_data()
    
    if not df.empty:
        # ช่องกรอกเงินต้น
        initial_capital = st.number_input("💰 เงินต้นเริ่มต้น ($)", value=1000.0, step=100.0)
        
        # เรียงลำดับข้อมูลตามวันที่
        df_sorted = df.sort_values(by='Date')
        
        # คำนวณกำไรสะสม (Cumulative PnL)
        df_sorted['Cumulative_PnL'] = df_sorted['PnL'].cumsum()
        
        # คำนวณเงินในพอร์ตปัจจุบัน (Balance)
        df_sorted['Balance'] = initial_capital + df_sorted['Cumulative_PnL']
        
        # แสดงสถิติสรุปตัวเลข
        final_balance = df_sorted['Balance'].iloc[-1]
        total_pnl = df_sorted['Cumulative_PnL'].iloc[-1]
        win_rate = (len(df[df['Result'] == 'Win']) / len(df)) * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("ยอดเงินปัจจุบัน", f"${final_balance:,.2f}", delta=f"${total_pnl:,.2f}")
        c2.metric("กำไร/ขาดทุนรวม", f"${total_pnl:,.2f}")
        c3.metric("อัตราการชนะ (Win Rate)", f"{win_rate:.1f}%")
        
        st.markdown("### กราฟการเติบโตของพอร์ต (Equity Curve Over Time)")
        
        # สร้างกราฟ Plotly
        fig = go.Figure()
        
        # เพิ่มเส้นกราฟเงินในพอร์ต
        fig.add_trace(go.Scatter(
            x=df_sorted['Date'], 
            y=df_sorted['Balance'],
            mode='lines+markers',
            name='Account Balance',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8),
            hovertemplate="วันที่: %{x}<br>เงินในพอร์ต: $%{y:,.2f}<extra></extra>"
        ))
        
        # เพิ่มเส้นเงินต้น (Base line)
        fig.add_trace(go.Scatter(
            x=df_sorted['Date'], 
            y=[initial_capital] * len(df_sorted),
            mode='lines',
            name='Initial Capital',
            line=dict(color='white', width=1, dash='dash'),
            hoverinfo='skip'
        ))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="วันที่",
            yaxis_title="จำนวนเงิน ($)",
            margin=dict(l=20, r=20, t=20, b=20),
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("กรุณาบันทึกข้อมูลการเทรดในหน้าแรกก่อน เพื่อแสดงผลแดชบอร์ด")
