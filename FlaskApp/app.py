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
    return render_template('nafc.html')

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
        GIO.setup(subject_id, port)
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
    parser.add_argument('--port', '-p', default=5050, type=int, metavar='', nargs=1,
                        help="Port number (default: 5050)")
    parser.add_argument('--local', '-l', action='store_true', default=False,
                        help="Run locally at 0.0.0.0 (default: false)")
    parser.add_argument('--debug', '-d', action='store_true', default=True,
                        help="Debug mode (default: true)")
    args = parser.parse_args()

    GIO = GustavIO(getpid(), port=args.port, local=args.local)
    print(GIO)
    app.run(host='0.0.0.0', debug=args.debug, port=args.port)
