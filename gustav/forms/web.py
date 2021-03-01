import os
import json
import time
import shutil
import requests
from datetime import datetime


class Interface():
    def __init__(self, alternatives=2, prompt='Choose an alternative'):
        self.prompt = prompt
        self.alternatives = alternatives
        style_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'style.json')
        with open(style_file) as f:
            self.style = json.load(f)
        self.dir = '../../FlaskApp/static/exp'
        self.root = '../../FlaskApp/static'
        self.out_dir = 'exp'
        self.sessions = {}
        self.io = {}

    def __repr__(self):
        return f"Psylab experiment\n  ID: {self.id}\n  Trial: {self.num_trial}\n  Directory: {self.dir}\n  Sessions: {len(self.sessions)}"

    def get_resp(self, sleep=0.1, max_timeout=300):
        try:
            waiting = True
            timeout_start = time.time()
            out_dir = os.path.join(self.dir, self.id)
            print(f'Get resp waiting: {out_dir}')
            while waiting:
                outs = os.listdir(out_dir)
                for out in outs:
                    if out not in self.io:
                        print(f'Found new out: {out}')
                        filename = os.path.join(out_dir, out)
                        self.io[out] = self.load(filename)
                        waiting = False
                        ret = self.io[out]
            return ret
        except:
            self.destroy()
            raise Exception('Error getting input')

    def get_resp_pre_exp(self, sleep=0.1, max_timeout=300):
        new_subject_found = False
        now = datetime.now()
        timeout = 0
        while not new_subject_found:
            subjects = os.listdir(self.dir)
            for sbj in subjects:
                try:
                    sbj_date = datetime.fromtimestamp(float(sbj))
                    if sbj_date > now:
                        print(f'New subject found: {sbj}')
                        self.id = sbj
                        new_subject_found = True
                except Exception as e:
                    print(f"Cannot parse subject id: {sbj}\n{e}")
            time.sleep(sleep)
            timeout += sleep
            if timeout > max_timeout:
                self.id = False
        return {'id': self.id}

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

    def present_trial(self):
        pass

    def trial(self, data):
        self.read(data)
        self.num_trial += 1
        # Ask gustav for audio files
        # For testing stop the experiment after 3 trials
        if self.num_trial >= 5:
            self.stop(data)
        else:
            if 'answer' in data:
                if data['answer'] == "1":
                    self.freq1 += 200
                    self.freq2 += 200
                else:
                    self.freq1 -= 200
                    self.freq2 -= 200
            files = select_audio(self.freq1, self.freq2)
            print("Frequency 1: {self.freq1} | 2: {self.freq2}")
            names = [i.split('/')[-1].split('.')[0] for i in files]
            audio = []
            for i, (f, n) in enumerate(zip(files, names), start=1):
                audio.append({'name': i, 'file': f, 'id': i})
            output = {
                        'type': 'trial',
                        'lower_left_text': 'Trial: {}'.format(self.num_trial),
                        'lower_right_text': f'Session ID: {self.id}',
                        'upper_left_text': 'Psylab n-AFC Experiment | Quiet Thresholds',
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

    def pre_exp(self, data):
        self.read(data)
        output = {
          "type": "info",
          "message": self.title_c_str
        }
        self.response = output
        print('info' + '-' * 30 + f'\n{self}')

    def load(self, filename):
        """Load data from json file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        return data

    def dump(self, data=None, filename=None):
        """Dump data to json file"""
        if data is None:
            data = self.response
        if filename is None:
            filename = os.path.join(self.dir, f"{self.response['type']}_{self.num_trial}.json")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f'dump -> {filename}')

    def dump_style(self, style=None):
        """Dump data to json file"""
        if style is None:
            style = self.style
        filename = os.path.join(self.root, "style.json")
        with open(filename, 'w') as f:
            json.dump(style, f, indent=2)
        print(f'dump -> {filename}')

    def destroy(self):
        # Stop experiment
        pass

    def update(self, filename="test.json"):
        """
        Update the interface
        """
        self.out = {}
        with open(filename, 'w') as f:
            json.dump(self.out, f)

    # Use instead of update_Status_Right etc
    def update_text(self):
        pass

    def show_Notify_Left(self, show=None):
        """Show the left notify text

            If show==None, toggle.
            Otherwise show should be a bool.
        """
        if show is not None:
            self.notify_l_show = show
        else:
            self.notify_l_show = not self.notify_l_show

    def update_Notify_Right(self, s, show=None):
        """Update the notify text to the left of the face.

            show is a bool specifying whether to show the text,
            set to None to leave this param unchanged [default].
            show can also be set with show_Notify_Left.
        """
        self.notify_r_str = s
        if show is not None:
            self.notify_r_show = show

    def show_Notify_Right(self, show=None):
        """Show the right notify text

            If show==None, toggle.
            Otherwise show should be a bool.
        """

        if show is not None:
            self.notify_r_show = show
        else:
            self.notify_r_show = not self.notify_r_show

    def update_Notify_Right(self, s, show=None):
        """Update the notify text to the left of the face.

            show is a bool specifying whether to show the text,
            set to None to leave this param unchanged [default].
            show can also be set with show_Notify_Left.
        """
        self.notify_r_str = s
        if show is not None:
            self.notify_r_show = show

    def show_Buttons(self, show=None):
        """Show the position bar

           If show==None, toggle show.
           Otherwise show should be a bool.
        """
        if show is not None:
            self.buttons_show = show
        else:
            self.buttons_show = not self.buttons_show

    def show_Prompt(self, show=None):
        """Show the prompt

           If show==None, toggle show.
           Otherwise show should be a bool.
        """
        if show is not None:
            self.prompt_show = show
        else:
            self.prompt_show = not self.prompt_show

    def update_Prompt(self, s, show=True):
        """Update the text of the prompt

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.prompt = s
        self.prompt_show = show

    def show_Buttons(self, show=None):
        """Show the position bar

           If show==None, toggle show and force a redraw. Otherwise
            show should be a bool.

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        if show is not None:
            self.buttons_show = show
        else:
            self.buttons_show = not self.buttons_show

    def update_Status_Left(self, s, redraw=False):
        """Update the text on the left side of the status bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.status_l_str = s
        if redraw:
            self.redraw()

    def update_Status_Right(self, s, redraw=False):
        """Update the text on the right side of the status bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.status_r_str = s

    def update_Status_Center(self, s, redraw=False):
        """Update the text in the center of the status bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.status_c_str = s
        if redraw:
            self.redraw()

    def update_Title_Left(self, s, redraw=False):
        """Update the text on the left side of the title bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.title_l_str = s
        if redraw:
            self.redraw()

    def update_Title_Right(self, s, redraw=False):
        """Update the text on the right side of the title bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.title_r_str = s
        if redraw:
            self.redraw()

    def update_Title_Center(self, s, redraw=False):
        """Update the text in the center of the title bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.title_c_str = s
        if redraw:
            self.redraw()
