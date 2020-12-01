# coding: utf-8

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base Configure"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious_secret_key')  # secret key to encrypt session
    DEBUG = False  # debug status
    CSRF_ENABLED = True  # enable csrf protection
    BOOTSTRAP_USE_MINIFIED = True  # use minified css and js files
    BOOTSTRAP_SERVE_LOCAL = True  # we serve bootstrap and jquery and popover locally
    WTF_CSRF_ENABLED = True  # web form protection enabled
    WTF_CSRF_SECRET_KEY = SECRET_KEY  # key as secret key
    FIREBASE_SDK_CREDENTIAL_FILE = os.path.join(basedir, 'firebase-sdk-key.json')


class DevelopmentConfig(Config):
    """Configure for Dev"""
    DEBUG = True  # debug enabled for dev


class TestingConfig(Config):
    """Configure for Testing"""
    DEBUG = True  # debug enable for testing
    TESTING = True  # tell we're testing.


class ProductionConfig(Config):
    """Configure for Production"""
    DEBUG = False  # disable debug mode while in production


config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig,

    default='development'
)

