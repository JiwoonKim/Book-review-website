import os

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from helpers import *

import requests

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


@app.route("/", methods=["GET", "POST"])
def index():
    """ Default page for Website
        User is able to search for a specific book using the isbn, title, author's name
        The results of matching books will be displayed and is clickable for more details """

    # Ensure user is logged in first
    if session.get("user_id") is None:
        return redirect("/login")

    # User reached route via POST (submitted a form)
    if request.method == "POST":

        # Ensure book is submitted
        if not request.form.get("book"):
            return error("must sumbit info of book for search")

        # Search for book in database
        search = request.form.get("book").lower()
        book = "%" + search + "%"
        books = db.execute(
            "SELECT * FROM books WHERE (LOWER(isbn) LIKE :book) OR (LOWER(title) LIKE :book) OR (LOWER(author) LIKE :book) LIMIT 15", {"book": book}).fetchall()

        # if no matching results, show error message
        if len(books) == 0:
            return error("No matching results")

        # if matching results, show lists of books
        else:
            return render_template("results.html", search=search, books=books)

    # User reached route via GET
    else:
        return render_template("index.html")


@app.route("/api/<isbn>")
def api(isbn):
    """ API access to the Website
        User may make a GET request via this route with the ISBN number
        A JSON response of the book's details will be returned """

    # Query from books table in database
    book = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": isbn}).fetchone()

    # If the requested ISBN number doesn't exist in database, return error
    if book is None:
        return jsonify({"error": "invalid ISBN number"}), 404

    else:
        # Query for book ratings from Goodreads API
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": "lV6JRoF2Xl75SN1f9SgOmQ", "isbns": isbn})
        if res.status_code != 200:
            raise Exception("ERROR: API request unsuccessful.")
        data = res.json()
        ratings = data["books"][0]

        # create JSON response and return it
        api = jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": ratings["work_ratings_count"],
            "average_score": ratings["average_rating"]
        })
        return api


@app.route("/book/<isbn>", methods=["GET", "POST"])
def book(isbn):
    """ Page for further details of the book clicked from the search results from the / route
        User may write one review for each book and can view the reviews and rankings """

    # Ensure user is logged in first
    if session.get("user_id") is None:
        return redirect("/login")

    # Query for book data
    book = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return error("Error in retrieving data")

    # Query for book ratings from Goodreads API
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "lV6JRoF2Xl75SN1f9SgOmQ", "isbns": isbn})
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")

    data = res.json()
    ratings = data["books"][0]

    # Query for book reviews
    reviews = db.execute("SELECT username, rating, review FROM reviews JOIN users ON reviews.user_id=users.id WHERE isbn=:isbn", {
        "isbn": isbn}).fetchall()

    return render_template("book.html", book=book, ratings=ratings, reviews=reviews)


@app.route("/login", methods=["GET", "POST"])
def login():
    """ User is logged in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (submitting a form for logging in)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return error("must submit username")

        # Ensure password was sumbitted
        elif not request.form.get("password"):
            return error("must submit password")

        # Query for username and password
        username = request.form.get("username")
        password = request.form.get("password")
        user_id = db.execute("SELECT id FROM users WHERE (username=:username AND password=:password)",
                             {"username": username, "password": password}).fetchone()

        # Ensure username exists and password matches
        if user_id is None:
            return error("user does not exist or password does not match")

        # If login credentials passes, store in session
        session["user_id"] = user_id

        return redirect("/")

        # Ensure username exists and password is correct
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """ User is logged out """

    # Forget any user_id
    session.clear()

    # Redirect to login page
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """ User is able to register their own credentials
        and is logged in automatically """

    # User reached route via POST
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return error("must submit username")
        # Ensure password was sumbitted
        elif not request.form.get("password"):
            return error("must submit password")
        # Ensure confirmation was submitted
        elif not request.form.get("comfirmation"):
            return error("must confirm password")
        # Ensure confirmation and password match
        elif not request.form.get("comfirmation") == request.form.get("password"):
            return error("password not matching")

        # Register username and password into database (w/o hashing)
        username = request.form.get("username")
        password = request.form.get("password")
        db.execute("INSERT INTO users(username, password) VALUES(:username, :password)",
                   {"username": username, "password": password})
        db.commit()

        # Log in credentials automatically
        user_id = db.execute("SELECT id FROM users WHERE (username=:username AND password=:password)",
                             {"username": username, "password": password}).fetchone()
        if user_id is None:
            return error("not registered")
        session["user_id"] = user_id

        # redirect user to login page
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("register.html")


@app.route("/review", methods=["POST"])
def review():
    """ Inserts the review data given from the /book route into the database
        Redirects the user back to the /book route """

    # Ensure user is logged in first
    if session.get("user_id") is None:
        return redirect("/login")
    user_id = session.get("user_id")[0]

    # Ensure user has not already written a review
    isbn = request.form.get("isbn")
    if db.execute("SELECT * FROM reviews WHERE isbn=:isbn AND user_id=:user_id", {"isbn": isbn, "user_id": user_id}).rowcount > 0:
        return error("Already wrote a review!")

    # Ensure rating is submitted
    if not request.form.get("rating"):
        return error("must submit rating")

    elif not request.form.get("review"):
        return error("must submit review")

    elif not request.form.get("isbn"):
        return error("must submit isbn")

    # Insert new review into database
    rating = request.form.get("rating")
    review = request.form.get("review")
    db.execute("INSERT INTO reviews(isbn, user_id, rating, review) VALUES(:isbn, :user_id, :rating, :review)",
               {"isbn": isbn, "user_id": user_id, "rating": rating, "review": review})
    db.commit()

    # Display the book page again
    book_route = "/book/" + isbn
    return redirect(book_route)