import datetime
from flask import Flask, render_template, redirect, url_for, request, jsonify

from tools import select_audio


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')


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

# Route for sending audio paths
@app.route('/audio', methods=['POST'])
def send_audio():
    outlet, status = request.form['id'], request.form['value']
    f1, f2 = select_audio()
    return [f1, f2]


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
