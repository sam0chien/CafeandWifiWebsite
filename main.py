from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Dictionary Comprehension
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route('/')
def home():
    return render_template('index.html')


## HTTP GET - Read Record
@app.route('/random')
def random():
    random_cafe = db.session.query(Cafe).order_by(func.random()).first()
    # Convert the random_cafe data record to a dictionary of key-value pairs.
    return jsonify(cafe=random_cafe.to_dict())


@app.route('/all')
def all():
    cafes = db.session.query(Cafe).all()
    # List Comprehension
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes]), 200


@app.route('/search')
def search():
    loc = request.args.get('loc').title()
    cafes = Cafe.query.filter_by(location=loc).all()
    if cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes]), 200
    return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


## HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        seats=request.form.get("seats"),
        has_sockets=bool(request.form.get("has_sockets")),
        has_toilet=bool(request.form.get("has_toilet")),
        has_wifi=bool(request.form.get("has_wifi")),
        can_take_calls=bool(request.form.get("can_take_calls")),
        coffee_price=request.form.get("coffee_price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."}), 200


## HTTP PUT/PATCH - Update Record
@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if cafe:
        new_price = request.args.get('new_price')
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    return jsonify(error={"Not Found": "Sorry, a cafe wtih that id was not found in the database."}), 404


## HTTP DELETE - Delete Record
@app.route('/report-closed/<int:cafe_id>', methods=['DELETE'])
def report_closed(cafe_id):
    if request.args.get('api-key') == 'TopSecretAPIKey':
        deleted_cafe = Cafe.query.get(cafe_id)
        if deleted_cafe:
            db.session.delete(deleted_cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."}), 404
    return jsonify(error={"Forbidden": "Sorry, that's not allowd. Make sure you have the correct api_key"}), 403


if __name__ == '__main__':
    app.run(debug=True)
