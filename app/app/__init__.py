# coding: utf-8
# import packages
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from firebase_admin import credentials, firestore, initialize_app
import os

from config import config_by_name  # import configs


app = Flask(__name__)  # init a flask app
app.config.from_object(config_by_name[os.getenv('FLASK_ENV') or config_by_name['default']])  # apply configure
cred = credentials.Certificate(app.config['FIREBASE_SDK_CREDENTIAL_FILE'])
firebase_app = initialize_app(cred)
db = firestore.client()

bootstrap = Bootstrap(app)  # init bootstrap

CSRFProtect(app)  # enable csrf protection for our app

from . import routes
