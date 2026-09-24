from flask import Flask, request, jsonify, render_template
import mysql.connector
import time


def ConnectServer():
    while True:
        try:
            return mysql.connector.connect(
                host="bookingdb",
                port=3306,
                user="BookingUser",
                password="BookingPassword",
                database="BookingDb"
            )
        except mysql.connector.Error:
            print("Waiting for MySQL...")
            time.sleep(2)


def CreateDatabase():
    while True:
        try:
            con = mysql.connector.connect(
                host="bookingdb",
                port=3306,
                user="BookingUser",
                password="BookingPassword"
            )
            cursorObject = con.cursor()
            cursorObject.execute("CREATE DATABASE IF NOT EXISTS BookingDb")
            cursorObject.close()
            con.close()
            break
        except mysql.connector.Error:
            print("Waiting for MySQL...")
            time.sleep(2)


def CreateTable():
    con = ConnectServer()
    cursorObject = con.cursor()
    cursorObject.execute("""
        CREATE TABLE IF NOT EXISTS PASSENGER (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            NAME VARCHAR(20) NOT NULL,
            SURNAME VARCHAR(20) NOT NULL,
            PHONENUMBER VARCHAR(20),
            EMAIL VARCHAR(100),
            BookingNumber INT,
            TRAVELDATE DATE NOT NULL,
            TRAVELTIME TIME NOT NULL,
            CHECKEDIN BOOLEAN DEFAULT FALSE
        )
    """)
    con.commit()
    cursorObject.close()
    con.close()


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/Booking", methods=["POST"])
def MakeBooking():

    data = request.get_json()
    Con = ConnectServer()
    CursorObject = Con.cursor()
    CursorObject.execute("""INSERT INTO PASSENGER(NAME,SURNAME,PHONENUMBER,EMAIL,TRAVELDATE,TRAVELTIME)VALUES (%s, %s, %s, %s, %s, %s)""", (data["NAME"],data["SURNAME"],data["PHONENUMBER"],data["EMAIL"],data["TRAVELDATE"],data["TRAVELTIME"]))
    BookingNumber = CursorObject.lastrowid
    CursorObject.execute("""UPDATE PASSENGER SET BookingNumber = %s WHERE ID = %s""", (BookingNumber,BookingNumber))
    Con.commit()
    CursorObject.close()
    Con.close()
    return jsonify({"message": "Booking created","BookingNumber": BookingNumber})


@app.route("/Booking", methods=["GET"])
def ShowItems():
    Con = ConnectServer()
    CursorObject = Con.cursor(dictionary=True)
    CursorObject.execute("SELECT * FROM PASSENGER")
    data = CursorObject.fetchall()
    for booking in data:
        if booking["TRAVELDATE"]:
            booking["TRAVELDATE"] = str(booking["TRAVELDATE"])
        if booking["TRAVELTIME"]:
            total_seconds = int(booking["TRAVELTIME"].total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            booking["TRAVELTIME"] = (f"{hours:02d}:{minutes:02d}")
    CursorObject.close()
    Con.close()
    return jsonify(data)


@app.route("/Booking/<int:id>", methods=["DELETE"])
def DeleteItem(id):
    Con = ConnectServer()
    CursorObject = Con.cursor()
    CursorObject.execute("DELETE FROM PASSENGER WHERE ID = %s",(id,))
    Con.commit()
    CursorObject.close()
    Con.close()
    return jsonify({"message": "Booking deleted"})


if __name__ == "__main__":
    CreateDatabase()
    CreateTable()
    app.run(host="0.0.0.0",port=5001,debug=False)
