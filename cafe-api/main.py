from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

API_KEY = os.environ['API_KEY']


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    location = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(500), nullable=False)
    open = db.Column(db.String(500), nullable=False)
    close = db.Column(db.String(500), nullable=False)
    toilet = db.Column(db.Boolean, nullable=False)
    call = db.Column(db.Boolean, nullable=False)
    wifi = db.Column(db.String, nullable=False)
    power = db.Column(db.String, nullable=False)
    rating = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        #  Dictionary Comprehension
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# db.create_all()


@app.route('/')
def home():
    return render_template('index.html')


#  HTTP GET - Read Record
@app.route('/random')
def random():
    random_cafe = db.session.query(Cafe).order_by(func.random()).first()
    #  Convert the random_cafe data record to a dictionary of key-value pairs.
    return jsonify(cafe=random_cafe.to_dict())


@app.route('/all')
def all():
    cafes = db.session.query(Cafe).all()
    #  List Comprehension
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes]), 200


@app.route('/search')
def search():
    try:
        loc = request.args.get('loc')
        name = request.args.get('name').title()
        if loc:
            cafes = Cafe.query.filter_by(location=loc).all()
            if cafes:
                return jsonify(cafes=[cafe.to_dict() for cafe in cafes]), 200
            return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404
        elif name:
            name = request.args.get('name').title()
            cafe = Cafe.query.filter_by(name=name).first()
            if cafe:
                return jsonify(cafes=cafe.to_dict()), 200
            return jsonify(error={"Not Found": "Sorry, we don't have a cafe with that name."}), 404
    except AttributeError:
        return jsonify(error={"Error": "Sorry, we don't receive the correct parameter."}), 404


#  HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add():
    new_cafe = Cafe(
        name=request.form.get("name"),
        location=request.form.get("location"),
        image=request.form.get("image"),
        open=request.form.get("open"),
        close=request.form.get("close"),
        toilet=bool(request.form.get("toilet")),
        call=bool(request.form.get("call")),
        wifi=request.form.get("wifi"),
        power=request.form.get("power"),
        rating=request.form.get('rating')
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."}), 200


#  HTTP PUT/PATCH - Update Record
@app.route('/update/<int:cafe_id>', methods=['PATCH'])
def update_wifi(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if cafe:
        new_wifi = request.args.get('new_wifi')
        cafe.wifi = new_wifi
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the WiFi."}), 200
    return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."}), 404


@app.route('/update/<int:cafe_id>', methods=['PATCH'])
def update_power(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if cafe:
        new_power = request.args.get('new_power')
        cafe.power = new_power
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the power."}), 200
    return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."}), 404


@app.route('/update/<int:cafe_id>', methods=['PATCH'])
def update_rating(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if cafe:
        new_rating = request.args.get('new_rating')
        cafe.rating = new_rating
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the rating."}), 200
    return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."}), 404


#  HTTP DELETE - Delete Record
@app.route('/report-closed/<int:cafe_id>', methods=['DELETE'])
def report_closed(cafe_id):
    if request.args.get('api-key') == API_KEY:
        deleted_cafe = Cafe.query.get(cafe_id)
        if deleted_cafe:
            db.session.delete(deleted_cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."}), 404
    return jsonify(error={"Forbidden": "Sorry, that's not allowd. Make sure you have the correct api_key"}), 403


if __name__ == '__main__':
    app.run(debug=True, port=5001)
