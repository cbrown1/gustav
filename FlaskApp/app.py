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


@app.route('/nafc')
def nfac():
    return render_template('nafc.html')


@app.route('/api', methods=['POST'])
def api():
    print(f"Received: {json.dumps(dict(request.form), indent=2)}")
    client_request = dict(request.form)
    if request.form['type'] == "style":
        # Initialize new ID?
        Exp.server_id = str(datetime.timestamp(datetime.now()))
        Exp.read({'id': Exp.server_id})
        return jsonify(read_json("static/colors.json"))
    elif request.form['type'] == "start":
        client_request['id'] = Exp.server_id
        Exp.start(client_request)
    elif request.form['type'] == "trial":
        client_request['id'] = Exp.server_id
        Exp.trial(client_request)
    elif request.form['type'] == "answer":
        client_request['id'] = Exp.server_id
        print(client_request)
        Exp.trial(client_request)
    elif request.form['type'] == "stop":
        client_request['id'] = Exp.server_id
        Exp.stop(client_request)
    elif request.form['type'] == "abort":
        client_request['id'] = Exp.server_id
        Exp.abort(client_request)
    elif request.form['type'] == "info":
        client_request['id'] = Exp.server_id
        Exp.info(client_request)
    Exp.dump(data=request.form, prefix='c')
    print(f"Sending: {json.dumps(Exp.response, indent=2)}")
    Exp.dump(prefix='s')
    return jsonify(Exp.response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
