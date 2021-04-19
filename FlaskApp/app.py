import sys
import json
import time
import argparse
import subprocess
from os import getpid
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, jsonify

from gustavio import GustavIO


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/setup')
def setup():
    return render_template('setup.html')

@app.route('/nafc')
def nafc():
    for e in GIO.read_experiments():
        if e['template'] == 'nafc':
            print(f'exp found: {e}')
            GIO.setup_script('{}.py'.format(e['name']))
    return render_template('nafc.html')

@app.route('/speech')
def speech():
    return render_template('speech.html')

@app.route('/login', methods=['POST'])
def login():
    client_request = dict(request.form)
    response = GIO.login(client_request)
    return jsonify(response)

@app.route('/change_ports', methods=['POST'])
def change_ports():
    # Change max ports and base port here
    client_request = dict(request.form)
    GIO.max_ports = client_request['max_ports']
    GIO.base_port = client_request['base_port']
    print(f'Changed ports | base: {GIO.base_port} max: {GIO.max_ports}')
    return jsonify({})

@app.route('/speechapi', methods=['POST'])
def speechapi():
    client_request = dict(request.form)
    if client_request['type'] == 'setup':
        response = GIO.load('setup.json')
    elif client_request['type'] == 'trial':
        response = GIO.load('calib.json')
    elif client_request['type'] == 'answer':
        print(f'Answer: {client_request}')
        response = GIO.load('trial.json')
    else:
        print(f'Unknown req: {client_request}')
        response = {}
    # response = GIO.get_experiments()
    return jsonify(response)

@app.route('/homeapi', methods=['POST'])
def homeapi():
    client_request = dict(request.form)
    response = GIO.get_experiments()
    return jsonify(response)

@app.route('/setupapi', methods=['POST'])
def setupapi():
    client_request = dict(request.form)
    response = GIO.get_setup()
    return jsonify(response)

@app.route('/killpid', methods=['POST'])
def killpid():
    client_request = dict(request.form)
    procs = GIO.get_processes()
    GIO.update_running()
    if client_request['pid'] == 'all':
        # Kill all gustav
        gustav_pids = [s['pid'] for s in GIO.running['subjects']]
        gustav_ports = {s['pid']: s['port'] for s in GIO.running['subjects']}
        pids = [p for p in procs if p in gustav_pids]
        response = f'Attempted killing {len(pids)} PIDs'
        for pid in pids:
            success = GIO.kill(pid)
            response += f'\nPort: {gustav_ports[pid]} PID: {pid} : {success}'
    elif client_request['pid'] == 'port':
        # Only kill current port's process
        if GIO.process is None:
            response = 'Gustav experiment has not been started'
        else:
            response = f'Killing gustav at port {GIO.port} pid: {GIO.process.pid}'
            success = GIO.kill()
            response += f'\nSuccess: {success}'
    elif client_request['pid'] == 'cleanup':
        procs = GIO.get_processes(status=['running'])
        gustav_pids = [s['pid'] for s in GIO.running['subjects']]
        server_pids = list(GIO.running['ports'].values())
        pids = [p for p in procs if p not in gustav_pids and p not in server_pids]
        response = f'Found {len(pids)} processes to cleanup'
        for pid in pids:
            success = GIO.kill(pid)
            response += f'\nPID: {pid} : {success}'
    return jsonify(response)


@app.route('/api', methods=['POST'])
def api():
    print(f'Received: {json.dumps(dict(request.form), indent=2)}')
    # Forward request to gustav
    client_request = dict(request.form)
    # Loading home page
    if client_request['type'] == "style":
        # If a gustav process is already running check how long it has been running for
        # If longer than 2 hours kill and restart
        # If not display an experiment in progress message
        if GIO.is_running():
            td = (datetime.now() - GIO.process_start_time).seconds
            print(f'Gustav {GIO.process.pid} has been running for {td} s')
            if td > 120 * 60:
                GIO.kill()
            else:
                msg = f'Experiment in progress...<br>Time elapsed: {int(td / 60)} mins and {td % 60} seconds<br>'
                msg += '<a href=http://run.psylab.org/>To participate click here</a>'
                output = {'type': 'ignore', 'message': msg}
                return jsonify(output)
        # Initialize new ID
        subject_id = str(datetime.timestamp(datetime.now()))
        # Set up experiment
        GIO.setup(subject_id, args.port)
        # Start gustav script
        GIO.run(sleep=2)
        # Initialize
        GIO.initialize({'id': GIO.id})
        client_request['id'] = GIO.id
        return jsonify(GIO.style)
    client_request['id'] = GIO.id
    GIO.send_request(client_request)
    # Get gustav response
    response = GIO.get_response()
    if 'type' in response and response['type'] in ['stop', 'abort']:
        print('Killing gustav')
        GIO.kill()
    # response = GIO.style
    print(f'Sending: {json.dumps(response, indent=2)}')
    return jsonify(response)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""
    =================================================
    GUSTAV server application........................
    =================================================
        """,
        epilog="""
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    # Optional arguments
    parser.add_argument('--port', '-p', default=5050, type=int, metavar='',
                        help="Port number (default: 5050)")
    parser.add_argument('--local', '-l', action='store_true', default=False,
                        help="Run locally at 0.0.0.0 (default: false)")
    parser.add_argument('--debug', '-d', action='store_true', default=True,
                        help="Debug mode (default: true)")
    args = parser.parse_args()
    print(args.port, type(args.port))
    GIO = GustavIO(getpid(), port=args.port, local=args.local)
    print(GIO)
    app.run(host='0.0.0.0', debug=args.debug, port=args.port)
