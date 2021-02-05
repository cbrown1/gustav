import os
import random


def select_audio():
    audio_files = os.listdir("static/audio")
    file1 = audio_files[random.randint(0, len(audio_files) - 1)]
    file2 = audio_files[random.randint(0, len(audio_files) - 1)]
    return "static/audio/{}".format(file1), "static/audio/{}".format(file2)
