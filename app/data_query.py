import os
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials, firestore, initialize_app
import pandas as pd
from datetime import datetime
from dataclasses import dataclass

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


def get_all_data() -> pd.DataFrame:
    df = pd.DataFrame(data=[], columns=[
        "appid", "name", "release_date", "english", "developer", "publisher", "platforms", "required_age", "categories",
        "genres", "steamspy_tags", "achievements", "positive_ratings", "negative_ratings", "average_playtime",
        "median_playtime", "owners", "price", 'q'
    ])
    for doc in db.collection("steam").stream():
        df = df.append(doc.to_dict(), ignore_index=True)
    return df


def filter_data_frame(data_frame: pd.DataFrame, string):
    string = string.lower()
    data_frame = data_frame.copy()
    data_frame['tag'] = data_frame.q.apply(lambda x: 'true' if x.count(string) > 1 else 'false')
    return data_frame[data_frame.tag == 'true'].drop(['tag', 'q'], axis=1)


@dataclass
class Record:
    appid: int = None
    name: str = None
    release_date: datetime = None
    english: int = None
    developer: str = None
    publisher: str = None
    platforms: list = None
    required_age: int = None
    categories: list = None
    genres: list = None
    steamspy_tags: list = None
    achievements: str = None
    positive_ratings: int = None
    negative_ratings: int = None
    average_playtime: int = None
    median_playtime: int = None
    owners: str = None
    price: float = None
    # q: str = None
    

if __name__ == '__main__':
    # df = get_all_data()
    # print(filter_data_frame(df, '2000'))

    # doc = db.collection('static').document('categories').get()
    # if doc.exists:
    #     print(doc.to_dict())
    # else:
    #     print('not exist')
    #
    # for page in db.collection('static').list_documents():
    #     print(page.id, page.get().to_dict())
    record_ref = db.collection('steam')
    query_dict = {
        'category_ls': ['Captions available', 'Co-op'],
        'genre_ls': ['Captions available', 'Co-op'],
        'date_from': datetime(1952, 8, 21, 0, 0),
        'date_to': datetime(2020, 9, 23, 0, 0),
        'price_from': 0.0, 'price_to': 888.0
    }
    category_ls = query_dict['category_ls']
    genre_ls = query_dict['genre_ls']
    date_from = query_dict['date_from']
    date_to = query_dict['date_to']
    price_from = query_dict['price_from']
    price_to = query_dict['price_to']

    query_ref = record_ref
    if category_ls:
        query_ref = query_ref.where('categories', 'array_contains_any', category_ls)

    if date_from:
        query_ref = query_ref.where('release_date', '>=', date_from)
    if date_to:
        query_ref = query_ref.where('release_date', '<=', date_to)

    results = [Record(**doc.to_dict()) for doc in query_ref.stream()]

    # if genre_ls:
    #     results = [r for r in results if set(r.genres) & set(genre_ls)]

    if isinstance(price_from, (float, int)):
        results = [r for r in results if r.price >= price_from]
    if isinstance(price_to, (float, int)):
        results = [r for r in results if r.price <= price_to]

    plot_data = [
        ['product', 'Average Playtime', 'Median Playtime']
    ]
    for r in results[:20]:
        print(r)
        plot_data.append([
            r.name, r.average_playtime, r.median_playtime
        ])

    print(plot_data)




