import os
import sys
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta
import time
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, ColorClip, AudioFileClip, CompositeVideoClip
from gtts import gTTS

script_dir = os.path.dirname(__file__)
sys.path.append(script_dir)

try:
    from voice import generate_guardian_audio
except ImportError:
    # Fallback if voice.py is in the same directory
    from charts_video.voice import generate_guardian_audio

def plot_stock(stock_symbol):
    """Fetches data, calculates indicators, and saves a PNG for the video engine."""
    # 1. Fetch 1 year of data
    data = yf.download(stock_symbol, period="1y", interval="1d")
    
    if data.empty:
        return None
    
    # Standardize MultiIndex columns from yfinance
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # 2. Indicators Calculation
    data['SMA_50'] = ta.sma(data['Close'], length=50)
    data['SMA_200'] = ta.sma(data['Close'], length=200)
    data['RSI'] = ta.rsi(data['Close'], length=14)

    # 3. Display Data (Last 120 days)
    display_data = data.tail(120).reset_index()
    
    # 4. Create War Room Figure
    fig = go.Figure()

    # Main Candlesticks
    fig.add_trace(go.Candlestick(
        x=display_data['Date'],
        open=display_data['Open'],
        high=display_data['High'],
        low=display_data['Low'],
        close=display_data['Close'],
        name='Price',
        increasing_line_color='#00FFAB', decreasing_line_color='#FF4B4B'
    ))

    # SMA Traces
    fig.add_trace(go.Scatter(
        x=display_data['Date'], y=display_data['SMA_50'], 
        line=dict(color='#FFA500', width=1.8), name='50 SMA'
    ))

    fig.add_trace(go.Scatter(
        x=display_data['Date'], y=display_data['SMA_200'], 
        line=dict(color='#FF0000', width=1.8), name='200 SMA'
    ))

    oversold_data = display_data[display_data['RSI'] < 30]
    
    if not oversold_data.empty:
        fig.add_trace(go.Scatter(
            x=oversold_data['Date'], 
            # Position markers slightly below the daily low for better visibility
            y=oversold_data['Low'] * 0.98, 
            mode='markers',
            name='RSI Oversold (Potential Buy)',
            marker=dict(
                symbol='circle',
                size=12,
                color='#00D4FF', 
                line=dict(width=1, color='white')
            ),
            hoverinfo='text',
            text=[f"RSI: {r:.2f}" for r in oversold_data['RSI']]
        ))

    # 5. Styling
    visible_high = display_data['High'].max()
    visible_low = display_data['Low'].min()
    padding = (visible_high - visible_low) * 0.15 

    fig.update_layout(
        template="plotly_dark",
        height=650,
        margin=dict(l=50, r=20, t=50, b=50),
        xaxis_rangeslider_visible=False,
        paper_bgcolor='#050A14', 
        plot_bgcolor='#050A14',
        hovermode='x unified',
        legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center", bgcolor="rgba(0,0,0,0)")
    )

    fig.update_yaxes(range=[visible_low - padding, visible_high + padding], tickprefix="₹")

    #  IMAGE FOR VIDEO ENGINE 
    chart_img_path = os.path.join(script_dir, "temp_chart.png")
    fig.write_image(chart_img_path, width=1200, height=700, scale=2)
    
    return fig

def generate_briefing_video(ticker, advice_data):
    """Generates the ET Markets style video using MoviePy 2.0+."""
    stock_name = ticker.replace(".NS", "")
    
    # 1. GENERATE AUDIO 
    voice_script = advice_data.get('script', f"Guardian analysis for {stock_name} is ready.")
    audio_path = generate_guardian_audio(voice_script)
    
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    output_path = os.path.join(script_dir, f"FINAL_REPORT_{stock_name}.mp4")

    # 2. WAIT FOR IMAGE SYNC
    # Ensure plot_stock was called recently to generate 'temp_chart.png'
    chart_img_path = os.path.join(script_dir, "temp_chart.png")
    time.sleep(1.0) # Buffer for file system I/O

    # 3. CONSTRUCT LAYERS 
    # Layer 0: Background
    bg = ColorClip(size=(1280, 720), color=(5, 15, 30)).with_duration(duration)

    # Layer 1: Chart
    if os.path.exists(chart_img_path):
        chart_clip = (ImageClip(chart_img_path)
                      .with_duration(duration)
                      .resized(width=1050) 
                      .with_position(("center", 60)))
    else:
        chart_clip = ColorClip(size=(100, 100), color=(255, 0, 0)).with_duration(duration)

    # Layer 2: Lower Third Panel
    panel_h = 150
    panel_img = Image.new("RGBA", (1280, panel_h), (10, 30, 60, 240))
    draw = ImageDraw.Draw(panel_img)
    draw.rectangle([0, 0, 1280, 8], fill="#00D4FF") # Neon Accent
    
    try:
        # Check standard Windows font paths
        font_main = ImageFont.truetype("arial.ttf", 45)
        font_sub = ImageFont.truetype("arial.ttf", 26)
    except:
        font_main = font_sub = ImageFont.load_default()

    draw.text((70, 30), f"GUARDIAN NODE: {stock_name}", font=font_main, fill="#00D4FF")
    draw.text((70, 90), f"{advice_data.get('insight', 'HOLD')} | IMPACT: {advice_data.get('impact', '₹0')}", font=font_sub, fill="white")
    
    panel_temp = os.path.join(script_dir, "temp_panel_render.png")
    panel_img.save(panel_temp)
    panel_overlay = (ImageClip(panel_temp)
                    .with_duration(duration)
                    .with_position(("center", "bottom")))

    # 4. FINAL COMPOSITE
    final_video = CompositeVideoClip([bg, chart_clip, panel_overlay])
    final_video = final_video.with_audio(audio_clip).with_duration(duration)

    # 5. RENDER
    final_video.write_videofile(
        output_path, 
        fps=15, 
        codec="libx264", 
        audio_codec="aac", 
        preset="ultrafast", 
        logger=None,
        threads=4
    )

    # 6. CLEANUP
    audio_clip.close()
    try:
        if os.path.exists(audio_path): os.remove(audio_path)
        if os.path.exists(panel_temp): os.remove(panel_temp)
    except:
        pass 

    return output_path