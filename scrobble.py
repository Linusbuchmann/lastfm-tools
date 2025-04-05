#!/usr/bin/env python3

# Takes a track and scrobbles it
# Mandatory parameter 1: "artist - track"
# Optional parameter 2: UNIX timestamp. Default: now
# Prerequisites: mylast.py, pyLast

import datetime
import time
import requests
import pyaudio
import wave

from mylast import lastfm_network, split_artist_track

# Hardcoded values for testing
testMode = False
last_scrobbled = None  # To track the last scrobbled song and prevent duplicates

if testMode:
    print("Test mode, won't actually scrobble.")
else:
    print("Live mode, can scrobble.")

# Function to scrobble a track
def scrobble_track(artist_track, unix_timestamp):
    global last_scrobbled
    (artist, track) = split_artist_track(artist_track)

    # Prevent duplicate scrobbles
    if last_scrobbled == (artist, track):
        print(f"Skipping duplicate scrobble: {artist} - {track}")
        return

    # Validate or set default timestamp
    if unix_timestamp == 0:
        unix_timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
    print("Timestamp:\t" + str(unix_timestamp))

    # Scrobble it
    if not testMode:
        lastfm_network.scrobble(artist=artist, title=track, timestamp=unix_timestamp)
        print(f"Scrobbled: {artist} - {track} at {unix_timestamp}")
        last_scrobbled = (artist, track)

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

def identify_song(audio_file):
    url = "https://api.audd.io/"
    data = {"api_token": "ac19b9a99b8489648c5236ddea4d6309"}  # Replace with your actual API token
    try:
        with open(audio_file, "rb") as f:
            files = {"file": f}
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()  # Raise an error for HTTP issues
            result = response.json()
            if result.get('result'):
                return result['result']['title'], result['result']['artist']
            else:
                print("Audd.io API did not return a result.")
    except Exception as e:
        print(f"Error identifying song: {e}")
    return None, None

# Main loop to record, identify, and scrobble songs
while True:
    audio_file = "recorded_clip.wav"
    record_audio(audio_file)

    title, artist = identify_song(audio_file)
    if title and artist:
        print(f"Identified Song: {title} by {artist}")
        with open("song_log.txt", "a") as f:
            f.write(f"Song: {title} by {artist}\n")

        # Scrobble the identified song
        artist_track = f"{artist} - {title}"
        unix_timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
        scrobble_track(artist_track, unix_timestamp)
    else:
        print("No song identified. Please ensure the audio is clear and the API token is valid.")

    time.sleep(10)