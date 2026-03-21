import yfinance as yf
import plotly.express as px
import pandas as pd

def plot_stock(stock_symbol):
    data = yf.download(stock_symbol, period="1mo", interval="1d")

    data.columns = data.columns.get_level_values(0)

    data = data.reset_index()
    data['Date'] = pd.to_datetime(data['Date'])

    fig = px.line(
        data,
        x='Date',
        y='Close',
        title=f"{stock_symbol} - Last 1 Month Trend"
    )

    fig.update_layout(
        template="plotly_dark",
        height=500
    )

    fig.update_yaxes(tickprefix="₹")

    return fig