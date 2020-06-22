import os
import requests
import re
from flask import Flask, session, render_template, request, redirect, url_for
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
    return render_template('index.html')

@app.route("/login",methods=["GET","POST"])
def login():
    msg = ""
    if request.method == "POST" and request.form.get('username') and request.form.get('password'):
        username = request.form.get("username")
        password = request.form.get("password")
        account = db.execute("SELECT * FROM users \
            WHERE username = :name AND password = :pass",{"name":username,"pass":password}).fetchone()
        if account:
            session['loggedIn'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            return redirect(url_for("home"))
        else:
            msg = "Invalid Username/Password"
    elif request.method == "POST":
        msg = "Please fill out the details!!"
    return render_template("login.html",msg=msg)


@app.route("/logout")
def logout():
    session.pop('loggedIn',None)
    session.pop('id',None)
    session.pop('username',None)
    return redirect(url_for('login'))

@app.route("/register",methods=["GET","POST"])
def register():
    msg = ""
    if request.method == "POST" and 'username' in request.form and 'password' in request.form:
        username = request.form.get("username")
        password = request.form.get("password")
        account = db.execute("SELECT * FROM users \
            WHERE username = :name",{"name":username}).fetchone()
        if account:
            msg = "Account Already exists!!"
        elif not re.match(r"[A-Za-z0-9]+",username):
            msg = "Username must contain only characters and numbers!!"
        elif not username or not password:
            msg = "Please fill out the form!!"
        else:
            db.execute("INSERT INTO users (username, password) \
                VALUES (:name, :pass)",{"name":username,"pass":password})
            db.commit()
            msg = "You are Successfully Registered!!"
    return render_template("signup.html",msg=msg)


@app.route("/home",methods=["GET","POST"])
def home():
    if 'loggedIn' in session:
        if request.method == "POST":
            query = request.form.get("book")
            results = db.execute("SELECT * FROM books WHERE title LIKE :query \
            OR author LIKE :query OR book_id LIKE :query",{"query":query}).fetchall()
            if len(results) == 0:
                results = "empty"
            return render_template("home.html",name = session['username'],results=results)
        return render_template("home.html",name = session['username'])
    return redirect(url_for('login'))

@app.route("/bookPage/<string:isbn>",methods=["GET","POST"])
def bookPage(isbn):
    msg = ""
    if 'loggedIn' in session:
        if request.method == "POST" and request.form.get('score') and request.form.get('textreview'):
            score = request.form.get("score")
            textreview = request.form.get("textreview")
            db.execute("INSERT INTO book_reviews (book_id,username,rating,text_reviews)\
                VALUES (:book_id, :name, :rating, :text)",\
                {"book_id":isbn,"name":session['username'],"rating":int(score),"text":textreview})
            db.commit()
            msg = "Reveiw submitted successfully!!"
        
        elif request.method == "POST":
            msg = "Please fill out the review!!"

        res = requests.get("https://www.goodreads.com/book/review_counts.json", \
            params={"key":os.getenv("KEY"), "isbns": isbn})
        raw = res.json()
        ratings = raw['books'][0]
        book = db.execute("SELECT * FROM books WHERE book_id = :id",{"id":isbn}).fetchone()
        reviews = db.execute("SELECT * FROM book_reviews WHERE book_id = :id",{"id":isbn}).fetchall()
        status = True
        for r in reviews:
            if r[1] == session['username']:
                status=False
        return render_template("book.html",reviews=reviews,book=book,ratings=ratings,msg=msg,status=status)

    return redirect(url_for('login'))




if __name__ == ' __main__':
    app.run(debug=True)
    
    
