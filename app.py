import yfinance as yf
import pandas as pd
import pandas_ta as ta
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="EasyCharts Pro", layout="wide", page_icon="📈")

# Nifty 200 List
STOCKS = [
    "ABB.NS", "ACC.NS", "ADANIENSOL.NS", "ADANIENT.NS", "ADANIGREEN.NS", "ADANIPORTS.NS", "ADANIPOWER.NS", "ATGL.NS", "AWL.NS", "ABCAPITAL.NS",
    "ABFRL.NS", "ALKEM.NS", "AMBUJACEM.NS", "APOLLOHOSP.NS", "APOLLOTYRE.NS", "ASHOKLEY.NS", "ASIANPAINT.NS", "ASTRAL.NS", "AUIPRO.NS", "AUBANK.NS",
    "AUROPHARMA.NS", "DMART.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BAJAJHLDNG.NS", "BALKRISIND.NS", "BANDHANBNK.NS", "BANKBARODA.NS",
    "BANKINDIA.NS", "BATAINDIA.NS", "BERGEPAINT.NS", "BEL.NS", "BHARATFORG.NS", "BHEL.NS", "BPCL.NS", "BHARTIARTL.NS", "BIOCON.NS", "BOSCHLTD.NS",
    "BRITANNIA.NS", "CGPOWER.NS", "CANBK.NS", "CHOLAFIN.NS", "CIPLA.NS", "COALINDIA.NS", "COFORGE.NS", "COLPAL.NS", "CONCOR.NS", "CUMMINSIND.NS",
    "DLF.NS", "DABUR.NS", "DALBHARAT.NS", "DEEPAKNTR.NS", "DELHIVERY.NS", "DIVISLAB.NS", "DIXON.NS", "LALPATHLAB.NS", "DRREDDY.NS", "EICHERMOT.NS",
    "ESCORTS.NS", "FSNREMS.NS", "FEDERALBNK.NS", "FORTIS.NS", "GAIL.NS", "GMRINFRA.NS", "GLAND.NS", "GODREJCP.NS", "GODREJPROP.NS", "GRASIM.NS",
    "GUJGASLTD.NS", "HAL.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HAVELLS.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "HINDPETRO.NS",
    "ICICIBANK.NS", "ICICIGI.NS", "ICICIPRULI.NS", "IDFCFIRSTB.NS", "ITC.NS", "IRCTC.NS", "IRFC.NS", "IGL.NS", "INDHOTEL.NS", "IOC.NS",
    "IRB.NS", "INDIAMART.NS", "INDUSINDBK.NS", "INFY.NS", "INDIGO.NS", "IPCALAB.NS", "JSWENERGY.NS", "JSWSTEEL.NS", "JINDALSTEL.NS", "JIOCINANCE.NS",
    "JUBLFOOD.NS", "KOTAKBANK.NS", "L&TFH.NS", "LTTS.NS", "LICHSGFIN.NS", "LTIM.NS", "LT.NS", "LAURUSLABS.NS", "LICI.NS", "LUPIN.NS",
    "MRF.NS", "M&M.NS", "MARICO.NS", "MARUTI.NS", "MAXHEALTH.NS", "METROPOLIS.NS", "MSUMI.NS", "MPHASIS.NS", "MUTHOOTFIN.NS", "NTPC.NS",
    "NAUKRI.NS", "NESTLEIND.NS", "NMDC.NS", "OBEROIRLTY.NS", "ONGC.NS", "OIL.NS", "PAYTM.NS", "PIIND.NS", "PIDILITIND.NS", "POLYCAB.NS",
    "POONAWALLA.NS", "PFC.NS", "POWERGRID.NS", "PRESTIGE.NS", "PGHH.NS", "PNB.NS", "RELIANCE.NS", "RVNL.NS", "RECLTD.NS", "SBICARD.NS",
    "SBILIFE.NS", "SRF.NS", "MOTHERSON.NS", "SHREECEM.NS", "SHRIRAMFIN.NS", "SIEMENS.NS", "SONACOMS.NS", "SBIN.NS", "SAIL.NS", "SUNPHARMA.NS",
    "SUNTV.NS", "SYNGENE.NS", "TATACOMM.NS", "TATACONSUM.NS", "TATAELXSI.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TCS.NS", "TECHM.NS",
    "TITAN.NS", "TORNTPHARM.NS", "TRENT.NS", "TRIDENT.NS", "TIINDIA.NS", "UPL.NS", "ULTRACEMCO.NS", "UNIONBANK.NS", "VBL.NS", "VEDL.NS",
    "IDEA.NS", "VOLTAS.NS", "WIPRO.NS", "YESBANK.NS", "ZOMATO.NS", "ZYDUSLIFE.NS"
]

# --- DARK UI CUSTOMIZATION ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .header-banner {
        background: linear-gradient(90deg, #2c3e50 0%, #000000 100%);
        padding: 40px; border-radius: 20px; text-align: center; color: white; margin-bottom: 30px;
        border: 1px solid #34495e;
    }
    .metric-card {
        background-color: #1a1c24; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        border-left: 6px solid; margin-bottom: 10px; text-align: left; color: white;
    }
    .card-label { font-size: 14px; color: #95a5a6; font-weight: 600; }
    .card-val { font-size: 40px; font-weight: bold; color: #00ffcc; }
    .stButton>button { background: #3498db; color: white; border-radius: 8px; width: 100%; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def scan_stock(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="60d")
        if df.empty or len(df) < 30: return None
        
        df['EMA_20'] = ta.ema(df['Close'], length=20)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        last = df.iloc[-1]
        
        res = {
            "Stock": symbol.replace(".NS", ""),
            "Price": round(float(last['Close']), 2),
            "RSI": round(float(last['RSI']), 1),
            "Chart": f"https://www.tradingview.com/chart/?symbol=NSE:{symbol.replace('.NS', '')}",
            "Type": None
        }
        
        # Logic Classification
        if last['Close'] > df['High'].iloc[-20:-1].max(): res["Type"] = "Live Breakout"
        elif last['RSI'] > 65: res["Type"] = "Momentum"
        elif last['Close'] > last['EMA_20'] and last['RSI'] > 50: res["Type"] = "Pre-Breakout"
            
        return res if res["Type"] else None
    except: return None

def main():
    st.markdown('<div class="header-banner"><h1>📈 EasyCharts Pro - Dark Edition</h1><p>Organized Real-time Market Analysis</p></div>', unsafe_allow_html=True)
    
    if st.button("🚀 START MARKET SCAN"):
        with st.spinner("Analyzing Nifty 200 Stocks..."):
            results = []
            with ThreadPoolExecutor(max_workers=30) as executor:
                futures = [executor.submit(scan_stock, s) for s in STOCKS]
                for f in as_completed(futures):
                    if f.result(): results.append(f.result())
            
            pre_list = [r for r in results if r['Type'] == "Pre-Breakout"]
            live_list = [r for r in results if r['Type'] == "Live Breakout"]
            mom_list = [r for r in results if r['Type'] == "Momentum"]

            # --- TOP CARDS ---
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card" style="border-left-color: #ff9f43;"><div class="card-label">Pre-Breakout</div><div class="card-val">{len(pre_list)}</div></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card" style="border-left-color: #2ecc71;"><div class="card-label">Live Breakout</div><div class="card-val">{len(live_list)}</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card" style="border-left-color: #3498db;"><div class="card-label">Momentum</div><div class="card-val">{len(mom_list)}</div></div>', unsafe_allow_html=True)

            # --- TABLES ---
            st.divider()
            for title, data, color in [("🟠 Pre-Breakout", pre_list, "pre"), ("🟢 Live Breakout", live_list, "live"), ("🔵 Momentum", mom_list, "mom")]:
                with st.expander(f"{title} Stocks ({len(data)})", expanded=True):
                    if data:
                        st.data_editor(pd.DataFrame(data).drop(columns=['Type']), key=color, column_config={"Chart": st.column_config.LinkColumn(display_text="View 📈")}, use_container_width=True, hide_index=True)
                    else: st.write("No setups found.")

            st.success(f"✅ Scan completed at {datetime.now().strftime('%I:%M:%S %p')}")

if __name__ == "__main__":
    main()