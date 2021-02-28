import json
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
        # Initialize new ID and return styling information
        Exp.server_id = str(datetime.timestamp(datetime.now()))
        Exp.initialize({'id': Exp.server_id})
        client_request['id'] = Exp.server_id
    else:
        if not hasattr(Exp, 'id'):
            return jsonify({})
    if hasattr(Exp, 'server_id'):
        client_request['id'] = Exp.server_id
    Exp.send_request(client_request)
    # Get gustav response
    response = Exp.get_response()
    print(f"Sending: {json.dumps(response, indent=2)}")
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)