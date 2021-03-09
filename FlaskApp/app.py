import sys
import json
import time
import subprocess
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, jsonify

from gustavio import GustavIO


app = Flask(__name__)
GIO = GustavIO()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api', methods=['POST'])
def api():
    print(f'Received: {json.dumps(dict(request.form), indent=2)}')
    # Forward request to gustav
    client_request = dict(request.form)
    # Loading home page
    if client_request['type'] == "style":
        if GIO.is_running():
            url = '<a href=http://run.psylab.org/>To participate click here</a>'
            output = {
                'type': 'ignore',
                'message': f'Experiment in progress...<br>{url}'
            }
            return jsonify(output)
        else:
            # Initialize new ID
            subject_id = str(datetime.timestamp(datetime.now()))
            # Set up experiment
            GIO.setup(subject_id, port, gustav_script)
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
    if len(sys.argv) > 1:
        port = 5050 + int(sys.argv[1])
    else:
        port = 5050
    gustav_script = 'gustav_exp__adaptive_quietthresholds.py'
    app.run(host='0.0.0.0', debug=True, port=port)
