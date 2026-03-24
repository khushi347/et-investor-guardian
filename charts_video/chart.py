import os
import sys
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta
from moviepy import ImageClip, AudioFileClip
import imageio_ffmpeg

# Set FFmpeg path for Windows
os.environ["IMAGEIO_FFMPEG_EXE"] = imageio_ffmpeg.get_ffmpeg_exe()

# Ensure voice.py can be imported from the same directory
sys.path.append(os.path.dirname(__file__))
from voice import generate_guardian_audio

def plot_stock(stock_symbol):
    """Fetches data and builds the Plotly figure."""
    data = yf.download(stock_symbol, period="1y", interval="1d")
    if data.empty: return None
    data.columns = data.columns.get_level_values(0)

    data['SMA_50'] = ta.sma(data['Close'], length=50)
    data['SMA_200'] = ta.sma(data['Close'], length=200)
    data['RSI'] = ta.rsi(data['Close'], length=14)

    display_data = data.tail(120).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=display_data['Date'], open=display_data['Open'], high=display_data['High'],
        low=display_data['Low'], close=display_data['Close'], name='Price'
    ))

    fig.add_trace(go.Scatter(x=display_data['Date'], y=display_data['SMA_50'], line=dict(color='#FFA500', width=1.8), name='50 SMA'))
    fig.add_trace(go.Scatter(x=display_data['Date'], y=display_data['SMA_200'], line=dict(color='#FF0000', width=1.8), name='200 SMA'))

    fig.update_layout(
        template="plotly_dark", height=720, width=1280,
        xaxis_rangeslider_visible=False, paper_bgcolor='#0b1117', plot_bgcolor='#0b1117',
    )
    fig.update_yaxes(tickprefix="₹", gridcolor='#1F2937')
    return fig

def generate_briefing_video(stock_symbol, ai_data):
    """Renders chart to image, generates audio, and stitches video."""
    print(f"🎬 Processing Guardian Briefing for {stock_symbol}...")

    # 1. SAVE CHART AS IMAGE (Missing in your previous version)
    fig = plot_stock(stock_symbol)
    temp_img = os.path.join(os.path.dirname(__file__), "temp_chart.png")
    fig.write_image(temp_img, engine="kaleido", scale=2)

    # 2. GENERATE AUDIO PATH
    script = f"Guardian Alert for {stock_symbol}. {ai_data['insight']}. Estimated impact: {ai_data['impact']}."
    audio_path = generate_guardian_audio(script)

    if not audio_path or not os.path.exists(audio_path):
        print("❌ Audio file not found!")
        return

    # 3. LOAD CLIPS (Using MoviePy 2.0+ syntax)
    audio_clip = AudioFileClip(audio_path)
    video_clip = ImageClip(temp_img).with_duration(audio_clip.duration)
    
    # 4. EXPLICITLY MERGE
    final_video = video_clip.with_audio(audio_clip)

    # 5. EXPORT
    output_name = f"Guardian_{stock_symbol.split('.')[0]}.mp4"
    print("⏳ Rendering final video...")
    
    final_video.write_videofile(
        output_name, 
        fps=10, 
        codec="libx264", 
        audio_codec="libmp3lame", 
        temp_audiofile="temp-audio.mp3", 
        remove_temp=True
    )
    
    # 6. CLEANUP & RELEASE
    audio_clip.close()
    video_clip.close()
    if os.path.exists(temp_img): os.remove(temp_img)
    
    print(f"🚀 SUCCESS: {output_name} is ready with sound.")

if __name__ == "__main__":
    sample_data = {
        "insight": "RSI is currently oversold. Potential rebound expected at support levels.",
        "impact": "+₹3,500"
    }
    generate_briefing_video("RELIANCE.NS", sample_data)