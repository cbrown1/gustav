import os
import json
import time
import random
import requests
from datetime import datetime

import scipy
import numpy as np

import psylab
# import medussa

def select_audio(frequency1=1200, frequency2=2000):
    # audio_files = os.listdir("static/audio")
    # file1 = audio_files[random.randint(0, len(audio_files) - 1)]
    # file2 = audio_files[random.randint(0, len(audio_files) - 1)]
    ts = str(datetime.timestamp(datetime.now()))
    ts = ts.replace(".", "_")

    file1 = f"static/audio/{ts}_1.wav"
    file2 = f"static/audio/{ts}_2.wav"
    generate_audio(filename=file1, frequency=frequency1)
    generate_audio(filename=file2, frequency=frequency2)
    # time.sleep(1)
    return file1, file2
    # return "static/audio/{}".format(file1), "static/audio/{}".format(file2)


def post_request(url="http://0.0.0.0:5000/audio", data={"audio": "static/audio/cat.wav"}):
    post = requests.post(url, data)
    if post.status_code == 200:
        response = True
        response = json.loads(post.text)
    else:
        print(post.text)
        response = False
    return response


def read_json(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return data


def generate_audio(filename="audio.wav", frequency=1000, duration=1000, level=30, max_level=80, fs=44100):
    sig = psylab.signal.tone(float(frequency), fs, duration)
    sig = psylab.signal.ramps(sig, fs)
    sig = psylab.signal.atten(sig, max_level - level)
    scipy.io.wavfile.write(filename, fs, sig)


def cleanup():
    for f in os.listdir('static/audio'):
        if f[0].isnumeric():
            os.remove(os.path.join('static/audio', f))


if __name__ == "__main__":
    cleanup()
