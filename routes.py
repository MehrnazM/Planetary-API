from app import db, app, mail, jwt
from flask import Blueprint, jsonify, request
import db_models
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Message

rts = Blueprint('routes', __name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/super_simple')
def super_simple():
    return jsonify(message='Hello from the Planetary API')


@app.route('/not_found')
def not_found():
    return jsonify(message='That resource was not found'), 404


@app.route('/parameters')
def parameters():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age < 18:
        return jsonify(message="Sorry " + name + ", you are not old enough"), 401
    return jsonify(message='Welcome ' + name + '!'), 200


@app.route('/url_variables/<string:name>/<int:age>')
def url_variables(name: str, age: int):
    if age < 18:
        return jsonify(message="Sorry " + name + ", you are not old enough"), 401
    return jsonify(message='Welcome ' + name + '!'), 200


@app.route('/planets', methods=['GET'])
def planets():
    planets_list = db_models.Planet.query.all()
    result = db_models.planets_schema.dump(planets_list)
    return jsonify(result)


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test = db_models.User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='That email already exists'), 409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = db_models.User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message='User created successfully'), 201


@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']
    test = db_models.User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message='login succeeded', access_token=access_token)
    else:
        return jsonify(message='login failed'), 401


@app.route('/retrieve_password/<string:email>', methods=['GET'])
def retrieve_password(email: str):
    user = db_models.User.query.filter_by(email=email).first()
    if user:
        msg = Message("your planetary API password is: " + user.password,
                      sender="admin@planetary-api.com",
                      recipients=[email])
        mail.send(msg)
        return jsonify(message="Password sent to " + email)
    else:
        return jsonify(message="That email doesn't exist"), 401


@app.route('/planet_details/<int:planet_id>', methods=['GET'])
def planet_details(planet_id: int):
    planet = db_models.Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        result = db_models.planet_schema.dump(planet)
        return jsonify(result)
    else:
        return jsonify(message='That planet does not exist'), 404


@app.route('/planets', methods=['POST'])
@jwt_required()
def add_planet():
    planet_name = request.json['planet_name']
    test = db_models.Planet.query.filter_by(planet_name=planet_name).first()
    if test:
        return jsonify(message="This planet already exists"), 409
    else:
        planet = request.json
        new_planet = db_models.Planet(planet_name=planet['planet_name'],
                                      planet_type=planet['planet_type'],
                                      home_star=planet['home_star'],
                                      mass=planet['mass'],
                                      radius=planet['radius'],
                                      distance=planet['distance'])
        db.session.add(new_planet)
        db.session.commit()

    return jsonify(message='you added a planet'), 201


@app.route('/planets/<int:planet_id>', methods=['PUT'])
@jwt_required()
def update_planet(planet_id:int):
    planet = db_models.Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        planet.planet_name = request.form['planet_name']
        planet.planet_type = request.form['planet_type']
        planet.home_star = request.form['home_star']
        planet.mass = float(request.form['mass'])
        planet.radius = float(request.form['radius'])
        planet.distance = float(request.form['distance'])
        db.session.commit()
        return jsonify(message="you updated a planet"), 202
    else:
        return jsonify(message="that planet does not exist"), 404


@app.route('/planets/<int:planet_id>', methods=['DELETE'])
@jwt_required()
def delete_planet(planet_id:int):
    planet = db_models.Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        db.session.delete(planet)
        db.session.commit()
        return jsonify(message='you deleted a planet'), 202
    else:
        return jsonify(message='the planet was not found'), 404

