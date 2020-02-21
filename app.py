#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from pathlib import Path

if __name__ == "__main__":
    web_service = Flask(__name__, template_folder=Path.cwd(), static_folder=Path.cwd())


    @web_service.route('/')
    def index():
        return report


    report = 'Hui sosi guboi tryasi'

    web_service.run(host='0.0.0.0')
