import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta

def plot_stock(stock_symbol):
    # 1. Fetch data (1 month for trend, but we fetch 6 months to calculate 200-day EMA later)
    # For today's 1-month view, we'll slice the display but keep the data for logic
    data = yf.download(stock_symbol, period="3mo", interval="1d")
    
    if data.empty:
        return None

    # Fix multi-level columns from yfinance
    data.columns = data.columns.get_level_values(0)
    
    # 2. Calculate Indicators (Prep for March 22 Milestone)
    data['EMA_20'] = ta.ema(data['Close'], length=20)
    data['RSI'] = ta.rsi(data['Close'], length=14)
    
    # Reset index to get Date as a column
    data = data.reset_index()

    # 3. Create a Candlestick Chart (More professional than a line)
    fig = go.Figure()

    # Add Candlesticks
    fig.add_trace(go.Candlestick(
        x=data['Date'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Price'
    ))

    # Add a Trend Line (20-day EMA)
    fig.add_trace(go.Scatter(
        x=data['Date'], 
        y=data['EMA_20'],
        line=dict(color='#00ff88', width=1.5),
        name='Guardian Trend (20 EMA)'
    ))

    # 4. Professional "War Room" Styling
    fig.update_layout(
        title=f"🛡️ {stock_symbol} - Market Signal Guard",
        template="plotly_dark",
        xaxis_rangeslider_visible=False, # Hides the messy slider at the bottom
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Add Rupee Prefix and Grid Styling
    fig.update_yaxes(tickprefix="₹", gridcolor='#333')
    fig.update_xaxes(gridcolor='#333') 

    return fig