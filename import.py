import os
from flask import Flask, render_template, request
import csv
# Import table definitions.
from models import *

app = Flask(__name__)

# Tell Flask what SQLAlchemy database to use.
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Link the Flask app with the database (no Flask app is actually being run yet).
db.init_app(app)

def main():
  # Create tables based on each table definition in `models`
  db.create_all()

  # import data in zips.csv file to table created
  f = open("zips.csv")
  reader = csv.reader(f)
  for zipcode, city, state, lat, lon, pop in reader[1:]:
      #
      location = Locations(zipcode=zipcode, city=city, state=state, latitude=lat, longitude=lon, population=pop)
      db.session.add(location)
      db.session.commit()

if __name__ == "__main__":
  # Allows for command line interaction with Flask application
  with app.app_context():
      main()