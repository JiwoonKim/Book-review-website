from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

class Locations(db.Model):
    __tablename__ = "locations"
    zipcode = db.Column(db.String, primary_key=True)
    city = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    latitude = db.Column(db.Integer, nullable=False)
    longitude = db.Column(db.Integer, nullable=False)
    population = db.Column(db.Integer, nullable=False)