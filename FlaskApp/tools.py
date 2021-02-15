import os
import json
import random
import requests


def select_audio():
    audio_files = os.listdir("static/audio")
    file1 = audio_files[random.randint(0, len(audio_files) - 1)]
    file2 = audio_files[random.randint(0, len(audio_files) - 1)]
    return "static/audio/{}".format(file1), "static/audio/{}".format(file2)


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
