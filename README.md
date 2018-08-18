# Project 1: Book Review Website

For CS50 Web Programming with Python and JavaScript.

Python and Flask are used as the server to direct the pages and the API.
A third-party API by Goodreads (a book review website) to use ratings on books.

Directions:
Created a web page to search for book reviews and ratings.
Users may register to the website ("/register").
Users may log in using their credentials and sessions ("/login").
Once logged in, users may be able to search for books ("/").
The search results will display on the same page ("/") where users may click on the titles for details.
When clicked, users are directed to ("/book/<isbn>") where details of the book, including ratings and reviews from Goodreads can be found.
Users may also write a review (one for each book only) on the book detail page and when submitted, will automatically refresh the page.
Users may also request a JSON for book details and reviews by a GET request via the website's API ("api/<isbn>").
