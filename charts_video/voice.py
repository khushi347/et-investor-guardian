# charts_video/voice.py
from gtts import gTTS
import os

def generate_guardian_audio(text, filename="briefing.mp3"):
    """
    Converts AI insight text into a 'Guardian' voice file.
    """
    try:
        # 'en-au' (Australian) gives a very professional, distinct 'Guardian' tone
        tts = gTTS(text=text, lang='en', tld='com.au')
        
        # Save in the current directory (charts_video/)
        output_path = os.path.join(os.path.dirname(__file__), filename)
        tts.save(output_path)
        
        print(f"✅ Guardian Voice Generated: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ Audio Error: {e}")
        return None