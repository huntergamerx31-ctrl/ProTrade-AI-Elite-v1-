# =========================================
# ProTrade AI Elite v7 – Stable Edition
# =========================================

import streamlit as st

st.set_page_config(
    page_title="ProTrade AI Elite v7",
    layout="wide"
)

import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ================= UI =================

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#141e30,#243b55); color:white;}
.glass {background: rgba(255,255,255,0.08); padding:20px; border-radius:15px;}
.buy {border-left:5px solid #00ff99;}
.sell {border-left:5px solid #ff3b3b;}
.hold {border-left:5px solid #00bfff;}
.warning {
background-color: rgba(255,165,0,0.1);
border-left: 5px solid orange;
padding: 15px;
border-radius: 8px;
margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 ProTrade AI Elite v7 – Stable")

# ================= LOAD NSE DATABASE SAFELY =================

@st.cache_data
def load_nse():
    try:
        url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        df = pd.read_csv(url)
        df = df[['SYMBOL','NAME OF COMPANY']]
        df.columns = ['Symbol','Company']
        return df
    except:
        return None

nse_data = load_nse()

# ================= STOCK SEARCH =================

if nse_data is not None:
    option = st.selectbox(
        "🔍 Search Indian Stock",
        nse_data['Company'] + " (" + nse_data['Symbol'] + ")"
    )
    symbol = option.split("(")[-1].replace(")","")
else:
    st.warning("⚠ NSE database unavailable. Use manual symbol input.")
    symbol = st.text_input("Enter NSE Symbol manually (Example: RELIANCE)", "RELIANCE")

ticker = symbol.upper() + ".NS"

# ================= FETCH DATA SAFELY =================

try:
    df = yf.download(ticker, period="6mo", interval="1d",
                     auto_adjust=True, progress=False)

    if df.empty:
        st.error("No stock data found.")
        st.stop()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

except Exception as e:
    st.error("Error fetching stock data.")
    st.stop()

# ================= INDICATORS =================

df['SMA20'] = df['Close'].rolling(20).mean()
df['SMA50'] = df['Close'].rolling(50).mean()

def rsi(data, period=14):
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

df['RSI'] = rsi(df['Close'])

latest = df.iloc[-1]
prev = df.iloc[-2]

price = latest['Close']
change = round(((price-prev['Close'])/prev['Close'])*100,2)
rsi_val = round(latest['RSI'],2)

trend = "Bullish" if latest['SMA20'] > latest['SMA50'] else "Bearish"

# ================= AI SIGNAL =================

if rsi_val < 35 and trend=="Bullish":
    signal="STRONG BUY"; prob=85; css="buy"
elif rsi_val > 65 and trend=="Bearish":
    signal="STRONG SELL"; prob=85; css="sell"
elif 40<rsi_val<60:
    signal="HOLD"; prob=60; css="hold"
else:
    signal="WAIT"; prob=50; css="hold"

# ================= DASHBOARD =================

col1,col2,col3 = st.columns(3)
col1.metric("Price",f"₹{round(price,2)}",f"{change}%")
col2.metric("RSI",rsi_val)
col3.metric("Trend",trend)

st.markdown(f"""
<div class="glass {css}">
<h2>AI Signal: {signal}</h2>
<h3>Probability: {prob}%</h3>
</div>
""",unsafe_allow_html=True)

st.markdown("""
<div class="warning">
⚠️ DISCLAIMER: Trading involves risk. AI signals are for study only.
Do your own research before investing.
</div>
""", unsafe_allow_html=True)

# ================= CHART =================

fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close']
))

fig.add_trace(go.Scatter(x=df.index,y=df['SMA20'],name="SMA20"))
fig.add_trace(go.Scatter(x=df.index,y=df['SMA50'],name="SMA50"))

fig.update_layout(
    template="plotly_dark",
    height=600,
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)
