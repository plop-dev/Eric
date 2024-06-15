import speech_recognition as sr
import os
from openai import OpenAI
from dotenv import load_dotenv
import io
import soundfile
import sounddevice
import random
from io import BytesIO
import requests
from bs4 import BeautifulSoup
from playsound import playsound
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import EricCommands
import EricUtils
import threading

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVEN_API_KEY = os.getenv('ELEVEN_API_KEY')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET  = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_DEVICE_ID = os.getenv('SPOTIFY_DEVICE_ID')

client = OpenAI(api_key=OPENAI_API_KEY)
scope = "user-read-playback-state,user-modify-playback-state"
sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, scope=scope, redirect_uri='http://google.com/callback/'))

user_query: str

sound_file = BytesIO()

def get_audio_file(text, path):
    speech_response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=text,
        speed=1.0,
    )
    speech_response.stream_to_file(path)

def speak(text):
    print('sending speech input to tts')
    speech_thread = threading.Thread(target=speak_thread_func, args=(text,))
    speech_thread.run()

def speak_thread_func(text):
    speech_response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=text,
        speed=1.0,
    )
    
    buffer = io.BytesIO()
    for chunk in speech_response.iter_bytes(chunk_size=2048):
        buffer.write(chunk)
    buffer.seek(0)
    
    with soundfile.SoundFile(buffer, 'r') as sound_file:
        data = sound_file.read(dtype='int16')
        sounddevice.play(data, sound_file.samplerate)
        sounddevice.wait()
        
    print('speak done')


def imlistening():
    choice = random.randint(1, 3)
    playsound(os.path.dirname(__file__) + f'/listening/{choice}.mp3')

def justwaitasec():
    choice = random.randint(1, 3)
    playsound(os.path.dirname(__file__) + f'/justwaitasec/{choice}.mp3')

def repeat():
    choice = random.randint(1, 2)
    playsound(os.path.dirname(__file__) + f'/repeat/{choice}.mp3')

def noresult():
    choice = random.randint(1, 2)
    playsound(os.path.dirname(__file__) + f'/noresults/{choice}.mp3')
    

def search(query):
    url = f"https://www.google.com/search?q={query}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0'
    }
    print("searching up:", query)
    response = requests.get(url, headers=headers)

    print("searching http code:", response.status_code)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        answer = soup.select_one(".Z0LcW.t2b5Cf")
        description = soup.select_one(".hgKElc")
        long_answer = soup.select_one(".hgKElc")

        if answer:
            if len(answer.find_all()) > 0:
                answer = answer.findChild().get_text()
            else:
                answer = answer.get_text()
            
            if description:
                description = description.get_text()
            else:
                description = "None provided."
            
            print(f"Answer: {answer}\nDescription: {description}")
            
            # text_responseRAW = client.chat.completions.create(
            #     model="gpt-3.5-turbo",
            #     messages=[
            #         {"role": "system", "content": "You use information provided to answer a question. You do not use your previous knowledge."},
            #         {"role": "user", "content": f"Use this information: \"{answer}\" and \"{description}\" to answer the question, \"{query}\". Make your answer at least 10 words."},
            #     ],
            # )
            # text_response = text_responseRAW.choices[0].message.content
            speak(answer + ". " + description)
            return
        elif long_answer:
            long_answer = long_answer.get_text()
            print(f"Long Answer: {long_answer}")
            
            # text_responseRAW = client.chat.completions.create(
            #     model="gpt-3.5-turbo",
            #     messages=[
            #             {"role": "system", "content": "You use information provided to answer a question. You do not use your previous knowledge."},
            #             {"role": "user", "content": f"Use this information: \"{long_answer}\" to answer the question, \"{query}\". Make your answer at least 10 words."},
            #         ],
            # )
            # text_response = text_responseRAW.choices[0].message.content
            speak(long_answer)
        else:
            noresult()


def discuss(text, r, audio):
    recent_keywords = ["search up", "look up", "recent", "latest", "current", "in the last few years", 'right now', 'newest', 'new', 'how old']
    is_recent = any(keyword in text for keyword in recent_keywords)
    if is_recent:
        for keyword in recent_keywords:
            if keyword in text:
                text = text.replace(keyword, "").strip()
                search(text)
                break
    else:
        _audio = audio
        _text = text
        _r = r
        conversation = [{"role": "system", "content": "Your name is Eric and you're kind, friendly and loyal. My name is plop, we've already met. Don't make your answers too long."},]
        while True:
            discuss_user_queryRAW: str = _r.recognize_whisper_api(_audio, api_key=OPENAI_API_KEY).lower().replace(',', '')
            if discuss_user_queryRAW.__len__() >= 5:
                discuss_user_query = ' '.join(discuss_user_queryRAW.lower().split(' '))
                
                _text = discuss_user_query
                print("discuss", _text)
                if _text.__contains__('bye') or _text.__contains__('goodbye') or _text.__contains__('nevermind'):
                    choice = random.randint(1, 2)
                    playsound(os.path.dirname(__file__) + f'/bye/{choice}.mp3')
                    print("stop discussion")
                    break
                conversation.append({"role": "user", "content": _text})
                text_responseRAW = client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    messages=[
                        *conversation
                    ],
                )
                text_response = text_responseRAW.choices[0].message.content
                print(text_response)
                speak(text_response)
                conversation.append({"role": "system", "content": text_response})
            else:
                repeat()
            
            _r = sr.Recognizer()
            with sr.Microphone() as source:
                _r.adjust_for_ambient_noise(source)
                print("listening in discuss")
                _audio = _r.listen(source)
                print("heard in discuss")


command_map = {
    "('what is'; or \"what's\";) and 'time'; or 'what time is it';": EricCommands.SayTime,
    "('pause'; or 'resume';) and ('the song'; or 'spotify'; or 'the music';)": EricCommands.PlayPause,
    "('play'; or 'play the song';) and 'by';": EricCommands.SearchSong,
    "'play'; and 'main playlist';": EricCommands.PlayMainPlaylist,
    "('what is'; or \"what's\";) and 'song'; and 'called'; or 'what song is this';": EricCommands.GetPlayingSong,
    "'add'; and ('to my queue'; or 'to the queue';)": EricCommands.AddSongToQueue,
    "'skip'; and ('this'; or 'the';) and 'song';": EricCommands.SkipSong,
    "'set the spotify volume to'; or 'set spotify volume to';": EricCommands.SetSpotifyVolume
}

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        imlistening()
        print("Ready!")
        audio = r.listen(source)
        print("Done!")

    try:
        user_queryRAW: str = r.recognize_whisper_api(audio, api_key=OPENAI_API_KEY).lower().replace(',', '')
        user_query = ' '.join(user_queryRAW.lower().split(' '))
        
        print("User:", user_query)
    
        for cmd, func_class in command_map.items():
            command = cmd.replace(';', ' in user_query')
            if eval(command):
                if not func_class(user_query).primary():
                    return
                else:
                    try:
                        speak(func_class(user_query).primary())
                    except EricUtils.UserQueryError as err:
                        repeat()
                        listen()
                return

        justwaitasec()
        discuss(user_query, r, audio)
    except sr.RequestError as e:
        print("Could not request results from Whisper API")


def main_listen(recogniser, audio):
    try:
        speech: str = recogniser.recognize_google(audio)
        print("main heard", speech)
        if speech.lower().replace(',', '') == "hey eric":
            listen()
    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


main_r = sr.Recognizer()
m = sr.Microphone()
with m as source:
    main_r.adjust_for_ambient_noise(source)

stop_main_listening = main_r.listen_in_background(m, main_listen, 2)

previous_song = None
while True:
    try:
        results = sp.current_playback()
    except Exception as e:
        print(e)

    if not not results and results['is_playing']:
        current_song = EricCommands.GetPlayingSong(None).primary()

        if current_song != previous_song:
            speak(f"Now playing: {current_song}")
            previous_song = current_song

    time.sleep(2)
