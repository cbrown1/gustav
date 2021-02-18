import os
import json
import shutil

from tools import select_audio


class Experiment(object):
    """Psylab Experiment"""
    def __init__(self, session_id="0"):
        self.root = 'static'
        self.out_dir = 'exp'
        self.sessions = {}

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
        self.abort(data, keep_dir=False)
        os.makedirs(self.dir)
        output = {'type': 'start',
                  'message': "Click '<code>Start</code>' or press '<code>Space</code>' to start the experiment.",
                  'logo': 'static/index.svg'}
        self.response = output
        print('start' + '-' * 30 + f'\n{self}')

    def abort(self, data, keep_dir=True):
        self.read(data)
        if os.path.exists(self.dir):
            print('Session exists! Deleting...')
            if len(os.listdir(self.dir)) > 1:
                for f in os.listdir(self.dir):
                    os.remove(os.path.join(self.dir, f))
            if not keep_dir:
                shutil.rmtree(self.dir)
        output = {
            'type': 'abort',
            'message': "Experiment has been aborted."
        }
        self.response = output
        self.num_trial = 0
        print('abort' + '-' * 30 + f'\n{self}')

    def trial(self, data):
        self.read(data)
        self.num_trial += 1
        # Ask gustav for audio files
        # For testing stop the experiment after 3 trials
        if self.num_trial >= 5:
            self.stop(data)
        else:
            files = select_audio()
            names = [i.split('/')[-1].split('.')[0] for i in files]
            audio = []
            for i, (f, n) in enumerate(zip(files, names), start=1):
                audio.append({'name': i, 'file': f, 'id': i})
            output = {
                        'type': 'trial',
                        'lower_left_text': 'Trial: {}'.format(self.num_trial),
                        'lower_right_text': f'Session ID: {self.id}',
                        'upper_left_text': 'Psylab NAFC Experiment',
                        'items': audio,
                        'prompt1': 'Press space to listen',
                        'prompt2': 'Select a sound (press 1 or 2)',
                        'answer': 1,
                        'delay': 500,
                        'next_delay': 2000,
                      }
            self.response = output
            print('trial' + '-' * 30 + f'\n{self}')

    def stop(self, data):
        self.read(data)
        output = {
          "type": "stop",
          "message" : "Experiment completed, thank you for participating"
        }
        self.response = output
        print('stop' + '-' * 30 + f'\n{self}')

    def info(self, data):
        self.read(data)
        output = {
          "type": "info",
          "message": "NAFC Experiment"
        }
        self.response = output
        print('info' + '-' * 30 + f'\n{self}')

    def dump(self, data=None, filename=None):
        """Dump data to json file"""
        if data is None:
            data = self.response
        if filename is None:
            filename = os.path.join(self.dir, f"{self.response['type']}_{self.num_trial}.json")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f'dump -> {filename}')
