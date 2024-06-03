import streamlit as st
import numpy as np
import pandas as pd
import streamlit.components.v1 as stc 
import matplotlib.pyplot as plt
import datetime
html_temp = """
		<div style="background-color:#BA55D3;padding:15px;border-radius:10px">
		<h1 style="color:white;text-align:center;">聯詠(3034)金融指標分析 </h1>
		<h2 style="color:white;text-align:center;">Financial Indicators Analysis of Novatek Microelectronics Corp (TPE:3034) </h2>
		</div>
		"""
stc.html(html_temp)

df_original = pd.read_excel("3034.T.xlsx")
df_original.to_pickle('3034.T.pkl')
# 讀取上傳的 Excel 文件
file_path = '3034.T.pkl'
df = pd.read_pickle(file_path)

def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9):
    df['EMA_fast'] = df['Close'].ewm(span=fast_period, min_periods=fast_period).mean()
    df['EMA_slow'] = df['Close'].ewm(span=slow_period, min_periods=slow_period).mean()
    df['MACD'] = df['EMA_fast'] - df['EMA_slow']
    df['Signal'] = df['MACD'].ewm(span=signal_period, min_periods=signal_period).mean()
    return df

def calculate_bollinger_bands(df, window=20, num_of_std=2):
    df['SMA'] = df['Close'].rolling(window=window).mean()
    df['Upper Band'] = df['SMA'] + (df['Close'].rolling(window=window).std() * num_of_std)
    df['Lower Band'] = df['SMA'] - (df['Close'].rolling(window=window).std() * num_of_std)
    return df

def calculate_donchian_channels(df, window=20):
    df['Upper Channel'] = df['High'].rolling(window=window).max()
    df['Lower Channel'] = df['Low'].rolling(window=window).min()
    df['Donchian Channel'] = (df['Upper Channel'] + df['Lower Channel']) / 2
    return df

def calculate_kd(df, period=14):
    df['Lowest Low'] = df['Low'].rolling(window=period).min()
    df['Highest High'] = df['High'].rolling(window=period).max()
    df['%K'] = (df['Close'] - df['Lowest Low']) / (df['Highest High'] - df['Lowest Low']) * 100
    df['%D'] = df['%K'].rolling(window=3).mean()
    return df

def calculate_obv(df):
    df['OBV'] = (df['Volume'] * ((df['Close'] - df['Close'].shift(1)) > 0).astype(int) - df['Volume'] * ((df['Close'] - df['Close'].shift(1)) < 0).astype(int)).cumsum()
    return df

def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

st.subheader("選擇開始與結束的日期, 區間:2022-01-03 至 2024-06-03")
start_date = st.text_input('選擇開始日期 (日期格式: 2022-01-03)', '2022-01-03')
end_date = st.text_input('選擇結束日期 (日期格式: 2024-06-03)', '2024-06-03')
start_date = datetime.datetime.strptime(start_date,'%Y-%m-%d')
end_date = datetime.datetime.strptime(end_date,'%Y-%m-%d')
df = df_original[(df_original['Date'] >= start_date) & (df_original['Date'] <= end_date)]


# 应用各种指标的计算

df = calculate_macd(df)
df = calculate_bollinger_bands(df)
df = calculate_donchian_channels(df)
df = calculate_kd(df)
df = calculate_obv(df)
df = calculate_rsi(df)

# 定義指標的計算函數
def plot_bollinger_bands(ax, df):
    ax.plot(df['Date'], df['Close'], label='Close Price')
    ax.plot(df['Date'], df['SMA'], label='SMA')
    ax.plot(df['Date'], df['Upper Band'], label='Upper Band')
    ax.plot(df['Date'], df['Lower Band'], label='Lower Band')
    ax.fill_between(df['Date'], df['Lower Band'], df['Upper Band'], color='gray', alpha=0.3)
    ax.legend()
    ax.set_title('Bollinger Bands')

def plot_macd(ax, df):
    ax.plot(df['Date'], df['MACD'], label='MACD')
    ax.plot(df['Date'], df['Signal'], label='Signal')
    ax.bar(df['Date'], df['MACD'] - df['Signal'], label='MACD Histogram', color='gray')
    ax.legend()
    ax.set_title('MACD')

def plot_donchian_channels(ax, df):
    ax.plot(df['Date'], df['Close'], label='Close Price')
    ax.plot(df['Date'], df['Upper Channel'], label='Upper Channel')
    ax.plot(df['Date'], df['Lower Channel'], label='Lower Channel')
    ax.fill_between(df['Date'], df['Lower Channel'], df['Upper Channel'], color='gray', alpha=0.3)
    ax.legend()
    ax.set_title('Donchian Channels')

def plot_kd(ax, df):
    ax.plot(df['Date'], df['%K'], label='%K')
    ax.plot(df['Date'], df['%D'], label='%D')
    ax.legend()
    ax.set_title('K and D lines')

def plot_obv(ax, df):
    ax.plot(df['Date'], df['OBV'], label='OBV')
    ax.legend()
    ax.set_title('OBV')

def plot_candlestick_ma(ax, df):
    ax.plot(df['Date'], df['Close'], label='Close Price')
    ax.plot(df['Date'], df['Close'].rolling(window=20).mean(), label='20-day MA')
    ax.plot(df['Date'], df['Close'].rolling(window=50).mean(), label='50-day MA')
    ax.legend()
    ax.set_title('Candlestick Chart with Moving Averages')

def plot_rsi(ax, df):
    ax.plot(df['Date'], df['RSI'], label='RSI')
    ax.axhline(70, color='red', linestyle='--')
    ax.axhline(30, color='green', linestyle='--')
    ax.legend()
    ax.set_title('RSI')

# 绘制布林通道 (Bollinger Bands)
with st.expander("Bollinger Bands"):
    fig, ax = plt.subplots()
    plot_bollinger_bands(ax, df)
    st.pyplot(fig)

# 绘制MACD
with st.expander("MACD"):
    fig, ax = plt.subplots()
    plot_macd(ax, filtered_df)
    st.pyplot(fig)

# 绘制唐奇安通道 (Donchian Channels)
with st.expander("Donchian Channels"):
    fig, ax = plt.subplots()
    plot_donchian_channels(ax, df)
    st.pyplot(fig)

# 绘制K、D线 (K and D lines)
with st.expander("K and D lines"):
    fig, ax = plt.subplots()
    plot_kd(ax, df)
    st.pyplot(fig)

# 绘制OBV
with st.expander("OBV"):
    fig, ax = plt.subplots()
    plot_obv(ax, df)
    st.pyplot(fig)

# 绘制K线图 (Candlestick Chart) 移动平均线
with st.expander("Candlestick Chart with Moving Averages"):
    fig, ax = plt.subplots()
    plot_candlestick_ma(ax, df)
    st.pyplot(fig)

# 绘制RSI
with st.expander("RSI"):
    fig, ax = plt.subplots()
    plot_rsi(ax, df)
    st.pyplot(fig)
