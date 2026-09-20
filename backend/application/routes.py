from flask import current_app as app, jsonify, request, abort
from flask import send_from_directory
from app import app, cache
from application.models import *
from flask_jwt_extended import create_access_token, jwt_required, current_user
from application.database import db
from functools import wraps
import random
import string
from celery.result import AsyncResult
from .tasks import csv_report, monthly_report, generate_msg
from datetime import datetime, timezone
from sqlalchemy import  or_
from sqlalchemy.exc import SQLAlchemyError




# ---------------------------
# Role-based decorator
# ---------------------------

def role_required(required_role):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorated(*args, **kwargs):
            if current_user.role != required_role:
                return jsonify(message = "You are not authorized"), 403
            return fn(*args, **kwargs)
        return decorated
    return wrapper

# ---------------------------
# Auth Routes
# ---------------------------

@app.route("/api/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(username=username).first()
    if not user or not user.password == password:
        return jsonify(message = "Wrong Username or Password"), 400
    
    access_token = create_access_token(identity=user) #identity from security
    return jsonify(access_token=access_token) #access token uses secret key internally to encrypt and retrieve the data

@app.route("/api/register", methods=["POST"])
def register():
    username = request.json.get("username", None)
    email = request.json.get("email", None)
    address = request.json.get("address", None)
    pincode = request.json.get("pincode", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(username = username).first()
    if user:
        return jsonify(message = "User already exists"), 400
    
    user = User(username=username, email=email, address=address, pincode=pincode, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify(message = "User created successfully"), 201

# ---------------------------
# Admin Dashboard & User Dashboard Route
# ---------------------------

@app.route("/api/dashboard")
@jwt_required()
@cache.cached(timeout=300, key_prefix=lambda: f"dashboard_{current_user.id}")
def dashboard():
    if current_user.role == "admin":
        users = User.query.filter_by(role="user").count()
        lots = Parkinglot.query.all()

        parking_lot_details = []
        available_by_lot = {}

        for lot in lots:
            total_spots = len(lot.spots)
            occupied_spots = 0
            spots_list = []

            for spot in lot.spots:
                if spot.status == "O":
                    occupied_spots += 1
                    latest_reservation = (
                        Reservation.query
                        .filter_by(spot_id=spot.id)
                        .order_by(Reservation.parking_timestamp.desc())
                        .first()
                    )
                    username = latest_reservation.bearer.username if latest_reservation else "Unknown"
                    spots_list.append({
                        "spot_id": spot.id,
                        "parking_lot_id": spot.lot_id,
                        "occupied_by_id": latest_reservation.user_id if latest_reservation else None,
                        "vehicle_number": latest_reservation.vehicle_number if latest_reservation else None,
                        "parking_timestamp": latest_reservation.parking_timestamp if latest_reservation else None,
                        "parking_cost": latest_reservation.parking_cost if latest_reservation else None,
                        "status": "Occupied",
                        "occupied_by": username
                    })
                else:
                    spots_list.append({
                        "spot_id": spot.id,
                        "status": "Available"
                    })

            available_spots = total_spots - occupied_spots
            available_by_lot[str(lot.id)] = available_spots

            parking_lot_details.append({
                "parking_lot_id": lot.id,
                "lot_name": f"Parking Lot : {lot.id}",
                "prime_location_name": lot.prime_location_name,
                "address": lot.address,
                "pin_code": lot.pin_code,
                "price": lot.price,
                "total_spots": total_spots,
                "available_spots": available_spots,
                "occupied_spots": occupied_spots,
                "spots": spots_list,
                "actions": ["Edit", "Delete"]
            })

        return jsonify({
            "role": current_user.role,
            "admin_name": current_user.username,
            "email": current_user.email,
            "address": current_user.address,
            "pincode": current_user.pincode,
            "users": users,
            "available parking spot in each lot": available_by_lot,
            "no of parking lots": len(lots),
            "parking_lot_details": parking_lot_details
        })
    else:
        #user must see all the parking lots available and parkling spot booked by them
        lots = Parkinglot.query.all()
        parking_lot_details = []
        total_available_spots = 0
        

        for lot in lots:
            total_spots = len(lot.spots)
            occupied_spots = sum(1 for spot in lot.spots if spot.status == "O")
            available_spots = total_spots - occupied_spots
            total_available_spots += available_spots
            spot_list = []

            for spot in lot.spots:
                spot_list.append({
                    "spot_id": spot.id,
                    "status": spot.status  # 'A' = Available, 'O' = Occupied
                })

            parking_lot_details.append({
                "parking_lot_id": lot.id,
                "prime_location_name": lot.prime_location_name,
                "address": lot.address,
                "pin_code": lot.pin_code,
                "price": lot.price,
                "total_spots": total_spots,
                "available_spots": available_spots,
                "spots": spot_list
            })

        user_reservations = (
            Reservation.query
            .filter_by(user_id=current_user.id)
            .order_by(Reservation.parking_timestamp.desc())
            .all()
        )

        booked_spots = [
            {
                "reservation_id": r.id,
                "spot_id": r.spot_id,
                "lot_id": r.spot.lot_id,
                "location_name": r.spot.lot.prime_location_name,
                "vehicle_number": r.vehicle_number,
                "Cost": r.parking_cost if r.parking_cost else "Pending",
                "lot_price": r.spot.lot.price,
                "status": "Occupied" if not r.leaving_timestamp else "Available",
                "parking_timestamp": r.parking_timestamp,
                "leaving_timestamp": r.leaving_timestamp.strftime('%Y-%m-%d %H:%M:%S') if r.leaving_timestamp else "N/A"
            }
            for r in user_reservations
        ]

        return jsonify({
            "role": current_user.role,
            "user_name": current_user.username,
            "email": current_user.email,
            "address": current_user.address,
            "pincode": current_user.pincode,
            "user_id": current_user.id,
            "no_of_parking_lots": len(lots),
            "parking_lot_details": parking_lot_details,
            "your_bookings": booked_spots
        })



# Create Parking Lot
@app.route("/api/create_lot", methods=["POST"])
@jwt_required()
def create_parking_lot():
    if current_user.role != "admin":
        return jsonify(message="Not authorized"), 403

    data = request.get_json()

    try:
        new_lot = Parkinglot(
            prime_location_name=data["prime_location_name"],
            price=data["price"],
            address=data["address"],
            pin_code=data["pin_code"],
            number_of_spots=data["number_of_spots"]
        )

        db.session.add(new_lot)
        db.session.commit()
        for _ in range(new_lot.number_of_spots):
            spot = ParkingSpot(lot_id=new_lot.id, status="A")
            db.session.add(spot)

        db.session.commit()

        for user in User.query.all():
            cache.delete(f"dashboard_{user.id}")

        users = User.query.filter(User.role != "admin").all()
        for user in users:
            res = generate_msg.delay(user.username, f"A new parking lot has been created at {new_lot.prime_location_name}. Please check the app at http://localhost:5173/")

        return jsonify(message="Parking lot created successfully"), 201

    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 400


# Admin: Edit Parking Lot
@app.route("/api/edit_lot/<int:lot_id>", methods=["GET", "PUT"])
@role_required("admin")
def edit_lot(lot_id):
    lot = Parkinglot.query.get(lot_id)
    if not lot:
        return jsonify(message="Lot not found"), 404
    
    if request.method == "GET":
        return jsonify({
            "prime_location_name": lot.prime_location_name,
            "price": lot.price,
            "address": lot.address,
            "pin_code": lot.pin_code,
            "number_of_spots": lot.number_of_spots
        })
    elif request.method == "PUT":
        data = request.get_json()
        try:
            lot.prime_location_name = data.get("prime_location_name", lot.prime_location_name)
            lot.price = data.get("price", lot.price)
            lot.address = data.get("address", lot.address)
            lot.pin_code = data.get("pin_code", lot.pin_code)
            lot.number_of_spots = data.get("number_of_spots", lot.number_of_spots)
            db.session.commit()
            for user in User.query.all():
                cache.delete(f"dashboard_{user.id}")
            return jsonify(message="Lot updated")
        except Exception as e:
            return jsonify(error=str(e)), 400



# Admin: Delete Lot 
@app.route("/api/delete_lot/<int:lot_id>", methods=["DELETE"])
@role_required("admin")
def delete_lot(lot_id):
    lot = Parkinglot.query.get(lot_id)
    if not lot:
        return jsonify(message="Lot not found"), 404

    if any(spot.status == "O" for spot in lot.spots):
        return jsonify(message="Cannot delete lot. Some spots are occupied."), 400
    
    for spot in lot.spots:
        db.session.delete(spot)
    
    db.session.delete(lot)
    db.session.commit()

    for user in User.query.all():
        cache.delete(f"dashboard_{user.id}")
    return jsonify(message="Lot deleted"), 200

def calc_estimated_cost(spot):
    if not spot.reservations:
        return 0
    
    start_time = spot.reservations.parking_timestamp
    end_time = spot.reservations.leave_timestamp or datetime.now()
    
    duration_hours = (end_time - start_time).total_seconds() / 3600
    duration_hours = int(duration_hours) + (1 if duration_hours % 1 > 0 else 0)
    
    price_per_hour = spot.price  
    
    return duration_hours * price_per_hour

# Get all spots
@app.route("/api/view_spot", methods=["GET"])
@role_required("admin")
def get_spots():
    spots = ParkingSpot.query.all()

    return jsonify([{
        "id": s.id,
        "customer_id": s.reservations.user_id if s.reservations else None,
        "vehicle_number": s.reservations.vehicle_number if s.reservations else None,
        "parking_timestamp": s.reservations.parking_timestamp if s.reservations else None,
        "leave_timestamp": s.reservations.leave_timestamp if s.reservations else None,
        "estimated_cost": calc_estimated_cost(s),
        "status": s.status
    } for s in spots])

# Delete a spot (only if available)
@app.route("/api/parking_spot/<int:spot_id>", methods=["DELETE"])
@role_required("admin")
def delete_spot(spot_id):
    spot = ParkingSpot.query.get(spot_id)
    if not spot:
        return jsonify(message="Spot not found"), 404

    if spot.status != "A":
        return jsonify(message="Cannot delete occupied spot"), 400

    db.session.delete(spot)
    db.session.commit()
    for user in User.query.all():
        cache.delete(f"dashboard_{user.id}")
    return jsonify(message="Spot deleted successfully")

# Admin: View All Users
@app.route("/api/users", methods=["GET"])
@role_required("admin")
def list_users():
    users = User.query.filter_by(role="user").all()
    response = []

    for u in users:
        reservations = Reservation.query.filter_by(user_id=u.id).all()

        lot_ids = set()
        for r in reservations:
            if r.spot and r.spot.lot: 
                lot_ids.add(r.spot.lot.id)

        user_info = {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "address": u.address,
            "pincode": u.pincode,
            "parking_lots": list(lot_ids) if lot_ids else ["N/A"]
        }

        response.append(user_info)

    return jsonify(response)


#--------------------------------------------------------
# User APIS
#--------------------------------------------------------

#booking a spot 
@app.route('/api/reserve_spot/', methods=['POST'])
@role_required("user")
def reserve_spot():
    data = request.get_json()
    lot_id = data.get('lot_id')
    vehicle_number = data.get('vehicle_number')
    user_id = current_user.id
    active_reservation = Reservation.query.filter_by(vehicle_number=vehicle_number, leaving_timestamp=None).first()

    if active_reservation:
        return jsonify(message="This vehicle is already parked!"), 400

    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()

    if not spot:
        return jsonify(message="No available spots in this lot"), 400

    reservation = Reservation(
        spot_id=spot.id,
        user_id=user_id,
        vehicle_number=vehicle_number,
        parking_timestamp=datetime.now(timezone.utc)
    )
    db.session.add(reservation)

    spot.status = 'O'
    db.session.commit()
    cache.delete(f"dashboard_{current_user.id}")

    return jsonify(message="Spot reserved successfully", spot_id=spot.id, vehicle_number=vehicle_number), 200

#release a spot
@app.route('/api/release_spot/', methods=['POST'])
@role_required("user")
def release_spot():
    print("===> /api/release_spot called!")
    print("Headers:", request.headers)
    data = request.get_json()
    print("Data received:", data)
    spot_id = data.get('spot_id')
    spot = ParkingSpot.query.get(spot_id)
    price = Parkinglot.query.get(spot.lot_id).price
    if not spot:
        return jsonify(message="Spot not found"), 404

    if spot.status != 'O':
        return jsonify(message="Spot is not currently occupied"), 400

    reservation = Reservation.query.filter_by(spot_id=spot.id).order_by(Reservation.parking_timestamp.desc()).first()
    
    if not reservation or reservation.leaving_timestamp:
        return jsonify(message="No active reservation found"), 400
    
    if reservation.user_id != current_user.id:
        return jsonify(message="You are not authorized to release this spot"), 403

    reservation.leaving_timestamp = datetime.utcnow()

    duration = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds() / 3600
    cost_per_hour = price
    reservation.parking_cost = round(duration * cost_per_hour, 2)

    spot.status = 'A'

    db.session.commit()
    cache.delete(f"dashboard_{current_user.id}")

    return jsonify(message="Spot released successfully", cost=reservation.parking_cost), 200


#view parking lot details
@app.route("/api/user/lots", methods=["GET"])
@role_required("user")
def get_available_lots():
    lots = Parkinglot.query.all()
    result = []
    for lot in lots:
        available_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status="A").count()
        result.append({
            "id": lot.id,
            "name": lot.prime_location_name,
            "address": lot.address,
            "price": lot.price,
            "available_spots": available_spots
        })
    return jsonify(result)


@app.route("/api/search", methods=["POST"])
@jwt_required()
def user_search():
    data = request.get_json(silent=True) or {}
    searchtext = (data.get("text_search") or "").strip()

    if not searchtext:
        return jsonify({"search_results": [], "message": "Please enter search text."}), 400

    try:
        if current_user.role == "admin":
            if not searchtext.isdigit():
                return jsonify({"search_results": [], "message": "Please enter a valid numeric User ID."}), 400

            users = User.query.filter(User.id.like(f"%{searchtext}%")).all()
            results = [
                {
                    "id": u.id,
                    "name": getattr(u, "username", None),
                    "email": getattr(u, "email", None),
                    "address": getattr(u, "address", None),
                    "pincode": getattr(u, "pincode", None),
                }
                for u in users
            ]
            return jsonify({"search_results": results}), 200
        else:
            lots = Parkinglot.query.filter(
                Parkinglot.prime_location_name.ilike(f"%{searchtext}%")
            ).all()

            results = []
            for lot in lots:
                spots = getattr(lot, "spots", []) or []
                total_spots = len(spots)
                occupied_spots = sum(1 for s in spots if getattr(s, "status", None) == "O")
                available_spots = total_spots - occupied_spots

                results.append({
                    "parking_lot_id": getattr(lot, "parking_lot_id", getattr(lot, "id", None)),
                    "address": getattr(lot, "address", None),
                    "prime_location_name": getattr(lot, "prime_location_name", None),
                    "price": getattr(lot, "price", None),
                    "total_spots": total_spots,
                    "occupied_spots": occupied_spots,
                    "available_spots": available_spots,
                })

            return jsonify({"search_results": results}), 200

    except Exception as e:
        return jsonify({"search_results": [], "message": str(e)}), 500

@app.route("/api/summary", methods=["GET"])
@jwt_required()
def summary():
    if current_user.role == "admin":
        lots = Parkinglot.query.all()
        data = []

        for lot in lots:
            total_spots = len(lot.spots)
            occupied_spots = sum(1 for s in lot.spots if s.status == 'O')
            available_spots = total_spots - occupied_spots

            data.append({
                "lot_name": lot.prime_location_name,
                "available": available_spots,
                "occupied": occupied_spots,
            })
        
        return jsonify(data), 200

    else:
        user_id = current_user.id
        reservations = Reservation.query.filter_by(user_id=user_id).all()

        usage_summary = {}
        for r in reservations:
            if r.spot and r.spot.lot:
                lot_name = r.spot.lot.prime_location_name
                usage_summary[lot_name] = usage_summary.get(lot_name, 0) + 1

        return jsonify(usage_summary), 200
    
@app.route("/api/update_profile", methods=["POST"])
@jwt_required()
def update_profile():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    address = data.get("address")
    pincode = data.get("pincode")
    password = data.get("password") 

    if current_user.role == "admin":
        current_user.username = name
    else:
        current_user.username = name

    current_user.email = email
    current_user.address = address
    current_user.pincode = pincode
    current_user.password = password
    db.session.commit()

    cache.delete(f"dashboard_{current_user.id}")

    return jsonify({"message": "Profile updated successfully"}), 200
 

@app.route('/export_csv')
def export():
    result = csv_report.delay()
    return {
        "id": result.id,
        "result": result.result
    }

@app.route('/api/csv_result/<id>')
def csv_result(id):
    res = AsyncResult(id)
    # return {
    #     "filename": res.result
    # }
    if not res.ready():
        return jsonify({"status": "pending"}), 202
    return send_from_directory('static', res.result)

@app.route('/api/send_mail')
def send_mail():
    res = monthly_report.delay()
    return {
        "message": res.result
    }


    