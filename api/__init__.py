from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from __main__ import app

@app.before_first_request
def create_tables():
    db.create_all()


app.config['SECRET_KEY'] = '3e69d8d66f3daeaa229143b9d62044cc'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ticketing.db'

db = SQLAlchemy(app)

from api import routes
