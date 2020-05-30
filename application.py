import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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
def index():
    books = db.execute("SELECT title FROM books limit 10").fetchall()
    return render_template("index.html",books = books)

@app.route("/home",methods=["GET","POST"])
def home():
    if request.method == "POST":
        query = request.form.get("book")
        results = db.execute("SELECT * FROM books WHERE title LIKE :query \
            OR author LIKE :query OR book_id LIKE :query",{"query":query}).fetchall()
        return render_template("home.html",results=results)
    #users = db.execute("SELECT id, username FROM users WHERE username = :username", {"username": name} )
    return render_template("home.html")

@app.route("/bookPage/<string:id>",methods=["GET","POST"])
def bookPage(id):
    book = db.execute("SELECT * FROM books WHERE book_id = :id",{"id":id}).fetchone()
    reviews = db.execute("SELECT reviews FROM book_reviews WHERE book_id = :id",{"id":id}).fetchall()
    return render_template("book.html",reviews=reviews,book=book)
