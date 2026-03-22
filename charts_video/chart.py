import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta


def plot_stock(stock_symbol):
    """
    Professional Candlestick chart with EMA + SMA + RSI signals
    """

    # ✅ Auto-fix ticker for Indian stocks
    fetch_symbol = stock_symbol
    if not stock_symbol.endswith(".NS") and not stock_symbol.endswith(".BO"):
        fetch_symbol = f"{stock_symbol}.NS"

    try:
        # ✅ Fetch data
        data = yf.download(fetch_symbol, period="6mo", interval="1d", progress=False)

        if data.empty or len(data) < 50:
            print(f"⚠️ No data for {fetch_symbol}")
            return None

        # Fix multi-index columns
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # ✅ Indicators
        data['EMA_20'] = ta.ema(data['Close'], length=20)
        data['SMA_50'] = ta.sma(data['Close'], length=50)
        data['SMA_200'] = ta.sma(data['Close'], length=200)
        data['RSI'] = ta.rsi(data['Close'], length=14)

        # Golden Cross Logic
        data['Prev_SMA_50'] = data['SMA_50'].shift(1)
        data['Prev_SMA_200'] = data['SMA_200'].shift(1)

        golden_cross = data[
            (data['SMA_50'] > data['SMA_200']) &
            (data['Prev_SMA_50'] <= data['Prev_SMA_200'])
        ]

        # Reset index
        data = data.reset_index()

        # ✅ Create Chart
        fig = go.Figure()

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=data['Date'],
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Price',
            increasing_line_color='#22C55E',
            decreasing_line_color='#EF4444'
        ))

        # EMA Trend
        fig.add_trace(go.Scatter(
            x=data['Date'],
            y=data['EMA_20'],
            line=dict(color='#38BDF8', width=2),
            name='EMA 20'
        ))

        # SMA 50
        fig.add_trace(go.Scatter(
            x=data['Date'],
            y=data['SMA_50'],
            line=dict(color='orange', width=1),
            name='SMA 50'
        ))

        # SMA 200
        fig.add_trace(go.Scatter(
            x=data['Date'],
            y=data['SMA_200'],
            line=dict(color='red', width=1),
            name='SMA 200'
        ))

        # Golden Cross markers
        fig.add_trace(go.Scatter(
            x=golden_cross.index,
            y=golden_cross['SMA_50'],
            mode='markers',
            name='Golden Cross',
            marker=dict(symbol='triangle-up', size=12, color='#00ff00')
        ))

        # RSI Oversold markers
        fig.add_trace(go.Scatter(
            x=data[data['RSI'] < 30]['Date'],
            y=data[data['RSI'] < 30]['Low'] * 0.98,
            mode='markers',
            name='RSI Oversold',
            marker=dict(size=6, color='#00d9ff')
        ))

        # ✅ Layout
        fig.update_layout(
            title=f"🛡️ {stock_symbol} - Market Signal Guard",
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(orientation="h", y=1.02),
            hovermode='x unified'
        )

        # Axis styling
        fig.update_yaxes(
            tickprefix="₹",
            gridcolor='#1F2937'
        )

        fig.update_xaxes(
            gridcolor='#1F2937'
        )

        return fig

    except Exception as e:
        print(f"❌ Error: {e}")
        return None