import os
import shutil
from flask import jsonify


class Experiment(object):
    """Psylab Experiment"""
    def __init__(self):
        self.out_dir = ""
        self.sessions = {}
        self.session = {"id": session_id, "dir": os.path.join(self.out_dir, session_id)}
        self.response = jsonify(self.session)

    def read(self, data):
        self.id = data['id']
        self.dir = os.path.join(self.out_dir, data['id'])
        if self.id not in self.sessions:
            self.sessions[self.id] = {'id': self.id, 'dir': self.dir, 'trial': 0}
        self.ses = self.sessions[data['id']]

    def start(self, data):
        if data['id'] in self.sessions:
            print('Session exists! Deleting...')
            self.abort(data['id'])
        self.ses = self.sessions[data['id']]
        self.read(data)

        os.makedirs(self.session['dir'])
        output = {'type': 'start_experiment',
                  'message': 'Click here or press space to start',
                  'logo': 'static/index.svg'}
        self.response = jsonify(output)

    def abort(self, data):
        self.read(data)
        if os.path.exists(self.session['dir']):
            print('Session exists! Deleting...')
            shutil.rmtree(self.session['dir'])

    def trial(self, data):
        self.read(data)
        self.trial = self.sessions[self.id]['trial'] += 1
        # Ask gustav for audio files
        audio = [
          {
            "name" : "Gitar",
            "file": "sounds/guitar.mp3",
            "id" : 1
          },
          {
            "name" : "Clave",
            "file": "sounds/clave.wav",
            "id" : 2
          }
        ]
        output = {
                    'type': 'trial',
                    'lower_left_text': 'Trial: {}'.format(self.trial),
                    'lower_right_text': 'test',
                    'items': audio,
                    'prompt': 'Select a sound (press 1 or 2)',
                    'answer': 1,
                    'delay': 500
                  }
        self.response = output
