import os
import json
import time
import shutil
import requests
from datetime import datetime

import numpy as np


class Interface():
    def __init__(self, alternatives=2, prompt='Choose an alternative', appdir=""):
        self.prompt = prompt
        self.alternatives = alternatives
        self.filedir = os.path.dirname(os.path.abspath(__file__))
        style_file = os.path.join(self.filedir, 'style.json')
        with open(style_file) as f:
            self.style = json.load(f)
        self.appdir = appdir
        self.staticdir = os.path.join(self.appdir, 'static')
        self.expdir = os.path.join(self.appdir, 'static', 'exp')
        self.sessions = {}
        self.io = {}

        self.info = ''
        self.upper_left_text = ''
        self.lower_left_text = ''
        self.lower_right_text = ''

        self.checked = []

    def __repr__(self):
        return f"Gustav web interface\n  ID: {self.id}"

    def get_resp(self, resp_type=None, sleep=0.1, max_timeout=300, max_load_attempts=3):
        try:
            waiting = True
            load_attempt = 0
            timeout_start = time.time()
            out_dir = os.path.join(self.expdir, self.id)
            print(f'Get resp waiting: {out_dir}', '' if resp_type is None else f' expected type: {resp_type}')
            # checked = []
            while waiting:
                outs = os.listdir(out_dir)
                for out in outs:
                    if out.startswith('c') and out.split('.')[-1] == 'json' and out not in self.io and out not in self.checked:
                        print(f'Found new out: {out}')
                        filename = os.path.join(out_dir, out)
                        try:
                            resp = self.load(filename)
                            if resp['type'] == 'abort':
                                print('Aborting experiment')
                                self.destroy()
                                exit(1)
                            if resp_type is None:
                                print('No type selected, read type: ', resp['type'] if 'type' in resp else None)
                                waiting = False
                                self.io[out] = resp
                                ret = self.io[out]
                            else:
                                if resp['type'] == resp_type:
                                    print(f'Out correct type: {resp_type} : {out}')
                                    waiting = False
                                    self.io[out] = resp
                                    ret = self.io[out]
                                else:
                                    print(f'Out not expected: {out} is not type {resp_type}')
                                    self.checked.append(out)
                        except:
                            load_attempt += 1
                            print(f'Could not load file, attempt: {load_attempt}')
                            time.sleep(sleep)
                        if load_attempt >= max_load_attempts:
                            print('Reached max load attempts: {max_load_attempts}, ignoring out')
                            self.checked.append(out)
                            load_attempt = 0

            return ret
        except:
            self.destroy()
            raise Exception('Error getting input')

    def parse_resp(self, resp):
        if resp['type'] == 'info':
            self.info()
        elif resp['type'] == 'trial':
            self.trial()
        elif resp['type'] == 'answer':
            self.trial()
        elif resp['type'] == 'stop':
            self.stop()
        elif resp['type'] == 'abort':
            self.abort()
        elif resp['type'] == 'style':
            self.dump_style()

    def get_resp_pre_exp(self, sleep=0.1, max_timeout=300):
        new_subject_found = False
        now = datetime.now()
        timeout = 0
        checked = []
        while not new_subject_found:
            subjects = os.listdir(self.expdir)
            for sbj in subjects:
                if sbj not in checked:
                    try:
                        sbj_date = datetime.fromtimestamp(float(sbj))
                        if sbj_date > now:
                            print(f'New subject found: {sbj}')
                            self.id = sbj
                            self.subjdir = os.path.join(self.expdir, self.id)
                            new_subject_found = True
                    except Exception as e:
                        print(f"Cannot parse subject id: {sbj}\n{e}")
                        checked.append(sbj)
                else:
                    continue
            time.sleep(sleep)
            timeout += sleep
            if timeout > max_timeout:
                self.id = False
        return {'id': self.id}

    def present_trial(self, exp):
        self.lower_left_text = 'Trial: {}'.format(exp.run.trials_block)
        self.lower_right_text = f"Block {exp.run.block+1} of {exp.var.nblocks+1}"
        output = {
                    'type': 'trial',
                    'lower_left_text': self.lower_left_text,
                    'lower_right_text': self.lower_right_text,
                    'upper_left_text': self.upper_left_text,
                    'items': self.audio,
                    'prompt1': self.prompt1,
                    'prompt2': self.prompt2,
                    'answer': exp.var.dynamic['correct'],
                    'delay': exp.user.isi,
                    'next_delay': 2000,
                    'block': exp.run.block,
                    'trial': exp.run.trials_block
                  }
        last_answer = self.find_last_answer()
        print(f'Last answer: {last_answer}')
        if last_answer is not None:
            filename = os.path.join(self.appdir, last_answer['response_file'])
        else:
            filename = os.path.join(self.expdir, self.id, f"g{exp.run.trials_block}_trial.json")
        self.dump(output, filename)

    def dump_info(self, filename):
        output = {
          "type": "info",
          "message": self.info
        }
        print('info' + '-' * 30 + f'\n{output}')
        self.dump(output, filename)
        return output

    def abort(self, data, keep_dir=True):
        self.read(data)
        if os.path.exists(self.subjdir):
            print('Session exists! Deleting...')
            if len(os.listdir(self.subjdir)) > 1:
                for f in os.listdir(self.subjdir):
                    os.remove(os.path.join(self.subjdir, f))
            if not keep_dir:
                shutil.rmtree(self.subjdir)
        output = {
            'type': 'abort',
            'message': "Experiment has been aborted."
        }
        self.response = output
        self.num_trial = 0
        print('abort' + '-' * 30 + f'\n{self}')

    def find_last_answer(self):
        """
        Find last answer from client
        Includes info about what the next response should be
        """
        answers = [i for i in self.io if 'answer' in i]
        print(f'answers: {answers}')
        if len(answers) > 0:
            nanswers = [int(i.split('_')[0][1:]) for i in answers]
            last_answer = self.io[answers[np.argsort(nanswers)[-1]]]
        else:
            last_answer = None
        return last_answer


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
        # data = requests.get(filename).json()
        with open(filename, 'r') as f:
            data = json.load(f)
        return data

    def dump(self, data=None, filename=None):
        """Dump data to json file"""
        if data is None:
            data = self.response
        if filename is None:
            filename = os.path.join(self.subjdir, f"g{self.num_trial}_{self.response['type']}.json")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f'dump -> {filename}')

    def dump_style(self, style=None):
        """Dump data to json file"""
        if style is None:
            style = self.style
        filename = os.path.join(self.staticdir, "style.json")
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

    def update_Status_Left(self, s):
        """Update the text on the left side of the status bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.status_l_str = s

    def update_Status_Right(self, s):
        """Update the text on the right side of the status bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.status_r_str = s

    def update_Status_Center(self, s):
        """Update the text in the center of the status bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.status_c_str = s

    def update_Title_Left(self, s):
        """Update the text on the left side of the title bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.title_l_str = s

    def update_Title_Right(self, s):
        """Update the text on the right side of the title bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.title_r_str = s

    def update_Title_Center(self, s):
        """Update the text in the center of the title bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.title_c_str = s
