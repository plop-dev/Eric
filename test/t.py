import sounddevice as sd
import numpy as np

duration = 1

while True:
    recording = sd.rec(int(duration * 44100), samplerate=44100, channels=2)
    sd.wait()

    rms = np.sqrt(np.mean(recording ** 2))
    if rms > 0.001:
        print("Sound detected!")
    else:
        print('nothing detected')
