import streamlit as st
import numpy as np
import pandas as pd
import streamlit.components.v1 as stc 
import matplotlib.pyplot as plt
import datetime

st.set_page_config(layout = 'wide',initial_sidebar_state='expanded')

st.sidebar.header('選擇開始與結束的日期, 區間:2022-01-03 至 2024-06-03')
start_date_input = st.sidebar.text_input('選擇開始日期 (日期格式: 2022-01-03)', '2022-01-03')
end_date_input = st.sidebar.text_input('選擇結束日期 (日期格式: 2024-06-03)', '2024-06-03')

# 轉換日期格式
start_date = datetime.datetime.strptime(start_date_input, '%Y-%m-%d')
end_date = datetime.datetime.strptime(end_date_input, '%Y-%m-%d')

# 顯示所選日期
st.write(f"開始日期: {start_date.strftime('%Y-%m-%d')}")
st.write(f"結束日期: {end_date.strftime('%Y-%m-%d')}")


html_temp = """
		<div style="background-color:#BA55D3;padding:20px;border-radius:10px">
		<h1 style="color:white;text-align:center;">聯詠(3034)金融指標分析 </h1>
		<h2 style="color:white;text-align:center;font-size:14px;">Financial Indicators Analysis of Novatek Microelectronics Corp (TPE:3034) </h2>
		</div>
		"""
stc.html(html_temp)

df_original = pd.read_excel("3034.T.xlsx")
df_original.to_pickle('3034.T.pkl')
# 讀取上傳的 Excel 文件
file_path = '3034.T.pkl'
df = pd.read_pickle(file_path)
df = df_original[(df_original['Date'] >= start_date) & (df_original['Date'] <= end_date)]
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



# 应用各种指标的计算

df = calculate_macd(df)
df = calculate_bollinger_bands(df)
df = calculate_donchian_channels(df)
df = calculate_kd(df)
df = calculate_obv(df)
df = calculate_rsi(df)

import plotly.graph_objects as go
def plot_bollinger_bands(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA'], mode='lines', name='SMA'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Upper Band'], mode='lines', name='Upper Band'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Lower Band'], mode='lines', name='Lower Band'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Upper Band'], fill=None, mode='lines', line_color='rgba(0,0,0,0)'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Lower Band'], fill='tonexty', mode='lines', line_color='rgba(0,0,0,0)', fillcolor='rgba(128,128,128,0.3)'))
    fig.update_layout(title='Bollinger Bands', xaxis_title='Date', yaxis_title='Price')
    return fig

def plot_macd(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MACD'], mode='lines', name='MACD'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Signal'], mode='lines', name='Signal'))
    fig.add_trace(go.Bar(x=df['Date'], y=df['MACD'] - df['Signal'], name='MACD Histogram'))
    fig.update_layout(title='MACD', xaxis_title='Date', yaxis_title='Value')
    return fig

def plot_donchian_channels(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Upper Channel'], mode='lines', name='Upper Channel'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Lower Channel'], mode='lines', name='Lower Channel'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Upper Channel'], fill=None, mode='lines', line_color='rgba(0,0,0,0)'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Lower Channel'], fill='tonexty', mode='lines', line_color='rgba(0,0,0,0)', fillcolor='rgba(128,128,128,0.3)'))
    fig.update_layout(title='Donchian Channels', xaxis_title='Date', yaxis_title='Price')
    return fig

def plot_kd(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['%K'], mode='lines', name='%K'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['%D'], mode='lines', name='%D'))
    fig.update_layout(title='K and D lines', xaxis_title='Date', yaxis_title='Value')
    return fig

def plot_obv(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['OBV'], mode='lines', name='OBV'))
    fig.update_layout(title='OBV', xaxis_title='Date', yaxis_title='Value')
    return fig

def plot_candlestick_ma(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'].rolling(window=20).mean(), mode='lines', name='20-day MA'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'].rolling(window=50).mean(), mode='lines', name='50-day MA'))
    fig.update_layout(title='Candlestick Chart with Moving Averages', xaxis_title='Date', yaxis_title='Price')
    return fig

def plot_rsi(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], mode='lines', name='RSI'))
    fig.add_shape(type='line', x0=df['Date'].min(), y0=70, x1=df['Date'].max(), y1=70, line=dict(color='Red', dash='dash'))
    fig.add_shape(type='line', x0=df['Date'].min(), y0=30, x1=df['Date'].max(), y1=30, line=dict(color='Green', dash='dash'))
    fig.update_layout(title='RSI', xaxis_title='Date', yaxis_title='Value')
    return fig

# Load your dataframe 'df' here

# Display plots in Streamlit
st.set_option('deprecation.showPyplotGlobalUse', False)

# Bollinger Bands
with st.expander("Bollinger Bands"):
    fig = plot_bollinger_bands(df)
    st.plotly_chart(fig)

# MACD
with st.expander("MACD"):
    fig = plot_macd(df)
    st.plotly_chart(fig)

# Donchian Channels
with st.expander("Donchian Channels"):
    fig = plot_donchian_channels(df)
    st.plotly_chart(fig)

# K and D lines
with st.expander("K and D lines"):
    fig = plot_kd(df)
    st.plotly_chart(fig)

# OBV
with st.expander("OBV"):
    fig = plot_obv(df)
    st.plotly_chart(fig)

# Candlestick Chart with Moving Averages
with st.expander("Candlestick Chart with Moving Averages"):
    fig = plot_candlestick_ma(df)
    st.plotly_chart(fig)

# RSI
with st.expander("RSI"):
    fig = plot_rsi(df)
    st.plotly_chart(fig)
