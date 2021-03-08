import sys
import json
import time
import subprocess
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, jsonify

from tools import select_audio, read_json
from experiment import Experiment


app = Flask(__name__)
Exp = Experiment()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api', methods=['POST'])
def api():
    print(f"Received: {json.dumps(dict(request.form), indent=2)}")
    # Forward request to gustav
    client_request = dict(request.form)
    if client_request['type'] == "style":
        if Exp.is_running():
            output = {
                'type': 'ignore',
                'message': 'Experiment in progress'
            }
            return jsonify(output)
        else:
            # Initialize new ID
            subject_id = str(datetime.timestamp(datetime.now()))
            # Set up experiment
            Exp.setup(subject_id, port)
            # Start gustav script
            Exp.run(sleep=1)
            # Initialize
            Exp.initialize({'id': Exp.id})
            client_request['id'] = Exp.id
            return jsonify(Exp.style)
    client_request['id'] = Exp.id
    Exp.send_request(client_request)
    # Get gustav response
    response = Exp.get_response()
    # response = Exp.style
    print(f"Sending: {json.dumps(response, indent=2)}")
    return jsonify(response)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = 5050 + int(sys.argv[1])
    else:
        port = 5050
    app.run(host='0.0.0.0', debug=True, port=port)
