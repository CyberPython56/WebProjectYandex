from flask import Flask, render_template, url_for, request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
app = Flask(__name__)
sqlite_connection = sqlite3.connect('YandexProject.sqlite', check_same_thread=False)
cursor = sqlite_connection.cursor()

def valid(login: str, password: str):
    req = f"""
SELECT * FROM "Admins"
"""
    resp = cursor.execute(req).fetchall()
    if len(resp) == 0:
        return False
    for i in resp:
        if i[1] == login and i[2] == password:
            return True
    return False

def get_bookings():
    req = f"""
SELECT * FROM "Booking"
"""
    resp = cursor.execute(req).fetchall()

    data = []
    for i in reversed(resp):
        d = {
            "id": i[0],
            "computer_id": i[1],
            "name": i[2],
            "date": i[3],
            "time_start": i[4],
            "time_finish": i[5],
            "full_price": i[6]
        }
        data.append(d)

    return data

@app.route('/')
def login_page():
    return render_template("login.html")

@app.route('/booking/')
def booking_page():
    username = request.args.get('login')
    password = request.args.get('password')
    if valid(username, password):
        return render_template("bookings.html", orders=get_bookings())
    else:
        return "Invalid login or Password"

if __name__ == "__main__":
    app.run(debug=True)
