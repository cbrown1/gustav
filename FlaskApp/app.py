import json
import datetime
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
    if request.form['type'] == "style":
        # Initialize new ID?
        return jsonify(read_json("static/colors.json"))
    elif request.form['type'] == "start":
        Exp.start(request.form)
    elif request.form['type'] == "trial":
        Exp.trial(request.form)
    elif request.form['type'] == "answer":
        print(dict(request.form))
        Exp.trial(request.form)
    elif request.form['type'] == "stop":
        Exp.stop(request.form)
    elif request.form['type'] == "abort":
        Exp.abort(request.form)
    elif request.form['type'] == "info":
        Exp.info(request.form)
    print(f"Sending: {json.dumps(Exp.response, indent=2)}")
    # Exp.dump()
    return jsonify(Exp.response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
