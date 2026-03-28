from gtts import gTTS
import os
import time

def generate_guardian_audio(text, filename="briefing.mp3"):
    """
    Converts AI insight text into a 'Guardian' voice file.
    Uses a timestamped filename to avoid 'File in Use' errors during rendering.
    """
    try:
        # 1. Clean up old briefing files
        folder = os.path.dirname(__file__)
        
        # 2. Professional Tone 
        tts = gTTS(text=text, lang='en', tld='com.au')
        
        # 3. Dynamic Filename
        unique_name = f"voice_{int(time.time())}.mp3"
        output_path = os.path.join(folder, unique_name)
        
        tts.save(output_path)
        
        # 4. Automatic Cleanup of older mp3 files
        for old_file in os.listdir(folder):
            if old_file.startswith("voice_") and old_file.endswith(".mp3"):
                if old_file != unique_name:
                    try: os.remove(os.path.join(folder, old_file))
                    except: pass

        print(f"✅ Guardian Voice Generated: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Audio Error: {e}")
        return None