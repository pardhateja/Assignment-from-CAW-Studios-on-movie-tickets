from api import app, db
from flask import request, jsonify,make_response
from api.models import Screen, Row ,Cinema,Cinema_Show,User
from __main__ import app
import json
import uuid,jwt,datetime
from werkzeug.security import generate_password_hash,check_password_hash
from email_validator import validate_email, EmailNotValidError
from functools import wraps



#This method is for deleting all the tables which were created as of now.
#Uncomment if needed.
# @app.route('/test', methods=['GET'])
# def test():
#     Cinema_Show.query.delete()
#     Row.query.delete()
#     Screen.query.delete()
#     Cinema.query.delete()
#     User.query.delete()
#     db.session.commit()
#
#     return 'it works!'



#Route for signup of the user
@app.route('/signup', methods=['POST'])
def signup():
    data=request.get_json()
    email=data['email']

    try:
        valid = validate_email(email)
        # Update with the normalized form.
        email = valid.email
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        return jsonify({"status": 202, "message": str(e)})

    user_exists = User.query.filter_by(email=email).first()

    if(user_exists):
        return jsonify({"status": 202, "message": "There is alredy a user with the same email id please login."})

    password=data['password']

    if(len(password)<=6):
        return jsonify({"status": 202, "message": "The password is too short."})

    hashed_password=generate_password_hash(password, method='sha256')
    new_user=User(public_id=str(uuid.uuid4()),name=data['name'],password=hashed_password,email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"status": 200, "message": "The user has been created."})



#Route for login into existing account.
@app.route('/login', methods=['POST'])
def login():
    auth=request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not varify.',401,{'WWW-Authenticate':'Basic realm="Login required!"'})

    user=User.query.filter_by(email=auth.username).first()

    if not user:
        return make_response('Could not varify. There is no user with the given email id.',401,{'WWW-Authenticate':'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token= jwt.encode({'public_id':user.public_id,'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=30)},app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not varify. Kindly check the password and email are correct.',401,{'WWW-Authenticate':'Basic realm="Login required!"'})



#This method is used for authentication check of the API which need authentication
def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token=None

        if 'Authorization' in request.headers:
            token=request.headers['Authorization']

        if not token:
            return jsonify({'status':'400','message': "token is missing."})

        try:
            data=jwt.decode(token,app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()

        except:
            return jsonify({'status':'400','message': "token is Invalid!"})

        return f(current_user, *args, **kwargs)

    return decorated



# Route for entering the details of various screens one at a time
@app.route('/screens', methods=['POST'])
def screens():
    try:
        name = request.json['name']
        shows = request.json['shows']

    except:
        return jsonify({"status": 400, "message": "Bad Request."})

    screen_exist = Screen.query.filter_by(name=name).first()

    if(not screen_exist):
        screen = Screen(name=name)
        db.session.add(screen)
        db.session.commit()

    else:
        return jsonify({"status": 202, "message": "The screen name is already added use another."})

    screen = Screen.query.filter_by(name=name).first()

    for show,value in shows.items():
        cinema_name=value['cinema']
        cinema_exist=Cinema.query.filter_by(name=cinema_name).first()

        if(not cinema_exist):
            cinema = Cinema(name=cinema_name)
            db.session.add(cinema)
            db.session.commit()
            cinema = Cinema.query.filter_by(name=cinema_name).first()
            cinema_id=str(cinema.id)

        else:
            cinema_id=str(cinema_exist.id)

        cinema_show_id=str(screen.id) + '_' + show
        cinema_show=Cinema_Show(id=cinema_show_id,
                                cinema_id=cinema_id)
        db.session.add(cinema_show)
        db.session.commit()

        #For posting seat details to the db.
        seat_info=value['seatInfo']

        for key, value in seat_info.items():
            num_seats = value['numberOfSeats']
            aisle_seats = value['aisleSeats']
            row_id = str(screen.id) + '_' + show + '_' + key
            row = Row(id=row_id,
                      number_of_seats=num_seats,
                      aisle_seats="_".join(str(x) for x in aisle_seats),
                      reserved_seats="")
            db.session.add(row)
            db.session.commit()

    db.session.commit()

    return jsonify({"status": 200, "message": "Screen details successfully added."})



# Route for reserving a ticket at a given screen
@app.route('/screens/<screen_name>/reserve', methods=['POST'])
@token_required
def reserve_seats(current_user,screen_name):
    if not screen_name:
        return jsonify({"message": "Bad request", "status": 400})

    screen = Screen.query.filter_by(name=screen_name).first()
    req_seats_list = []

    try:
        seats = request.json['seats']
        show = request.json['show']

    except :
        return jsonify({"status": 400, "message": "Kindly add the seat numbers and show in body."})

    # Check whether the required seats are available or not
    for key, value in seats.items():
        req_seats = value
        req_seats_list += value
        row_id = str(screen.id)+'_'+show+'_'+key
        row = Row.query.filter_by(id=row_id).first()
        reserved_seats = row.reserved_seats.split('_')

        for seat_no in req_seats:
            if str(seat_no) in reserved_seats:
                return jsonify({"status": 400,
                                "message": "Cannot reserve specified seats!"})

    # Mark the reserved seats in the database
    for key, value in seats.items():
        row_id = str(screen.id) + '_' + show + '_' + key
        row = Row.query.filter_by(id=row_id).first()
        reserved_seats = row.reserved_seats.split('_')
        reserved_seats += value
        reserved_seats = "_".join(str(x) for x in reserved_seats)
        row.reserved_seats = reserved_seats
        db.session.commit()

    return jsonify({"status": 200, "message": "Seats successfully reserved."})


# Route for viewing information of available tickets at a given position
# Route to get available number of tickets for a given screen.
@app.route('/screens/<screen_name>/seats', methods=['GET'])
def available_seats(screen_name):
    status = None

    try:
        status = request.args.get('status')

    except:
        pass

    if not status:
        num_seats = None
        choice = None
        show = None

        try:
            num_seats = request.args.get('numSeats')
            choice = request.args.get('choice')
            show = request.args.get('show')

        except:
            return jsonify({"message": "Bad request.", "status": 400})

        if num_seats and choice and show:
            try:
                num_seats = int(num_seats)

            except:
                return jsonify({"status": 400, "message": "Bad Request."})

            row_num = choice[0]
            seat_num = choice[1:]

            # Get the screen id of the screen spedified by name=screen_name
            id = Screen.query.filter_by(name=screen_name).first().id
            cinema_show_id=str(id) + '_' + show
            cinema_id = Cinema_Show.query.filter_by(id=cinema_show_id).first().cinema_id
            cinema = Cinema.query.filter_by(id=cinema_id).first().name

            # Get the specified row of the screen given by the paarameter 'choice'
            row = Row.query.filter_by(id=str(id)+"_"+show+"_"+row_num).first()
            reserved_seats = row.reserved_seats.split("_")
            reserved_seats.remove('')
            reserved_seats = list(map(int, reserved_seats))
            aisle_seats = row.aisle_seats.split("_")
            aisle_seats = list(map(int, aisle_seats))
            aisle_seats.sort()
            rem_seats = [x for x in list(range(0, row.number_of_seats)) if x not in reserved_seats]

            if int(seat_num) in reserved_seats:
                return jsonify({"message": "Required seats not available!"})

            lst = []
            i = 0

            while i < len(aisle_seats):
                l = []

                for j in rem_seats:
                    if j <= aisle_seats[i+1] and j >= aisle_seats[i]:
                        l.append(j)

                if len(l) >= num_seats:
                    lst.append(l)

                i = i+2

            if len(lst) == 0:
                return jsonify({"status": 520, "message": "Required seats not available!"})

            for l in lst:
                if int(seat_num) in l:
                    if len(l) == seat_num:
                        return jsonify({"cinema":cinema,"availableSeats": {row_num: l}})

                    ind = l.index(int(seat_num))

                    if ind >= num_seats:
                        return jsonify({"cinema":cinema,"availableSeats": {row_num: l[ind+1-num_seats:ind+1]}})

                    else:
                        return jsonify({"cinema":cinema,"availableSeats": {row_num: l[0:num_seats]}})

            return jsonify({"message": "Required seats not available!"})

    # To get all unreserved seats at a given screen
    if status != "unreserved":
        return jsonify({"message": "Bad request", "status": 401})

    # Get the screen object from database with name=screen_name
    screen = Screen.query.filter_by(name=screen_name).first()
    id = screen.id

    # Get all the rows at the screen given by 'screen_name'
    rows = Row.query.filter(Row.id.like(str(id)+"%")).all()
    result = dict()
    shows = dict()

    for row in rows:
        row_split=row.id.split("_")
        show=row_split[1]
        cinema_show_id=row_split[0] + '_' + row_split[1]
        cinema_id = Cinema_Show.query.filter_by(id=cinema_show_id).first().cinema_id
        cinema = Cinema.query.filter_by(id=cinema_id).first().name
        reserved = row.reserved_seats.split('_')
        num = row.number_of_seats
        lst= list(range(0, num))

        for item in reserved:
            try:
                lst.remove(int(item))

            except:
                None
        lst.append("cinema :"+cinema)
        shows[row.id[-1]+'_'+show]=lst

    result["seats"] = shows

    # Return a list of all unreserved seats
    return jsonify(result)



#Route for viewing all the movies currently playing in all screens in all shows
#Route for viewing a particular movie playing in all screens and shows
@app.route('/screens/movies', methods=['GET'])
def movies():
    name = None

    try:
        name = request.args.get('name')

    except:
        pass

    result = dict()
    data=dict()

    if(not name):
        cinema_shows = Cinema_Show.query.all()
        j=0

        for cinema_show in cinema_shows:
            cinema_output = dict()
            cinema_show_id=cinema_show.id.split('_')
            cinema_id=cinema_show.cinema_id
            show=cinema_show_id[1]
            screen_id=cinema_show_id[0]
            cinema = Cinema.query.filter_by(id=cinema_id).first().name
            screen_name=Screen.query.filter_by(id=screen_id).first().name
            cinema_output["screen_name"]=screen_name
            cinema_output["cinema"]=cinema
            cinema_output["show"]=show
            data[j] = cinema_output
            j+=1

        result["cinemas"]=data

        return jsonify(result)

    else:
        cinema_id = Cinema.query.filter_by(name=name).first().id
        cinema_shows = Cinema_Show.query.filter_by(cinema_id=cinema_id).all()
        j=0

        for cinema_show in cinema_shows:
            cinema_output = dict()
            cinema_show_id=cinema_show.id.split('_')
            show=cinema_show_id[1]
            screen_id=cinema_show_id[0]
            screen_name=Screen.query.filter_by(id=screen_id).first().name
            cinema_output["screen_name"]=screen_name
            cinema_output["cinema"]=name
            cinema_output["show"]=show
            data[j] = cinema_output
            j+=1

        result["cinemas"]=data

        return jsonify(result)
