import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import csv

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Import data from csv file into database
f= open("books.csv")
reader = csv.reader(f)

# read and insert data
count = 0
print(f"{count}")
for isbn, title, author, year in reader:
  # skip the first row
  if count == 0:
    count += 1
    continue
  # insert the next rows
  db.execute("INSERT INTO books(isbn, title, author, year) VALUES(:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year})
db.commit()