import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from helpers import *

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return error("must submit username")

        # Ensure password was sumbitted
        elif not request.form.get("password"):
            return error("must submit password")

        # Query for username and password

        # Ensure username exists and password is correct
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect to login page
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    # User reached route via POST
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return error("must submit username")

        # Ensure password was sumbitted
        elif not request.form.get("password"):
            return error("must submit password")

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return error("must confirm password")

        # Ensure confirmation and password match
        elif not request.form.get("confirmation") == request.form.get("password"):
            return error("password not matching")

    else:
        return render_template("register.html")