import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine(os.getenv("DATABASE_URL"))

db = scoped_session(sessionmaker(bind=engine))

db.execute("CREATE TABLE users ( id SERIAL PRIMARY KEY,\
    username VARCHAR NOT NULL, password VARCHAR NOT NULL)")

#db.execute("CREATE TABLE book_reviews ( book_id VARCHAR REFERENCES books, reviews VARCHAR)")

db.execute("CREATE TABLE book_reviews (book_id VARCHAR REFERENCES books, username VARCHAR NOT NULL, rating INTEGER NOT NULL, text_reviews VARCHAR)")

db.commit()
