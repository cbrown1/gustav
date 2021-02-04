import datetime
from flask import Flask, render_template, redirect, url_for, request


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
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M")
    print('Time: %s | ID: %s | Value: %s' % (time, pid, pvalue))
    return pid


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
