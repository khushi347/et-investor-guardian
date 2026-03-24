import os
import sys
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta
from moviepy import VideoFileClip, ImageClip, AudioFileClip, CompositeVideoClip,ColorClip
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

# Set FFmpeg path for Windows stability
os.environ["IMAGEIO_FFMPEG_EXE"] = imageio_ffmpeg.get_ffmpeg_exe()

# Import your voice logic
sys.path.append(os.path.dirname(__file__))
from voice import generate_guardian_audio


def plot_stock(stock_symbol):
    """Fetches real-time NSE data and builds the Plotly figure."""
    data = yf.download(stock_symbol, period="1y", interval="1d")
    if data.empty:
        return None
    data.columns = data.columns.get_level_values(0)

    # Indicators
    data['SMA_50'] = ta.sma(data['Close'], length=50)
    data['SMA_200'] = ta.sma(data['Close'], length=200)
    data['RSI'] = ta.rsi(data['Close'], length=14)

    display_data = data.tail(100).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=display_data['Date'],
        open=display_data['Open'],
        high=display_data['High'],
        low=display_data['Low'],
        close=display_data['Close'],
        name='Price'
    ))

    # Styling for the 'Hologram' look
    fig.update_layout(
        template="plotly_dark",
        height=800,
        width=1200,
        xaxis_rangeslider_visible=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10,17,23,0.8)',
    )
    fig.update_yaxes(tickprefix="₹", gridcolor='#1F2937')

    return fig


def generate_briefing_video(stock_symbol, ai_data, veo_bg_name="guardian_bg.mp4"):
    """The Winning Engine: Layers Live Chart + AI Voice + Veo Background."""

    # Smart Pathing: Find files relative to THIS script's location
    script_dir = os.path.dirname(__file__)
    veo_bg_path = os.path.join(script_dir, veo_bg_name)
    temp_img = os.path.join(script_dir, "temp_chart.png")

    if not os.path.exists(veo_bg_path):
        print(f"❌ Error: {veo_bg_name} not found in {script_dir}")
        return None

    print(f"🏆 Orchestrating Briefing for {stock_symbol}...")

    # 1. Save Chart as PNG
    fig = plot_stock(stock_symbol)
    fig.write_image(temp_img, scale=2)

    # 2. Generate Audio
    script = f"Guardian Alert for {stock_symbol}. {ai_data.get('insight', '')}. Impact: {ai_data.get('impact', 'Calculating')}."
    audio_path = generate_guardian_audio(script)
    audio_clip = AudioFileClip(audio_path)

    # 3. Load & Setup Background
    bg_clip = VideoFileClip(veo_bg_path)
    target_w, target_h = 1280, 720
    crop_w = min(bg_clip.w, 1920)
    crop_h = min(bg_clip.h, 1080)

    x1 = (bg_clip.w - crop_w) / 2
    y1 = (bg_clip.h - crop_h) / 2
    x2 = x1 + crop_w
    y2 = y1 + crop_h

    bg_clip = bg_clip.cropped(x1=x1, y1=y1, x2=x2, y2=y2)\
                 .resized(new_size=(target_w, target_h))

    # Check if audio is longer than video
    if audio_clip.duration > bg_clip.duration:
        from moviepy import concatenate_videoclips
        n_loops = int(audio_clip.duration / bg_clip.duration) + 1
        bg_clip = concatenate_videoclips([bg_clip] * n_loops)

    # Trim to match audio exactly
    bg_clip = bg_clip.with_duration(audio_clip.duration)

    # 4. Create Overlay (FIXED CENTER ALIGNMENT)
    chart_overlay = (ImageClip(temp_img)
                     .with_duration(audio_clip.duration)
                     .resized(0.55)
                     .with_opacity(1.0)
                     .with_position(("center", "center")))

        # 4.5 Create Subtitle
        # 4.5 Create Bottom Info Panel (NO TextClip issues)

    # 4.5 Create Bottom Panel with TEXT (Stable Method)

    panel_height = 120
    panel_width = 1280

    # Create image
    panel_img = Image.new("RGBA", (panel_width, panel_height), (0, 0, 0, 160))
    draw = ImageDraw.Draw(panel_img)

    # Load font (safe)
    font_path = "C:/Windows/Fonts/arial.ttf"
    font = ImageFont.truetype(font_path, 28)

    # Text content
    text = f"{stock_symbol}: {ai_data.get('insight', '')} | Impact: {ai_data.get('impact', '')}"

    # Draw text
    draw.text((40, 35), text, font=font, fill=(255, 255, 255))

    # Save temp panel
    panel_path = os.path.join(script_dir, "temp_panel.png")
    panel_img.save(panel_path)

    # Convert to clip
    panel = (ImageClip(panel_path)
            .with_duration(audio_clip.duration)
         .with_position(("center", 720 - panel_height)))


    final_video = CompositeVideoClip([
    bg_clip,
    chart_overlay,
    panel
    ]).with_audio(audio_clip)

    output_name = f"GUARDIAN_REPORT_{stock_symbol.split('.')[0]}.mp4"
    output_path = os.path.join(script_dir, output_name)

    final_video.write_videofile(
        output_path,
        fps=12,
        codec="libx264",
        audio_codec="libmp3lame",
        preset="ultrafast",
        logger=None
    )

    # 6. Cleanup
    audio_clip.close()
    bg_clip.close()
    if os.path.exists(temp_img):
        os.remove(temp_img)
    if os.path.exists(panel_path):
        os.remove(panel_path)

    return output_path