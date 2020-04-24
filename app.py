#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_dropzone import Dropzone
from werkzeug.utils import secure_filename

from scripts.runit import analyze
from scripts.shifts import duty


app = Flask(__name__)
app.config.from_object('config.ProductionConfig')
dropzone = Dropzone(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('upload'), code=302)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')

@app.route('/jira', methods=['POST'])
def parser():
    requests = request.files.to_dict()
    for name, file in requests.items():
        requests[name] = {}
        report = analyze(name, file)
        requests[name]['filename'] = secure_filename(file.filename)
        requests[name]['model'] = report[0]
        requests[name]['family'] = report[1]
        requests[name]['subfamily'] = report[2]
        requests[name]['serial_number'] = report[3]
        requests[name]['firmware'] = report[4]
        requests[name]['report'] = report[5]
    return jsonify(requests)

@app.route('/schedule', methods=['GET'])
def schedule():
    schedule = duty()
    return render_template('schedule.html', date=schedule[0], person=schedule[1])

@app.errorhandler(413)
def request_entity_too_large(error):
    return 'File is too large. It must be less than 1 MB.', 413


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
