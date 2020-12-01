import os
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials, firestore, initialize_app
import pandas as pd

"""
doc
[Perform simple and compound queries in Cloud Firestore](https://firebase.google.com/docs/firestore/query-data/queries#python)

"""

base_dir = os.path.abspath(os.path.dirname(__file__))

sdk_json_file = os.path.join(base_dir, 'firebase-sdk-key.json')

cred = credentials.Certificate(sdk_json_file)
default_app = initialize_app(cred)

db = firestore.client()

query_string = 'alv'
# google.api_core.exceptions.FailedPrecondition: 400 The query requires an index
# create index as showed in error
ls = db.collection("steam")\
        .order_by("appid")\
        .where("q", "array_contains", query_string) \
        .stream()
for u in ls:
    print(f'{u.id}, {u.to_dict()["developer"]}')

