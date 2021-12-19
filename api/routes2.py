from api import app, db
from flask import request, jsonify
from api.models import Screen, Row
from __main__ import app


@app.route('/test', methods=['GET'])
def test():
    return 'it works!'

# Route for entering the details of various screens one at a time
@app.route('/screens', methods=['POST'])
def screens():
    try:
        name = request.json['name']
        seat_info = request.json['seatInfo']
    except:
        return jsonify({"status": 400, "message": "Bad Request"})

    screen = Screen(name=name)

    try:
        db.session.add(screen)
        db.session.commit()

        screen = Screen.query.filter_by(name=name).first()

        for key, value in seat_info.items():
            num_seats = value['numberOfSeats']
            aisle_seats = value['aisleSeats']
            row_id = str(screen.id) + '_' + key
            row = Row(id=row_id,
                      number_of_seats=num_seats,
                      aisle_seats="_".join(str(x) for x in aisle_seats),
                      reserved_seats="")
            db.session.add(row)
            db.session.commit()

        db.session.commit()
        return jsonify({"status": 200, "message": "Screen details successfully added"})
    except :
        return jsonify({"status": 400,
                        "message": "Failure to add screen details.This may occur due to duplicate entry of screen name"})



# Route for reserving a ticket at a given screen
@app.route('/screens/<screen_name>/reserve', methods=['POST'])
def reserve_seats(screen_name):
    if not screen_name:
        return jsonify({"message": "Bad request", "status": 400})
    screen = Screen.query.filter_by(name=screen_name).first()
    req_seats_list = []
    seats = request.json['seats']

    # Check whether the required seats are available or not
    for key, value in seats.items():
        req_seats = value
        req_seats_list += value
        row_id = str(screen.id)+'_'+key
        row = Row.query.filter_by(id=row_id).first()
        reserved_seats = row.reserved_seats.split('_')
        for seat_no in req_seats:
            if str(seat_no) in reserved_seats:
                return jsonify({"status": 400,
                                "message": "Cannot reserve specified seats!"})

    # Mark the reserved seats in the database
    for key, value in seats.items():
        row_id = str(screen.id) + '_' + key
        row = Row.query.filter_by(id=row_id).first()
        reserved_seats = row.reserved_seats.split('_')
        reserved_seats += value
        reserved_seats = "_".join(str(x) for x in reserved_seats)
        row.reserved_seats = reserved_seats
        db.session.commit()

    return jsonify({"status": 200, "message": "Seats successfully reserved"})

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
        try:
            num_seats = request.args.get('numSeats')
            choice = request.args.get('choice')
        except:
            return jsonify({"message": "Bad request", "status": 400})

        if num_seats and choice:
            try:
                num_seats = int(num_seats)
            except:
                return jsonify({"status": 400, "message": "Bad Request"})
            row_num = choice[0]
            seat_num = choice[1:]
            # Get the screen id of the screen spedified by name=screen_name
            id = Screen.query.filter_by(name=screen_name).first().id
            # Get the specified row of the screen given by the paarameter 'choice'
            row = Row.query.filter_by(id=str(id)+"_"+row_num).first()
            reserved_seats = row.reserved_seats.split("_")
            reserved_seats.remove('')
            reserved_seats = list(map(int, reserved_seats))
            aisle_seats = row.aisle_seats.split("_")
            aisle_seats = list(map(int, aisle_seats))
            aisle_seats.sort()
            rem_seats = [x for x in list(range(0, row.number_of_seats)) if x not in reserved_seats]
            if int(seat_num) in reserved_seats:
                return jsonify({"message": "Required seats not available"})

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
                        return jsonify({"availableSeats": {row_num: l}})
                    ind = l.index(int(seat_num))
                    if ind >= num_seats:
                        return jsonify({"availableSeats": {row_num: l[ind+1-num_seats:ind+1]}})
                    else:
                        return jsonify({"availableSeats": {row_num: l[0:num_seats]}})

            return jsonify({"message": "Required seats not available!"})

    # To get all unreserved seats at a given screen
    if status != "unreserved":
        return jsonify({"message": "Bad request", "status": 400})

    # Get the screen object from database with name=screen_name
    screen = Screen.query.filter_by(name=screen_name).first()
    id = screen.id
    # Get all the rows at the screen given by 'screen_name'
    rows = Row.query.filter(Row.id.like("%"+str(id)+"%")).all()
    result = dict()
    seats = dict()
    for row in rows:
        reserved = row.reserved_seats.split('_')
        num = row.number_of_seats
        lst = list(range(0, num))
        for item in reserved:
            try:
                lst.remove(int(item))
            except:
                None
        seats[row.id[-1]] = lst
    result["seats"] = seats

    # Return a list of all unreserved seats
    return jsonify(result)
