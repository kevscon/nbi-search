import os, json
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import Optional, DataRequired, Regexp, ValidationError

class SearchForm(FlaskForm):

    state_postal = SelectField(
        'Select State Name:',
        choices = [('-1', '--select state--')]
       )

    county_name = SelectField(
        'Select County:',
        choices = [('-1', '--select county--')]
       )

    submit = SubmitField('List County Structures')
