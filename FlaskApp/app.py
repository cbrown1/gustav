import datetime
from flask import Flask, render_template, redirect, url_for, request, jsonify

from tools import select_audio
from experiment import Experiment


app = Flask(__name__)
Exp = Experiment()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/nafc')
def nfac():
    return render_template('nafc.html')


@app.route('/postmethod', methods=['POST'])
def get_post():
    pid, pvalue = request.form['id'], request.form['value']
    f1, f2 = select_audio()
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M")
    print('Time: %s | f1: %s | f2: %s' % (time, f1, f2))
    return jsonify([f1, f2])


@app.route('/api', methods=['POST'])
def api():
    if request.form['type'] == "start":
        Exp.start(request.form)
    elif request.form['type'] == "trial":
        Exp.trial(request.form)
    elif request.form['type'] == "stop":
        Exp.stop(request.form)
    elif request.form['type'] == "abort":
        Exp.abort(request.form)
    return Exp.response


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
