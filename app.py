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
    return pd.DataFrame(columns=["Date", "Pair", "TimeFrame", "Buy/Sell", "LotSize", "Points", "Strategy", "Risk/Reward", "PnL", "Result", "Entry_Screenshot", "Exit_Screenshot", "Note"])

# --- สร้างแท็บเมนูการใช้งาน 4 แท็บ ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📥 บันทึกออเดอร์ใหม่", 
    "📜 สมุดประวัติและสถิติรวม", 
    "🔍 ค้นหาและคัดกรอง", 
    "📈 กราฟแนวโน้มเงินทุน (Equity Curve)"
])

# ================= TAB 1: กรอกข้อมูล (เวอร์ชันแยก Time Frame และ รูป Entry/Exit) =================
with tab1:
    st.header("🗂️ บันทึกรายละเอียดการเข้าเทรด (Trade Entry)")
    
    with st.form("trade_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            trade_date = st.date_input("📅 วันที่เข้าเทรด", datetime.now().date())
            
            # เลือกคู่เงิน
            pair_selection = st.selectbox("💱 เลือกคู่เงิน / สินทรัพย์", ["XAUUSD", "USDJPY", "GBPUSD", "อื่นๆ (กรอกเองด้านล่าง)"])
            if pair_selection == "อื่นๆ (กรอกเองด้านล่าง)":
                pair_input = st.text_input("✍️ พิมพ์ชื่อคู่เงินเอง", placeholder="เช่น EURUSD").upper().strip()
            else:
                pair_input = pair_selection
                
            # เพิ่มตัวเลือก Time Frame ยอดนิยม
            tf_input = st.selectbox("⏱️ หน้าเทรดใช้ Time Frame อะไร?", ["M1", "M5", "M15", "H1", "H4", "D1", "อื่นๆ"])
            side_input = st.selectbox("↕️ ฝั่งออเดอร์", ["Buy", "Sell"])
            
        with col2:
            lotsize_input = st.number_input("📊 ขนาดสัญญา (Lot Size)", value=0.01, step=0.01, format="%.2f")
            points_input = st.number_input("🎯 จำนวนจุดที่ ชนะ/แพ้ (Points)", value=0, step=10)
            pnl_input = st.number_input("💵 กำไร / ขาดทุนสุทธิ (PnL $)", value=0.0, step=1.0, format="%.2f")
            
        with col3:
            strategy_input = st.selectbox("🧠 แผนระบบเทรด (Setup/Strategy)", 
                                          ["Price Action", "Fair Value Gap (FVG)", "Volume Profile (POC/HVN/LVN)", "Break of Structure (BOS)", "Indicator Sign", "อื่นๆ"])
            rr_input = st.selectbox("⚖️ Risk / Reward Ratio", ["1:1", "1:1.5", "1:2", "1:3", "มากกว่า 1:3", "ไม่ได้ตั้ง (No RR)"])
            
            # แยกช่องวางลิงก์รูปเป็น 2 ช่อง
            entry_screenshot = st.text_input("📸 ลิงก์รูปภาพตอน 'เข้าออเดอร์' (Entry Link)", placeholder="วางลิงก์รูปกล้อง TradingView")
            exit_screenshot = st.text_input("🏁 ลิงก์รูปภาพตอน 'จบไม้' (Exit Link)", placeholder="วางลิงก์รูปกล้อง TradingView")
            
        note_input = st.text_area("📝 บันทึกช่วยจำ / อารมณ์และการตัดสินใจ", placeholder="เขียนบันทึกสรุปข้อผิดพลาดหรือข้อดีของไม้นี้...")

        submit_button = st.form_submit_button("💾 บันทึกออเดอร์ลงระบบ (Save Trade)", use_container_width=True)
        
        if submit_button:
            if pair_input:
                sheet = get_google_sheet()
                if sheet:
                    with st.spinner("กำลังบันทึกข้อมูลแบบลงระบบ..."):
                        formatted_date = trade_date.strftime("%Y-%m-%d")
                        result_status = "Win" if pnl_input > 0 else ("Loss" if pnl_input < 0 else "Draft/Breakeven")
                        
                        # เรียงแถวข้อมูลให้ตรงกับหัวข้อคอลัมน์ Google Sheets ใหม่ (13 คอลัมน์)
                        new_row = [
                            formatted_date, 
                            pair_input, 
                            tf_input,
                            side_input, 
                            lotsize_input,
                            points_input,
                            strategy_input, 
                            rr_input, 
                            pnl_input, 
                            result_status, 
                            entry_screenshot.strip(),
                            exit_screenshot.strip(),
                            note_input.strip()
                        ]
                        sheet.append_row(new_row)
                        st.success(f"🎉 บันทึกข้อมูลการเทรดคู่ {pair_input} ({tf_input}) สำเร็จแล้ว!")
                        st.rerun()
            else:
                st.warning("⚠️ กรุณาระบุชื่อคู่เงินก่อนกดบันทึก")

# ================= TAB 2: สมุดบันทึกประวัติและสถิติรวม (พรีวิว 2 รูป) =================
with tab2:
    st.header("📊 หน้าสรุปผลงานและการวิเคราะห์ (Dashboard Analytics)")
    df = load_data()
    
    if not df.empty:
        total_trades = len(df)
        total_pnl = df["PnL"].astype(float).sum()
        
        win_trades = len(df[df["Result"] == "Win"])
        win_rate = (win_trades / total_trades) * 100 if total_trades > 0 else 0
        
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("จำนวนออเดอร์ทั้งหมด (Total Trades)", f"{total_trades} ไม้")
        metric_col2.metric("กำไรสะสมทั้งหมด (Total Net PnL)", f"${total_pnl:,.2f}", delta=f"${total_pnl:,.2f}")
        metric_col3.metric("อัตราการชนะ (Win Rate %)", f"{win_rate:.1f}%")
        
        st.markdown("---")
        st.markdown("### 📜 ประวัติออเดอร์และการแสดงรูปภาพพรีวิว")
        
        display_df = df.copy()
        # ดึงภาพทั้งสองมาเข้าคอลัมน์แสดงผลพรีวิวบนหน้าตาราง
        if "Entry_Screenshot" in display_df.columns:
            display_df["ภาพตอนเข้า (Entry)"] = display_df["Entry_Screenshot"]
        if "Exit_Screenshot" in display_df.columns:
            display_df["ภาพตอนจบ (Exit)"] = display_df["Exit_Screenshot"]
            
        st.data_editor(
            display_df,
            column_config={
                "Date": st.column_config.TextColumn("วันที่"),
                "Pair": st.column_config.TextColumn("สินทรัพย์"),
                "TimeFrame": st.column_config.TextColumn("TF"),
                "Buy/Sell": st.column_config.TextColumn("ฝั่ง"),
                "LotSize": st.column_config.NumberColumn("Lot"),
                "Points": st.column_config.NumberColumn("จุด (Pts)"),
                "Strategy": st.column_config.TextColumn("ระบบเทรด"),
                "Risk/Reward": st.column_config.TextColumn("R:R"),
                "PnL": st.column_config.NumberColumn("กำไร/ขาดทุน ($)", format="$%.2f"),
                "Result": st.column_config.TextColumn("ผลลัพธ์"),
                "Entry_Screenshot": st.column_config.LinkColumn("ลิงก์รูปเข้า"),
                "Exit_Screenshot": st.column_config.LinkColumn("ลิงก์รูปจบ"),
                "ภาพตอนเข้า (Entry)": st.column_config.ImageColumn("📸 ภาพตอนเข้า"),
                "ภาพตอนจบ (Exit)": st.column_config.ImageColumn("🏁 ภาพตอนจบ"),
                "Note": st.column_config.TextColumn("บันทึกเพิ่มเติม")
            },
            use_container_width=True,
            disabled=True
        )
    else:
        st.info("ยังไม่มีข้อมูลการเทรดในระบบตาราง")

# ================= TAB 3: ค้นหาและคัดกรองข้อมูลประวัติ =================
with tab3:
    st.header("🔍 ค้นหาและกรองสถิติรายเทคนิค")
    df = load_data()
    
    if not df.empty:
        search_col1, search_col2, search_col3 = st.columns(3)
        with search_col1:
            unique_pairs = ["ทั้งหมด"] + sorted(df["Pair"].unique().tolist())
            select_pair = st.selectbox("กรองตามคู่เงิน", unique_pairs, key="search_pair")
        with search_col2:
            unique_strategies = ["ทั้งหมด"] + sorted(df["Strategy"].unique().tolist())
            select_strategy = st.selectbox("กรองตามระบบเทรด (Strategy)", unique_strategies, key="search_strat")
        with search_col3:
            select_side = st.selectbox("กรองตามฝั่งออเดอร์", ["ทั้งหมด", "Buy", "Sell"], key="search_side")
            
        filtered_df = df.copy()
        if select_pair != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df["Pair"] == select_pair]
        if select_strategy != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df["Strategy"] == select_strategy]
        if select_side != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df["Buy/Sell"] == select_side]
            
        st.markdown(f"🔍 ค้นพบข้อมูลออเดอร์ที่ตรงเงื่อนไข **{len(filtered_df)}** รายการ")
        
        if "Entry_Screenshot" in filtered_df.columns:
            filtered_df["ภาพตอนเข้า (Entry)"] = filtered_df["Entry_Screenshot"]
        if "Exit_Screenshot" in filtered_df.columns:
            filtered_df["ภาพตอนจบ (Exit)"] = filtered_df["Exit_Screenshot"]
            
        st.data_editor(
            filtered_df,
            column_config={
                "PnL": st.column_config.NumberColumn("กำไร/ขาดทุน ($)", format="$%.2f"),
                "ภาพตอนเข้า (Entry)": st.column_config.ImageColumn("📸 ภาพตอนเข้า"),
                "ภาพตอนจบ (Exit)": st.column_config.ImageColumn("🏁 ภาพตอนจบ")
            },
            use_container_width=True,
            disabled=True
        )
    else:
        st.info("ยังไม่มีข้อมูลสำหรับการค้นหา")

# ================= TAB 4: หน้าแสดงกราฟแนวโน้มเงินทุน (เหมือนเดิม) =================
with tab4:
    st.header("📈 กราฟการเติบโตของพอร์ตลงทุน (Equity Curve)")
    df = load_data()
    
    if not df.empty:
        initial_capital = st.number_input("💰 ระบุเงินต้นเริ่มต้นของคุณ ($)", value=1000.0, step=100.0)
        
        df_chart = df.copy()
        df_chart['Date'] = pd.to_datetime(df_chart['Date'])
        df_chart = df_chart.sort_values(by='Date').reset_index(drop=True)
        
        df_chart['PnL'] = pd.to_numeric(df_chart['PnL'], errors='coerce').fillna(0)
        df_chart['Cumulative_PnL'] = df_chart['PnL'].cumsum()
        df_chart['Current_Balance'] = initial_capital + df_chart['Cumulative_PnL']
        
        total_growth = df_chart['Cumulative_PnL'].iloc[-1]
        final_balance = df_chart['Current_Balance'].iloc[-1]
        
        c1, c2 = st.columns(2)
        c1.metric("เงินทุนสุทธิปัจจุบัน (Current Balance)", f"${final_balance:,.2f}")
        c2.metric("ผลกำไร/ขาดทุนสะสมรวม", f"${total_growth:,.2f}", delta=f"${total_growth:,.2f}")
        
        st.markdown("---")
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_chart['Date'].dt.strftime('%Y-%m-%d'),
            y=[initial_capital] * len(df_chart),
            mode='lines',
            name='Initial Capital (ทุนเริ่มต้น)',
            line=dict(color='rgba(255, 255, 255, 0.4)', width=1.5, dash='dash'),
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=df_chart['Date'].dt.strftime('%Y-%m-%d'),
            y=df_chart['Current_Balance'],
            mode='lines+markers',
            name='Equity Curve',
            line=dict(color='#10b981', width=3),
            marker=dict(size=7, symbol='circle', color='#10b981'),
            hovertemplate="<b>วันที่:</b> %{x}<br><b>เงินในบัญชี:</b> $%{y:,.2f}<extra></extra>"
        ))
        
        fig.update_layout(
            hovermode="x unified",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title="ลำดับวันที่เทรด", showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title="มูลค่าเงินในพอร์ต ($)", showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            margin=dict(l=40, r=40, t=20, b=40),
            height=500,
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("💡 จะสามารถวาดกราฟแนวโน้มได้ ก็ต่อเมื่อคุณมีข้อมูลบันทึกในสมุดประวัติอย่างน้อย 1 รายการขึ้นไปครับ")
