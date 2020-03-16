#!/usr/bin/python
# -*- coding: utf-8 -*-

from pathlib import Path


class Config(object):
    UPLOAD_FOLDER = Path.cwd() / 'scripts' / 'dcards'
    ALLOWED_EXTENSIONS = 'txt'
    MAX_CONTENT_LENGTH = 1024 * 1024


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True