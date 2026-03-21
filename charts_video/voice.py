from gtts import gTTS

def generate_voice(text, filename="output.mp3"):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    return filename