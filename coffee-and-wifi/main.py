import requests
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, URL
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
Bootstrap(app)
CAFE_API_URL = 'http://localhost:5001'


class AddForm(FlaskForm):
    name = StringField('Cafe Name', validators=[DataRequired()])
    location = StringField('Cafe Location on Google Maps (URL)', validators=[DataRequired(), URL()])
    image = StringField('Cafe Image on Google Maps (URL)', validators=[DataRequired(), URL()])
    open = StringField('Open Time e.g. 8:00AM', validators=[DataRequired()])
    close = StringField('Close Time e.g. 5:30PM', validators=[DataRequired()])
    wifi = SelectField('WiFi Availability', choices=['🈚️', '❤️', '❤️❤️', '❤️❤️❤️'],
                       validators=[DataRequired()])
    power = SelectField('Power Socket Availability', choices=['🈚️', '🔌', '🔌🔌', '🔌🔌🔌'],
                        validators=[DataRequired()])
    rating = SelectField('Coffee Rating', choices=['🈚️', '⭐️', '⭐️⭐️', '⭐️⭐️⭐️'], validators=[DataRequired()])
    toilet = BooleanField('Has Toilet?')
    call = BooleanField('Can Take Call?')
    submit = SubmitField('Submit')


class DeleteForm(FlaskForm):
    name = StringField('Cafe Name', validators=[DataRequired()])
    key = StringField('API Key🔑', validators=[DataRequired()])
    submit = SubmitField('Submit')


# all Flask routes below
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    form = AddForm()
    if form.validate_on_submit():
        if not form.toilet.data:
            form.toilet.data = None
        if not form.call.data:
            form.call.data = None
        params = {'name': form.name.data,
                  'location': form.location.data,
                  'image': form.image.data,
                  'open': form.open.data,
                  'close': form.close.data,
                  'wifi': form.wifi.data,
                  'power': form.power.data,
                  'rating': form.rating.data,
                  'toilet': form.toilet.data,
                  'call': form.call.data
                  }
        requests.post(f'{CAFE_API_URL}/add', data=params)
        return redirect(url_for('add_cafe'))
    return render_template('add.html', form=form)


@app.route('/delete', methods=['GET', 'POST'])
def delete_cafe():
    form = DeleteForm()
    if form.validate_on_submit():
        params = {'name': form.name.data}
        response = requests.get(f'{CAFE_API_URL}/search', params=params)
        id_to_delete = response.json()['cafes']['id']
        params = {'api-key': form.key.data}
        requests.delete(url=f'{CAFE_API_URL}/report-closed/{id_to_delete}', params=params)
        return redirect(url_for('delete_cafe'))
    return render_template('delete.html', form=form)


@app.route('/cafes')
def all_cafes():
    response = requests.get(url=f'{CAFE_API_URL}/all')
    cafes = response.json()['cafes']
    return render_template('cafes.html', cafes=cafes)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
