import os
import json
import shutil

from tools import select_audio


class Experiment(object):
    """Psylab Experiment"""
    def __init__(self, session_id="0"):
        self.root = 'static'
        self.out_dir = 'exp'
        self.dir = os.path.join(self.root, self.out_dir, str(session_id))
        self.sessions = {session_id: {"id": session_id, "dir": self.dir}}
        self.ses = self.sessions[session_id]
        self.response = self.ses
        self.num_trial = 0

    def __repr__(self):
        return f"Psylab experiment\n  ID: {self.id}\n  Trial: {self.num_trial}\n  Directory: {self.dir}\n  Sessions: {len(self.sessions)}"

    def read(self, data):
        self.id = data['id']
        self.dir = os.path.join(self.root, self.out_dir, str(data['id']))
        if self.id not in self.sessions:
            self.sessions[self.id] = {'id': self.id, 'dir': self.dir, 'trial': self.num_trial}
        else:
            self.sessions[self.id] = {**data, **self.sessions[self.id]}
        self.ses = self.sessions[self.id]
        print(self)

    def start(self, data):
        self.num_trial = 0
        self.read(data)
        self.abort(data)
        os.makedirs(self.dir)
        output = {'type': 'start',
                  'message': "Click '<code>Start</code>' or press '<code>Space</code>' to start the experiment.",
                  'logo': 'static/index.svg'}
        self.response = output

    def abort(self, data):
        self.read(data)
        if os.path.exists(self.dir):
            print('Session exists! Deleting...')
            shutil.rmtree(self.dir)
        output = {
            'type': 'abort',
            'message': "Experiment has been aborted."
        }
        self.response = output
        self.num_trial = 0

    def trial(self, data):
        self.read(data)
        self.num_trial += 1
        # Ask gustav for audio files
        # For testing stop the experiment after 3 trials
        if self.num_trial >= 3:
            self.stop(data)
        else:
            files = select_audio()
            names = [i.split('/')[-1].split('.')[0] for i in files]
            audio = []
            for i, (f, n) in enumerate(zip(files, names)):
                audio.append({'name': n, 'file': f, 'id': i})
            output = {
                        'type': 'trial',
                        'lower_left_text': 'Trial: {}'.format(self.num_trial),
                        'lower_right_text': 'lower_right_text',
                        'upper_left_text': 'upper_left_text',
                        'items': audio,
                        'prompt1': 'Press space to listen',
                        'prompt2': 'Select a sound (press 1 or 2)',
                        'answer': 1,
                        'delay': 500
                      }
            self.response = output

    def stop(self, data):
        self.read(data)
        output = {
          "type": "stop",
          "message" : "Experiment completed, thank you for participating"
        }
        self.response = output

    def dump(self, data, filename):
        """Dump data to json file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
