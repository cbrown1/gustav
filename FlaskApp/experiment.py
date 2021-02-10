import os
import json
import shutil

from tools import select_audio


class Experiment(object):
    """Psylab Experiment"""
    def __init__(self, session_id="0"):
        self.root = 'static'
        self.out_dir = 'exp'
        self.dir = os.path.join(self.root, self.out_dir, session_id)
        self.sessions = {session_id: {"id": session_id, "dir": self.dir}}
        self.ses = self.sessions[session_id]
        self.response = self.ses

    def read(self, data):
        self.id = data['id']
        self.dir = os.path.join(self.root, self.out_dir, data['id'])
        if 'trial' in data:
            self.num_trial = int(data['trial'])
        else:
            self.num_trial = 0
        if self.id not in self.sessions:
            self.sessions[self.id] = {'id': self.id, 'dir': self.dir, 'trial': self.num_trial}
        else:
            self.sessions[self.id] = {**data, **self.sessions[self.id]}
        self.ses = self.sessions[data['id']]

    def start(self, data):
        self.read(data)
        # self.abort()
        # os.makedirs(self.dir)
        jsonf = os.path.join(self.dir, 'api.json')
        output = {'type': 'start_experiment',
                  'message': 'Click here or press space to start',
                  'logo': 'static/index.svg',
                  'json': os.path.join(self.out_dir, self.id, 'api.json')}
        self.dump(output, jsonf)
        self.response = output

    def abort(self):
        if os.path.exists(self.dir):
            print('Session exists! Deleting...')
            shutil.rmtree(self.dir)

    def trial(self, data):
        self.read(data)
        self.num_trial += 1
        # self.num_trial = self.sessions[self.id]['trial'] + 1
        # Ask gustav for audio files
        files = select_audio()
        names = [i.split('/')[-1].split('.')[0] for i in files]
        audio = []
        for i, (f, n) in enumerate(zip(files, names)):
            audio.append({'name': n, 'file': f, 'id': i})
        # audio = [
        #   {
        #     "name" : "Gitar",
        #     "file": "static/audio/guitar.wav",
        #     "id" : 1
        #   },
        #   {
        #     "name" : "Clave",
        #     "file": "static/audio/clave.wav",
        #     "id" : 2
        #   }
        # ]
        jsonf = os.path.join(self.dir, 'api.json')
        output = {
                    'type': 'trial',
                    'lower_left_text': 'Trial: {}'.format(self.num_trial),
                    'lower_right_text': 'test',
                    'items': audio,
                    'prompt': 'Select a sound (press 1 or 2)',
                    'answer': 1,
                    'delay': 500,
                    'json': os.path.join(self.out_dir, self.id, 'api.json')
                  }
        self.dump(output, jsonf)
        self.response = output

    def stop(self, data):
        self.read(data)
        jsonf = os.path.join(self.dir, 'api.json')
        output = {
          "type": "stopExperiment",
          "message" : "Experiment completed, thank you for participating",
          'json': os.path.join(self.out_dir, self.id, 'api.json')
        }
        self.dump(output, jsonf)
        self.response = output

    def dump(self, data, filename):
        """Dump data to json file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
