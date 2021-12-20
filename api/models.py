from api import db

# DB model for relation (id, screen_name). One-to-One mapping of unique ids with screen_name
class Screen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

# DB model for relation (id, number_of_seats, aisle_seats, reserved_seats)
# This relation stores the details of each row of a screen.
# id is a unique id made of "screen_id + show_id + row_alphabet"
class Row(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    number_of_seats = db.Column(db.Integer)
    aisle_seats = db.Column(db.String)
    reserved_seats = db.Column(db.String)

# DB model for relation (id, name)
# This relation stores the details of each unique cinema.
class Cinema(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

# DB model for relation (id, cinema_id)
# This relation stores the details of each cinema with the show in which it is been played.
class Cinema_Show(db.Model):
    id=db.Column(db.String(10), primary_key=True)
    cinema_id=db.Column(db.Integer)

# DB model for relation (id, public_id, name, email, password)
# This relation stores the details of each user who has signup his account.
# public_id is a unique id made of uuid4 for maintaining unique values.
class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    public_id=db.Column(db.String(50),unique=True)
    name=db.Column(db.String(50))
    email=db.Column(db.String(80),unique=True)
    password=db.Column(db.String(80))
