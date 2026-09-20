from .database import db

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False, default='user')
    reservation_details = db.relationship('Reservation', backref='bearer')


class Parkinglot(db.Model):
    __tablename__ = 'Parkinglot'
    id = db.Column(db.Integer, primary_key=True)

    prime_location_name = db.Column(db.Text, unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.Integer, nullable=False)
    number_of_spots = db.Column(db.Integer, nullable=False)
    spots = db.relationship('ParkingSpot', backref='lot')


class ParkingSpot(db.Model):
    __tablename__ = 'ParkingSpot'
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('Parkinglot.id'), nullable=False)
    status = db.Column(db.Text, nullable=False, default='A')
    reservations = db.relationship('Reservation', backref='spot')


class Reservation(db.Model):
    __tablename__ = 'Reservation'
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('ParkingSpot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    vehicle_number = db.Column(db.Text, nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False)
    leaving_timestamp = db.Column(db.DateTime, nullable=True) 
    parking_cost = db.Column(db.Integer, nullable=True)
