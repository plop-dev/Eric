import speech_recognition as sr
import pyttsx3
from datetime import datetime, date
import webbrowser
from ctypes import WinDLL
import random
import os
from SwSpotify import spotify
from dotenv import load_dotenv
import time

load_dotenv()
user32 = WinDLL("user32")
greetings = ['Hi plop', 'Hello plop', 'Hey plop', 'Okay plop', 'Alright plop']
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, phrase_time_limit=3)
        try:
            text = r.recognize_whisper_api(audio, api_key=OPENAI_API_KEY)
            print(f"User: {text}")
            return text
        except sr.UnknownValueError:
            # speak("Sorry, I didn't understand that. Could you please repeat?")
            return listen()

def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('volume', 100)
    
    for _ in range(15):
        user32.keybd_event(0xAE, 0, 0, 0)
        user32.keybd_event(0xAE, 0, 2, 0)
    
    for _ in range(15):
        user32.keybd_event(0xAF, 0, 0, 0)
        user32.keybd_event(0xAF, 0, 2, 0)
    
    engine.say(text)
    engine.runAndWait()

while True:
    time.sleep(1)
    textRAW: str = listen()
    textRAW.replace(',', '')
    
    if textRAW.lower().__contains__('hey eric'):
        text = textRAW.lower().split('hey eric')[1].strip()
 
        if text == "what's the time":
            now = datetime.now()
            speak(random.choice(greetings) + ", it's currently " + now.strftime('%I:%M%p'))
        elif text == 'what is the date':
            today = date.today()
            speak(random.choice(greetings) + ", it's currently " + today.strftime("%B %d"))
        elif text.startswith('search up'):
            arg = text.split('search up')[1]
            webbrowser.open("https://www.google.com/search?q=" + arg, new=0, autoraise=True)
            speak(random.choice(greetings) + ", I searched up" + arg)
        
        elif text.startswith('increase volume'):
            for _ in range(2):
                user32.keybd_event(0xAF, 0, 0, 0)
                user32.keybd_event(0xAF, 0, 2, 0)
            speak(random.choice(greetings) + ", I increased the volume by 2%")
        elif text.startswith('decrease volume'):
            for _ in range(2):
                user32.keybd_event(0xAE, 0, 0, 0)
                user32.keybd_event(0xAE, 0, 2, 0)
            speak(random.choice(greetings) + ", I decreased the volume by 2%")
            
        elif text.startswith('what song is this'):
            try:
                speak(random.choice(greetings) + ", Spotify is playing " + spotify.song() + " by " + spotify.artist())
            except spotify.SpotifyNotRunning as e:
                speak('Spotify is not playing anything right now.')
