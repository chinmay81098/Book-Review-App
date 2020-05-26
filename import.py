import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))

db = scoped_session(sessionmaker(bind=engine))


f = open("books.csv")
reader = csv.reader(f)
next(reader,None)

db.execute("CREATE TABLE books ( book_id VARCHAR PRIMARY KEY,\
    title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INTEGER)")

for book_id, title, author, year in reader  :
    db.execute("INSERT INTO books (book_id, title, author, year) VALUES (:book_id, :title, :author, :year)",
        {"book_id":book_id, "title":title, "author":author, "year":year})
    print(f"Added books titled {title} written by {author} in {year}")

db.commit()
