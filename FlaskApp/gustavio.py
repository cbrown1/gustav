import os
import json
import time
import shutil
import subprocess
from datetime import datetime

import psutil
import pkgutil

from tools import read_json

from gustav.utils import exp
from gustav.user_scripts.html import gustav_exp__adaptive_quietthresholds


class GustavIO(object):
    """Gustav IO"""
    def __init__(self, server_pid, subject_id="1", port=5050, experiment='', local=False):
        """
        Initialize gustav input/output.
        """
        self.server_pid = server_pid
        self.root = 'static'
        self.out_dir = 'exp'
        self.sessions = {}
        self.num_trial = 0
        self.port = port
        self.max_ports = 10
        self.base_port = 5050
        self.id = subject_id
        # Read experiments as submodule
        # Check the experiment script if the experiment is available (exp.ready = True)
        self.experiment = 'gustav_exp__adaptive_quietthresholds'
        self.script = f'{self.experiment}.py'
        file_dir = os.path.dirname(os.path.abspath(__file__))
        script_dir = os.path.join(file_dir, '..', 'gustav', 'user_scripts', 'html')
        self.script_dir = os.path.abspath(script_dir)
        self.process = None
        self.dir = None
        self.str_time = None
        self.running_file = os.path.join(file_dir, 'running.json')
        if self.port == self.base_port and os.path.exists(self.running_file):
            os.remove('running.json')
        self.update_running()
        if local:
            self.url = 'http://0.0.0.0'
        else:
            self.url = 'http://74.109.252.140'


    def __repr__(self):
        if self.process is None:
            pid = None
        else:
            pid = self.process.pid
        return f"Gustav IO\n  Server PID: {self.server_pid} Port: {self.port}\n  ID: {self.id}\n  Gustav PID: {pid}\n  Directory: {self.dir}"

    def setup(self, subject_id, port):
        """
        Set up subject id and port.
        Create subject directory (deletes if it exists)
        """
        self.id = subject_id
        self.port = port
        self.port_dir = os.path.join(self.root, self.out_dir, str(self.port))
        os.makedirs(self.port_dir, exist_ok=True)
        self.subject_dir = os.path.join(self.port_dir, str(self.id))
        self.dir = os.path.join(self.port_dir, str(self.id))
        if os.path.exists(self.dir):
            self.abort(data, keep_dir=False)
        os.makedirs(self.dir)

    def read(self, data):
        self.id = data['id']
        self.dir = os.path.join(self.port_dir, str(self.id))
        if self.id not in self.sessions:
            self.sessions[self.id] = {'id': self.id, 'dir': self.dir, 'trial': self.num_trial}
        else:
            self.sessions[self.id] = {**data, **self.sessions[self.id]}
        self.ses = self.sessions[self.id]
        print(self)

    def run(self, sleep=3):
        cmd = ['python', '-u', self.script, '-s', f'{self.id}:{self.port}']
        # redirect output to a file in subject dir
        self.process_out = os.path.join(self.dir, 'out.txt')
        self.process = subprocess.Popen(cmd, cwd=self.script_dir, stdout=open(self.process_out, 'w'))
        self.process_start_time = datetime.now()
        self.str_time = self.process_start_time.strftime("%m/%d/%Y, %H:%M:%S")
        print(f'Running script: {self.script} | PID: {self.process.pid}')
        new_run = {'pid': self.process.pid,
                   'port': self.port,
                   'script': self.script,
                   'time': self.str_time,
                   'sid': self.id}
        self.update_running(append=new_run)
        time.sleep(sleep)

    def update_running(self, append=None, remove=None):
        if not os.path.exists(self.running_file):
            self.running = []
            with open(self.running_file, 'w') as f:
                json.dump({'ports': {self.port: self.server_pid}, 'subjects': []}, f)
        else:
            with open(self.running_file, 'r') as f:
                self.running = json.load(f)
            running = {'ports': {}, 'subjects': []}
            for p in self.running['ports']:
                running['ports'][int(p)] = int(self.running['ports'][p])
            for s in self.running['subjects']:
                running['subjects'].append(s)
            self.running = running
            self.running['ports'][self.port] = self.server_pid
            if append is not None:
                self.running['subjects'].append(append)
            if remove is not None:
                self.running['subjects'] = [r for r in self.running['subjects'] if r['pid'] != remove['pid']]
            with open(self.running_file, 'w') as f:
                json.dump(self.running, f)

    def is_running(self):
        if self.process is None:
            return False
        else:
            poll = self.process.poll()
            if poll is None:
                return True
            else:
                return False

    def kill(self):
        """
        Kill Gustav process
        """
        pid = str(self.process.pid)
        print(f'Killing gustav script pid: {pid}')
        self.process.kill()
        out = subprocess.run(f'kill {pid}', shell=True, capture_output=True, text=True)
        self.update_running(remove={'pid': pid})
        if out.returncode != 0:
            print(f'Process {pid} does not exist : ', out.stderr)
        else:
            print(f'Process {pid} killed')

    def send_request(self, data):
        """
        Send request to gustav.
        """
        print(f"send_request: {data}")
        self.read(data)
        self.request = data
        self.response = data
        if data['type'] == 'answer':
            request_type = 'trial'
            self.num_trial += 1
        else:
            request_type = data['type']
        if not hasattr(self, 'id'):
            print('WARNING: No subject id available, skipping')
        else:
            self.expected_response = os.path.join(self.dir, f"g{self.num_trial}_{request_type}.json")
            data['response_file'] = self.expected_response
            self.dump(data=data, prefix='c')

    def get_response(self, sleep=0.1, max_timeout=20, max_load_attempts=3):
        """
        Get response from gustav.
        """
        print(f'Waiting for response: {self.expected_response}')
        timeout = 0
        load_attempt = 0
        while not os.path.exists(self.expected_response) and timeout <= max_timeout:
            time.sleep(sleep)
            timeout += sleep
            # print(f"waiting {timeout} < {max_timeout}")
        if timeout <= max_timeout:
            print(f"Received reponse")
            for i in range(max_load_attempts):
                try:
                    self.response = self.load(self.expected_response)
                except:
                    load_attempt += 1
                    print(f'Could not load file, attempt: {load_attempt}/{max_load_attempts}')
                    time.sleep(sleep)
            if load_attempt >= max_load_attempts:
                print(f'Reached max load attempts: {max_load_attempts}, ignoring out')
                self.response = {}
        else:
            print(f'Max timeout ({max_timeout} s) reached, no response!')
            self.response = {}
        return self.response

    def initialize(self, data):
        self.read(data)
        self.num_trial = 0
        self.response = read_json("static/style.json")
        self.style = read_json("static/style.json")
        print('initialize' + '-' * 30 + f'\n{self}')

    def login(self, data):
        print(f'Login: {data}')
        if data['username'] == 'gustav' and data['password'] == 'test':
            return 'true'
        else:
            return 'false'

    def get_experiments(self):
        # Get running processes
        procs = self.get_processes()
        # Kill if no activity

        # Get running servers
        self.update_running()
        exp_ports = [int(p) for p in self.running['ports'] if int(p) != self.base_port]
        print(f'Exp ports: {exp_ports}')
        port_pids = self.running['ports'].values()
        print(f'Port pids: {port_pids}')
        print(f'procs: {procs}')
        running_ports = [pt for pt, pd in self.running['ports'].items() if pd in port_pids]
        print(f'Running ports: {running_ports} Total processes: {len(procs)}')
        # Check ifthe gustav process are running
        used_ports = [s['port'] for s in self.running['subjects'] if int(s['pid']) in procs]
        print(f'Used ports: {used_ports}')
        avail_ports = [p for p in exp_ports if p not in used_ports and p in running_ports]
        print(f'Avail ports: {avail_ports}')
        if len(avail_ports) == 0:
            url, ready = '', False
            print('No ports available!')
        else:
            port = min(avail_ports)
            print(f'{len(avail_ports)} ports available, selected {port}')
            url = f'{self.url}:{port}/nafc'
            ready = True
        # url = 'http://74.109.252.140:5051/nafc'
        # url = '/nafc'
        # Get available experiments
        exps = []
        gustav_exp__adaptive_quietthresholds.setup(exp)
        # html_exps = list(pkgutil.iter_modules(html.__path__)))
        # Load all available experiments
        # exp.experiment = __import__(exp.experimentBase)
        # exp.experiment.setup( exp )
        e = {'title': exp.title, 'description': exp.note, 'url': url, 'ready': ready}
        exps.append(e)
        # exps = self.load('experiments.json')
        print('get_experiments' + '-' * 30 + f'\n{exps}')
        return {'experiments': exps}

    def get_setup(self):
        # exps = self.load('setup.json')
        sbj = []
        for r in self.running['subjects']:
            sbj.append({'id': r['sid'], 'port': r['port'], 'time': r['time']})
        # sbj = {'id': self.id, 'port': self.port, 'time': self.str_time}
        exp = {'title': 'n-AFC', 'description': f'{len(sbj)} subject(s)', 'subjects': sbj}
        data = {'experiments': [exp],
                'max_ports': self.max_ports,
                'base_port': self.base_port,
                }
        print('get_setup' + '-' * 30 + f'\n{self}')
        return data

    def dump(self, data=None, filename=None, prefix='', suffix=''):
        """Dump data to json file"""
        if data is None:
            data = self.response
        if filename is None:
            filename = os.path.join(self.dir, f"{prefix}{self.num_trial}_{data['type']}{suffix}.json")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f'dump -> {filename}')

    def load(self, filename):
        """Load json file"""
        with open(filename, "r") as f:
            data = json.load(f)
        return data

    def get_processes(self, name='python'):
        procs = []
        for proc in psutil.process_iter():
            try:
                # Get process name & pid from process object.
                processName = proc.name()
                processID = proc.pid
                processTime = proc.create_time()
                if name in processName:
                    print(f'{processName} {processID} {processTime}')
                    procs.append(processID)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return procs
