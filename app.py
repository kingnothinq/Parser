#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, request
from pathlib import Path
from werkzeug.utils import secure_filename
from scripts.runit import analyze

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = Path.cwd() / 'scripts' / 'dcards'
app.config['ALLOWED_EXTENSIONS'] = 'txt'


def allowed_format(filename):
    return 'txt' in filename.rsplit('.', 1)[1]


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.get_data()
        return analyze(data)


@app.route('/parser', methods=['POST'])
def parser():
    file = request.files['file']
    filename = secure_filename(file.filename)
    if file and allowed_format(filename):
        return analyze(file)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)