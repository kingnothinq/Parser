#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, make_response, render_template, request
from werkzeug.utils import secure_filename

from scripts.runit import analyze


app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/jira', methods=['POST'])
def parser():
    result = []
    for file in request.files.values():
        filename = secure_filename(file.filename)
        result.append(analyze(file, filename))
        result.append('\n' * 2)
    response = make_response('\n'.join(result), 200)
    response.headers['Content-Type'] = 'text/plain'
    return response


@app.errorhandler(413)
def request_entity_too_large(error):
    return 'File is too large. It must be less than 1 MB.', 413


if __name__ == '__main__':
    app.run(host='0.0.0.0')
