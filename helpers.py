import os
from flask import redirect, render_template, request, session
from functools import wraps


def error(message):
    """Render error message to user."""

    # Escape characters
    def escape(s):
        """
        Using meme generator API from https://github.com/jacebrowning/memegen
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s

    # render error.html with escaped message
    return render_template("error.html", message=escape(message))


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/

    based on CS50 pset7 code.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
