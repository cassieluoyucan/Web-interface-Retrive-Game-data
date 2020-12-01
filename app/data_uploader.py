# coding: utf-8
import os
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials, firestore, initialize_app
import pandas as pd
from datetime import datetime

"""
Description: a script to upload csv file to firebase
Version: v.0.0.1
"""

base_dir = os.path.abspath(os.path.dirname(__file__))

sdk_json_file = os.path.join(base_dir, 'firebase-sdk-key.json')  # please goto https://console.firebase.google.com/
# create a project, then create database
# video tutorial may help "Python Firebase Cloud Firestore Example" - https://www.youtube.com/watch?v=Wlr8jMehNQ0

cred = credentials.Certificate(sdk_json_file)
default_app = initialize_app(cred)

db = firestore.client()

collection = db.collection('steam')

df = pd.read_csv('steam.csv')

print(f'columns: {list(df.columns)}')
print(f'{df.shape[0]} rows, has {len(df.appid.unique())} unique app ids')  # a proof to use appid as the document id

size = 500  # limit data size for dev
# size = df.shape[0]  # upload all data

category_set = set()
genre_set = set()
steam_spy_tag_set = set()
platform_set = set()

for row in df.iloc[:size, :].to_dict('records'):
    ref = collection.document(str(row['appid']))

    # # create query string cause firebase'query is quite weak
    # row['q'] = '{appid},{name},{release_date},{english},{developer},{publisher},' \
    #            '{platforms},{required_age},{categories},{genres},{steamspy_tags},' \
    #            '{achievements},{positive_ratings},{negative_ratings},' \
    #            '{average_playtime},{median_playtime},{owners},{price}'.format(**row).lower()

    row['categories'] = row['categories'].split(';')
    row['genres'] = row['genres'].split(';')
    row['release_date'] = datetime.strptime(row['release_date'], '%Y-%m-%d')
    row['steamspy_tags'] = row['steamspy_tags'].split(';')
    row['platforms'] = row['platforms'].split(';')

    category_set.update(row['categories'])
    genre_set.update(row['genres'])
    steam_spy_tag_set.update(row['steamspy_tags'])
    platform_set.update(row['platforms'])

    ref.set(row)
    print(f'uploaded: {row["appid"]}, {row["name"]}')

category_ls = sorted(category_set)
genre_ls = sorted(genre_set)
platform_ls = sorted(platform_set)
steam_spy_tag_ls = sorted(steam_spy_tag_set)

collection = db.collection('static')

collection.document('categories').set({
    'kind': 'categories',
    'values': category_ls
    })
print(f'Uploaded categories: {category_ls}')

collection.document('genres').set({
    'kind': 'genres',
    'values': genre_ls
    })
print(f'Uploaded genres: {genre_ls}')


collection.document('platforms').set({
    'kind': 'platforms',
    'values': platform_ls
    })
print(f'Uploaded platforms: {platform_ls}')


collection.document('steamspy_tags').set({
    'kind': 'steamspy_tags',
    'values': steam_spy_tag_ls
    })
print(f'Uploaded steamspy_tags: {steam_spy_tag_ls}')