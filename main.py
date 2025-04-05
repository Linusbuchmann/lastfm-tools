import time
import requests
import pyaudio
import wave

# Function to record audio
def record_audio(filename, duration=10):
    p = pyaudio.PyAudio()
    rate = 44100
    chunk = 1024
    channels = 1
    format = pyaudio.paInt16
    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
    frames = []

    for i in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

# Function to identify song using Audd.io API
def identify_song(audio_file):
    url = "https://api.audd.io/"
    data = {"api_token": "your_api_token", "file": open(audio_file, "rb")}
    response = requests.post(url, files=data)
    result = response.json()
    return result['result']['title'], result['result']['artist']

# Main loop
while True:
    audio_file = "recorded_clip.wav"
    record_audio(audio_file)

    title, artist = identify_song(audio_file)

    with open("song_log.txt", "a") as f:
        f.write(f"Song: {title} by {artist}\n")

    time.sleep(10)