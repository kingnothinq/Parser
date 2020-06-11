# -*- coding: utf-8 -*-

import logging

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_dropzone import Dropzone
from werkzeug.utils import secure_filename

from scripts.dc_handler import analyze
from scripts.shifts import duty


app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
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
    data = request.files.to_dict()
    logger.warning(f'--------------------NEW REQUEST--------------------')
    logger.info(f'POST request received from {request.remote_addr}')
    logger.debug(f'POST request User-Agent: {request.headers["User-Agent"]}')
    logger.info(f'POST contains: {list(data.keys())}')
    for name, file in data.items():
        data[name] = {}
        data[name]['filename'] = secure_filename(file.filename)
        logger.info(f'Send "{name}" ({data[name]["filename"]}) to parser')
        report = analyze(name, file, dc_source=['jira', 'DESK-00000'])
        data[name]['model'] = report[0]
        data[name]['family'] = report[1]
        data[name]['subfamily'] = report[2]
        data[name]['serial_number'] = report[3]
        data[name]['firmware'] = report[4]
        data[name]['report'] = report[5]
    logger.info(f'Send reply (JSON) to {request.remote_addr}')
    return jsonify(data)


@app.route('/schedule', methods=['GET'])
def schedule():
    schedule = duty()
    return render_template('schedule.html', date=schedule[0], person=schedule[1])


@app.errorhandler(413)
def request_entity_too_large(error):
    logger.info(f'POST request received from {request.remote_addr}')
    logger.error(f'HTTP 413 File is too large')
    return 'File is too large. It must be less than 1 MB.', 413


# Create a custom logger
logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)

# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler('parser.log')
console_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)

# Create formatter and add it to handlers
form = '%(asctime)s - %(levelname)s - %(pathname)s - %(message)s'
formatter = logging.Formatter(fmt=form, datefmt='%d-%b-%y %H:%M:%S')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)






