import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta

def plot_stock(stock_symbol):
    # 1. Fetch 1 year of data to calculate the 200 SMA 
    data = yf.download(stock_symbol, period="1y", interval="1d")
    if data.empty: return None
    data.columns = data.columns.get_level_values(0)

    # 2. Calculate Indicators
    data['SMA_50'] = ta.sma(data['Close'], length=50)
    data['SMA_200'] = ta.sma(data['Close'], length=200)
    data['RSI'] = ta.rsi(data['Close'], length=14)

    # Signal Logic: Golden Cross (50 crosses above 200)
    data['Prev_SMA_50'] = data['SMA_50'].shift(1)
    data['Prev_SMA_200'] = data['SMA_200'].shift(1)
    
    golden_cross = data[(data['SMA_50'] > data['SMA_200']) & (data['Prev_SMA_50'] <= data['Prev_SMA_200'])]
    
    # Signal Logic: RSI Extremes
    rsi_oversold = data[data['RSI'] < 30]
    rsi_overbought = data[data['RSI'] > 70]

    # Slice for the last 6 months for the actual display
    display_data = data.tail(120).reset_index()
    golden_cross_display = golden_cross[golden_cross.index >= display_data['Date'].min()]

    # 3. Create Chart
    fig = go.Figure()

    # Base Candlesticks
    fig.add_trace(go.Candlestick(
        x=display_data['Date'], open=display_data['Open'], high=display_data['High'],
        low=display_data['Low'], close=display_data['Close'], name='Price'
    ))

    # ---SMA TRACES---
    fig.add_trace(go.Scatter(
        x=display_data['Date'], y=display_data['SMA_50'], 
        line=dict(color='#FFA500', width=1.8), # Orange 50 SMA
        name='50 SMA'

        
    ))

    fig.add_trace(go.Scatter(
        x=display_data['Date'], y=display_data['SMA_200'], 
        line=dict(color='#FF0000', width=1.8), # Red 200 SMA
        name='200 SMA'
    ))
    # --------------------------------------------------

    # Golden Cross Markers
    fig.add_trace(go.Scatter(
        x=golden_cross_display.index, y=golden_cross_display['SMA_50'],
        mode='markers', name='GOLDEN CROSS',
        marker=dict(symbol='triangle-up', size=15, color='#00ff00', line=dict(width=2, color='white'))
    ))

    # RSI Oversold (Buy Signal) Markers
    fig.add_trace(go.Scatter(
        x=display_data[display_data['RSI'] < 30]['Date'], 
        y=display_data[display_data['RSI'] < 30]['Low'] * 0.98,
        mode='markers', name='RSI Oversold',
        marker=dict(symbol='circle', size=8, color='#00d9ff')
    ))

    # 4.Styling 
    visible_high = display_data['High'].max()
    visible_low = display_data['Low'].min()
    padding = (visible_high - visible_low) * 0.15 

    fig.update_layout(
        template="plotly_dark",
        height=650,
        margin=dict(l=50, r=10, t=50, b=50), 
        xaxis_rangeslider_visible=False,
        paper_bgcolor='#0b1117',
        plot_bgcolor='#0b1117',
        hovermode='x unified',
        
        #Sharpness Settings
        dragmode='pan',
        newshape=dict(line_color='cyan'),
    )

    #Refined Sharpness 
    fig.update_yaxes(
    gridcolor='#1F2937',
    automargin=True,
    range=[visible_low - padding, visible_high + padding],
    tickprefix="$", 
    separatethousands=True,
    tickfont=dict(color="#9CA3AF", size=11),
    showline=True,
    linewidth=1,
    linecolor='#1F2937'
    )

    fig.update_xaxes(
    gridcolor='#1F2937',
    automargin=True
    )

    return fig