# -*- coding: utf-8 -*-

from pathlib import Path


class Config(object):
    UPLOAD_FOLDER = Path.cwd() / 'scripts' / 'dcards'
    ALLOWED_EXTENSIONS = 'txt'
    MAX_CONTENT_LENGTH = 1024 * 1024
    DROPZONE_MAX_FILE_SIZE = 1
    DROPZONE_UPLOAD_MULTIPLE = True
    DROPZONE_ALLOWED_FILE_CUSTOM = True
    DROPZONE_ALLOWED_FILE_TYPE = '.txt'
    #DROPZONE_REDIRECT_VIEW = 'results'
    DROPZONE_DEFAULT_MESSAGE = 'Drop files here to upload111'

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True
    SEND_FILE_MAX_AGE_DEFAULT = 0
