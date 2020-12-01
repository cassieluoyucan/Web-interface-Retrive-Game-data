from flask import render_template, flash, abort, request, jsonify, redirect, url_for
from . import app, db
from .forms import SearchForm
from datetime import datetime, date
import base64
import json
import binascii
from dataclasses import dataclass
import pandas as pd


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


record_ref = db.collection('steam')
static_ref = db.collection('static')


def get_all_data() -> pd.DataFrame:
    df = pd.DataFrame(data=[], columns=[
        "appid", "name", "release_date", "english", "developer", "publisher", "platforms", "required_age", "categories",
        "genres", "steamspy_tags", "achievements", "positive_ratings", "negative_ratings", "average_playtime",
        "median_playtime", "owners", "price", 'q'
    ])
    for doc in db.collection("steam").stream():
        df = df.append(doc.to_dict(), ignore_index=True)
    return df


def filter_data_frame(data_frame: pd.DataFrame, string) -> pd.DataFrame:
    string = string.lower()
    data_frame = data_frame.copy()
    data_frame['tag'] = data_frame.q.apply(lambda x: 'true' if x.count(string) > 1 else 'false')
    return data_frame[data_frame.tag == 'true'].drop(['tag', 'q'], axis=1)


@app.route('/firebase', methods=['get', 'post'])
def firebase():
    if request.args.get('q'):
        tag = True
    else:
        tag = False
    query_dict = parse_q(request)

    form = SearchForm()
    form.category.choices = get_categories_choices()
    form.genre.choices = get_genres_choices()

    if request.method == 'GET':
        form.category.data = query_dict['category_ls']
        form.genre.data = query_dict['genre_ls']
        form.date_from.data = query_dict['date_from']
        form.date_to.data = query_dict['date_to']
        form.price_from.data = query_dict['price_from']
        form.price_to.data = query_dict['price_to']
    else:
        if form.validate_on_submit():
            category_ls = form.category.data
            genre_ls = form.genre.data
            date_from = form.date_from.data
            date_to = form.date_to.data
            price_from = form.price_from.data
            price_to = form.price_to.data
            q = build_q(
                data={'category_ls': category_ls, 'genre_ls': genre_ls, 'date_from': date_from, 'date_to': date_to,
                    'price_from': price_from, 'price_to': price_to, })
            return redirect(f'{url_for("firebase")}?q={q}')

    print(query_dict)
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

    if genre_ls:
        results = [r for r in results if set(r.genres) & set(genre_ls)]

    if isinstance(price_from, (float, int)):
        results = [r for r in results if r.price >= price_from]
    if isinstance(price_to, (float, int)):
        results = [r for r in results if r.price <= price_to]

    plot_data = [
        ['product', 'Average Playtime', 'Median Playtime']
    ]

    total_num = len(results)
    results = results[:20]
    display_num = len(results)

    for r in results:
        plot_data.append([
            r.name, r.average_playtime, r.median_playtime
        ])

    # plot_data = [['product', 'Average Playtime', 'Median Playtime'], ['Half-Life 2', 691, 402], ['Earth 2160', 405, 414], ['Half-Life 2: Episode One', 281, 184], ['Disciples II: Rise of the Elves ', 0, 0], ["Disciples II: Gallean's Return", 9, 12], ['X2: The Threat', 732, 732], ['X3: Reunion', 831, 1232], ['Sub Command', 0, 0], ["Garry's Mod", 12422, 1875], ['Commandos: Behind Enemy Lines', 63, 70], ['Commandos: Beyond the Call of Duty', 12, 14], ['Commandos 2: Men of Courage', 201, 302], ['Commandos 3: Destination Berlin', 14, 20], ['Joint Task Force', 0, 0], ['Rogue Trooper', 0, 0], ['Full Spectrum Warrior', 124, 244], ['Full Spectrum Warrior: Ten Hammers', 1, 1], ['QUAKE', 167, 189], ['QUAKE II', 291, 349], ['HeXen II', 10, 10]]
    print(total_num, display_num, tag)
    return render_template(
        'firebase.html', title='Firebase Steam Site',
        form=form,
        results=results, plot_data=plot_data,
        total_num=total_num,
        display_num=display_num,
        tag=tag,
    )


@app.route('/categories')
def get_categories():
    """
    Get Categories
    :return {
        "kind": "categories",
        "values": [
    "Captions available",
    "Co-op",
    "Commentary available",
    "Cross-Platform Multiplayer",
    "Full controller support",
    "In-App Purchases",
    "Includes Source SDK",
    "Includes level editor",
    "Local Co-op",
    "Local Multi-Player",
    "MMO",
    "Mods",
    "Mods (require HL2)",
    "Multi-player",
    "Online Co-op",
    "Online Multi-Player",
    "Partial Controller Support",
    "Shared/Split Screen",
    "Single-player",
    "Stats",
    "Steam Achievements",
    "Steam Cloud",
    "Steam Leaderboards",
    "Steam Trading Cards",
    "Steam Workshop",
    "SteamVR Collectibles",
    "VR Support",
    "Valve Anti-Cheat enabled"
        ]
    }

    """
    doc = static_ref.document('categories').get()
    if not doc.exists:
        abort(404)
    return jsonify(doc.to_dict())


@app.route('/genres')
def get_genres():
    """
    Get Genres
    :return {
  "kind": "genres",
  "values": [
  'Action',
  'Adventure',
  'Animation & Modeling',
   'Casual', 'Early Access',
   'Free to Play',
   'Gore',
    'Indie',
    'Massively Multiplayer', 'Nudity', 'RPG', 'Racing', 'Simulation', 'Sports',
    'Strategy', 'Video Production', 'Violent']
}
    """
    doc = static_ref.document('genres').get()
    if not doc.exists:
        abort(404)
    return jsonify(doc.to_dict())


def get_genres_choices():
    # doc = static_ref.document('genres').get()
    # values = doc.to_dict()['values']
    values = ['Action', 'Adventure', 'Animation & Modeling', 'Casual', 'Early Access', 'Free to Play', 'Gore', 'Indie', 'Massively Multiplayer', 'Nudity', 'RPG', 'Racing', 'Simulation', 'Sports', 'Strategy', 'Video Production', 'Violent']
    return [(i, i) for i in values]


def get_categories_choices():
    # doc = static_ref.document('categories').get()
    # values = doc.to_dict()['values']
    values = ["Captions available", "Co-op", "Commentary available", "Cross-Platform Multiplayer",
              "Full controller support", "In-App Purchases", "Includes Source SDK", "Includes level editor",
              "Local Co-op", "Local Multi-Player", "MMO", "Mods", "Mods (require HL2)", "Multi-player", "Online Co-op",
              "Online Multi-Player", "Partial Controller Support", "Shared/Split Screen", "Single-player", "Stats",
              "Steam Achievements", "Steam Cloud", "Steam Leaderboards", "Steam Trading Cards", "Steam Workshop",
              "SteamVR Collectibles", "VR Support", "Valve Anti-Cheat enabled"
                ]

    return [(i, i) for i in values]


def parse_q(request):
    query_dict = {
        'category_ls': [],
        'genre_ls': [],
        'date_from': None,
        'date_to': None,
        'price_from': 0,
        'price_to': 9999999,
    }
    q = request.args.get('q')
    if q:
        try:
            q = base64.urlsafe_b64decode(bytes(q, encoding='utf-8'))
            q = q.decode('utf-8')
        except (binascii.Error, UnicodeDecodeError):
            q = None
    if q:
        try:
            data = json.loads(q)
        except json.JSONDecodeError:
            data = {}
        category_ls = data.get('category_ls')
        if isinstance(category_ls, list) and all([isinstance(i, str) for i in category_ls]):
            query_dict['category_ls'] = category_ls

        genre_ls = data.get('genre_ls')
        if isinstance(genre_ls, list) and all([isinstance(i, str) for i in genre_ls]):
            query_dict['genre_ls'] = genre_ls

        date_from = data.get('date_from')
        if isinstance(date_from, str):
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d')
                query_dict['date_from'] = date_from
            except ValueError:
                pass

        date_to = data.get('date_to')
        if isinstance(date_to, str):
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d')
                query_dict['date_to'] = date_to
            except ValueError:
                pass

        price_from = data.get('price_from')
        if isinstance(price_from, (float, int)):
            query_dict['price_from'] = price_from

        price_to = data.get('price_to')
        if isinstance(price_to, (float, int)):
            query_dict['price_to'] = price_to

    return query_dict


def build_q(data: dict):
    """"""
    data = data.copy()
    data['date_from'] = str(data['date_from'])
    data['date_to'] = str(data['date_to'])
    return base64.urlsafe_b64encode(json.dumps(data).encode('utf8')).decode('utf8')

    

@app.route('/')
def index():
    """home"""
    return render_template('index.html', title='Hello Firebase')

