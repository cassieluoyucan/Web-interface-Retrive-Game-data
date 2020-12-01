from flask_wtf import FlaskForm
from wtforms import (SelectMultipleField, FloatField, DateField, SubmitField)
from wtforms.validators import DataRequired, Length, NumberRange


class SearchForm(FlaskForm):
    category = SelectMultipleField(label='Categories')
    genre = SelectMultipleField(label='Genres')
    price_from = FloatField(label='Price From')
    price_to = FloatField(label='Price To')
    date_from = DateField(label='Release Date From')
    date_to = DateField(label='Release Date To')
    submit = SubmitField('Search')
