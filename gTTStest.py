from gtts import gTTS
import os

tts = gTTS(text="Hello. My name is Iris. I was made by Peter and Christophe, and I live at 61 34 Washington Boulevard.", lang='en')
tts.save("tts.mp3")
os.system("aplay -D plughw:1,0 tts.mp3")
