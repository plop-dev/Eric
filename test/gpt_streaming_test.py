from openai import OpenAI
from dotenv import load_dotenv
import os
from charactr_api import CharactrAPISDK, Credentials
import io
import soundfile
import sounddevice
import time
import threading
import asyncio

start_time = time.time()
end_time: float

speak_queue = []

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)


def speak_queue_thread_main():
    global speak_queue
    
    while True:
        if len(speak_queue) > 0:
            for _ in range(0, len(speak_queue)):
                print('speak:', speak_queue[0])
                speak(speak_queue[0])
                print('finished speak:', speak_queue[0])
                speak_queue.pop(0)
        
        time.sleep(0.1)

def speak(text):
    global end_time
    speech_response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=text,
        speed=1.0,
    )
    print('received response, timer stopped')
    end_time = time.time()
    
    buffer = io.BytesIO()
    for chunk in speech_response.iter_bytes(chunk_size=2048):
        buffer.write(chunk)
    buffer.seek(0)
    
    print('reading audio')
    with soundfile.SoundFile(buffer, 'r') as sound_file:
        data = sound_file.read(dtype='int16')
        print('playing audio')
        sounddevice.play(data, sound_file.samplerate)
        sounddevice.wait()


# speak_queue_thread = threading.Thread(target=asyncio.run, args=(speak_queue_thread_main(),), daemon=True)
speak_queue_thread = threading.Thread(target=speak_queue_thread_main, daemon=False)
speak_queue_thread.start()

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a ChatBot."},
        {"role": "user", "content": "Describe London's location and history in 1 sentence."},
    ],
    stream=True
)
# response = response.choices[0].message.content

token_counter = 0
token_string = ''

for chunk in response:
    if chunk.choices[0].delta.content is not None:
        text_response = chunk.choices[0].delta.content
        
        if token_counter >= 5 and text_response.strip().isalpha():
            # print(token_string)
            speak_queue.append(token_string)
            
            token_counter = 0
            token_string = ''
    
        token_counter += 1
        token_string += text_response
        
speak_queue.append(token_string)
# print(token_string)

# time_taken = end_time - start_time
# print(f'Time taken by speak() to generate a response: {time_taken} seconds')
