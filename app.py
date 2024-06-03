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

st.subheader("選擇開始與結束的日期, 區間:2022-01-03 至 2024-06-03")
start_date = st.text_input('選擇開始日期 (日期格式: 2022-01-03)', '2022-01-03')
end_date = st.text_input('選擇結束日期 (日期格式: 2024-06-03)', '2024-06-03')
start_date = datetime.datetime.strptime(start_date,'%Y-%m-%d')
end_date = datetime.datetime.strptime(end_date,'%Y-%m-%d')
df = df_original[(df_original['Date'] >= start_date) & (df_original['Date'] <= end_date)]

Date = start_date.strftime("%Y-%m-%d")


# 定義指標的計算函數
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
# 應用各種指標的計算
df = calculate_macd(df)
df = calculate_bollinger_bands(df)
df = calculate_donchian_channels(df)
df = calculate_kd(df)
df = calculate_obv(df)
df = calculate_rsi(df)
fig, axs = plt.subplots(7, figsize=(14, 30))


# 繪製MACD
st.expander("MACD")
axs[1].plot(df['Date'], df['MACD'], label='MACD')
axs[1].plot(df['Date'], df['Signal'], label='Signal')
axs[1].bar(df['Date'], df['MACD'] - df['Signal'], label='MACD Histogram', color='gray')
axs[1].legend()
axs[1].set_title('MACD')

# 繪製布林通道
st.expander("Bollinger Bands")
axs[0].plot(df['Date'], df['Close'], label='Close Price')
axs[0].plot(df['Date'], df['SMA'], label='SMA')
axs[0].plot(df['Date'], df['Upper Band'], label='Upper Band')
axs[0].plot(df['Date'], df['Lower Band'], label='Lower Band')
axs[0].fill_between(df['Date'], df['Lower Band'], df['Upper Band'], color='gray', alpha=0.3)
axs[0].legend()
axs[0].set_title('Bollinger Bands')


st.expander("DC")
axs[2].plot(df['Date'], df['Close'], label='Close Price')
axs[2].plot(df['Date'], df['Upper Channel'], label='Upper Channel')
axs[2].plot(df['Date'], df['Lower Channel'], label='Lower Channel')
axs[2].fill_between(df['Date'], df['Lower Channel'], df['Upper Channel'], color='gray', alpha=0.3)
axs[2].legend()
axs[2].set_title('DC')


st.expander("KD")
axs[3].plot(df['Date'], df['%K'], label='%K')
axs[3].plot(df['Date'], df['%D'], label='%D')
axs[3].legend()
axs[3].set_title('KD')


st.expander("OBV")
axs[4].plot(df['Date'], df['OBV'], label='OBV')
axs[4].legend()
axs[4].set_title('OBV')

st.expander("Candlestick Chart with Moving Averages")
axs[5].plot(df['Date'], df['Close'], label='Close Price')
axs[5].plot(df['Date'], df['Close'].rolling(window=20).mean(), label='20-day MA')
axs[5].plot(df['Date'], df['Close'].rolling(window=50).mean(), label='50-day MA')
axs[5].legend()
axs[5].set_title('Candlestick Chart with Moving Averages')


st.expander("RSI")
axs[6].plot(df['Date'], df['RSI'], label='RSI')
axs[6].axhline(70, color='red', linestyle='--')
axs[6].axhline(30, color='green', linestyle='--')
axs[6].legend()
axs[6].set_title('RSI')

st.pyplot(fig)
