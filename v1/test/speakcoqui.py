import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
# print(TTS().list_models().list_tts_models())

# Init TTS
tts = TTS("tts_models/en/vctk/vits").to(device)

# Run TTS
# ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
# Text to speech list of amplitude values as output
tts.tts_to_file(text="hey plop, how are you today? I'm a demo for coqui ai tts. we'll see how well this goes", file_path="output.wav")
