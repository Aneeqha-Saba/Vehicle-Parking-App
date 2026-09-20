from celery import shared_task 
import csv
from jinja2 import Template
from .mail import send_email
from .database import db
from .models import *
from datetime import datetime, timezone
import requests
from sqlalchemy import extract, func

# Task 1 User Triggered Async Job - Export as CSV - Devise a CSV format details for the parking spots used by the user till date
# This export is meant to download the parking details (slot_id, spot_id,  timestamps, coset, remarks etc.)
# Have a dashboard from where the user can trigger the export
# This should trigger a batch job, and send an alert once done

@shared_task(ignore_result=False, name = "download_csv_report")
def csv_report():
    spot_details = Reservation.query.filter_by().all()
    csv_file_name = f"Parking_{datetime.now(timezone.utc).strftime('%d%m%y_%f')}.csv"
    with open(f'static/{csv_file_name}', 'w', newline = "") as csvfile:
        sr_no = 1
        spot_csv = csv.writer(csvfile, delimiter = ',')
        spot_csv.writerow(['Sr No.','User ID','Lot ID', 'Spot ID', 'Parking Timestamp', 'Leaving Timestamp', 'Price', 'Vehicle Number'])
        for s in spot_details:
            this_spot = [sr_no, s.user_id, s.spot.lot_id, s.spot_id, s.parking_timestamp, s.leaving_timestamp, s.parking_cost, s.vehicle_number]
            spot_csv.writerow(this_spot)
            sr_no += 1

    return csv_file_name

#Task 2 Scheduled Job - Monthly Activity Report - Devise a monthly report for the user created using HTML and sent via mail.
# The activity report can include parking spots booked per month, Most used parking lot by the user, amount spent on parking for a month or any relevant information to the user etc.
# For the monthly report to be sent, start a job on the first day of every month → create a report using the above parameters → send it as an email

# user_data = {
#     username : 
#     email :
#     details: [
#         {
#             parking spots booked per month: 23
#             most used parking lots: {1:12, 2:10, 3:4}
#             amount spent on parking every month: 23,400 rupees
#         }
#     ]
# }

#function returns a number of how many spots were booked in a month by a user
def spot_per_month(user_id):
    now = datetime.now(timezone.utc)
    year = now.year
    month = now.month
    return Reservation.query.filter( Reservation.user_id == user_id, extract('year', Reservation.parking_timestamp) == year, extract('month', Reservation.parking_timestamp) == month).count()

# function returns a list of most used lots example Most used Lots in a month = {lot 1 = 12 times parked, lots 2 = 3 times parked, lot 3 = 1 time parked}
def lots_per_month(user_id):
    now = datetime.now(timezone.utc)
    year = now.year
    month = now.month
    results = (db.session.query(Parkinglot.prime_location_name, func.count(Reservation.id)).join(ParkingSpot, ParkingSpot.lot_id == Parkinglot.id).join(Reservation, Reservation.spot_id == ParkingSpot.id).filter( Reservation.user_id == user_id, extract('year', Reservation.parking_timestamp) == year, extract('month', Reservation.parking_timestamp) == month ).group_by(Parkinglot.prime_location_name).all())
    return {lot: count for lot, count in results}

# function returns an amount spend on parking by a user in a month
def amount_per_month(user_id):
    now = datetime.now(timezone.utc)
    year = now.year
    month = now.month
    amount = (db.session.query(func.sum(Reservation.parking_cost)).filter(Reservation.user_id == user_id, extract('year', Reservation.parking_timestamp) == year, extract('month', Reservation.parking_timestamp) == month).scalar())
    return amount or 0

@shared_task(ignore_result=False, name="monthly_report")
def monthly_report():
    users = User.query.all()
    for user in users[1:]: 
        total_spots = spot_per_month(user.id)
        user_lots = lots_per_month(user.id)
        total_amount = amount_per_month(user.id)
        user_data = {
            "username": user.username,
            "details": [
                {
                    "spots": total_spots,
                    "lots": user_lots,
                    "amount": f"{total_amount} rupees"
                }
            ]
        }
        mail_template = """
        <h3>Dear {{ user_data.username }}</h3>
        <p>Please find the current status of your Parking in the table below.</p>
        <p>Visit our Vehicle Parking App at http://127.0.0.1:5173 for details.</p>

        <table border="1" cellpadding="6">
            <tr>
                <th>Parking Spots Booked</th>
                <th>Most Used Parking Lots</th>
                <th>Amount Spent</th>
            </tr>

            {% for d in user_data.details %}
            <tr>
                <td>{{ d.spots }}</td>
                <td>
                    {% for lot, count in d.lots.items() %}
                        {{ lot }} = {{ count }} times<br>
                    {% endfor %}
                </td>
                <td>{{ d.amount }}</td>
            </tr>
            {% endfor %}
        </table>
        """
        message = Template(mail_template).render(user_data=user_data)
        send_email(user.email, "Monthly Parking Report", message)
    return "Monthly report sent."



# Task 3 Scheduled Job - Daily reminders - The application should send daily reminders to users on g-chat using Google Chat Webhooks or SMS or mail
# Check if a user has not visited or parking lot is created by the admin
# If yes, then send the alert asking them to book a parking spot if required by them
# The reminder can be sent in the evening, every day (students can choose the time)

@shared_task(ignore_results=False, name="generate_msg")
def generate_msg(username, message):
    text = f"Hi {username}, {message}"
    response = requests.post(
        "https://chat.googleapis.com/v1/spaces/AAQAwhaN85c/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=NHNiH7QxqZcwpD2RL3CR9_AnLagsEcjhbW5V4tUqnPc",
        json={"text": text}
    )
    print(response.status_code, response.text)
    return "Notification sent"
