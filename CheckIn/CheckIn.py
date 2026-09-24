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

def Status():
    Con = ConnectServer()
    CursorObject = Con.cursor()
    try:
        CursorObject.execute("SHOW COLUMNS FROM PASSENGER LIKE 'CHECKEDIN'")
        column = CursorObject.fetchone()
        
        if column is None:
            CursorObject.execute("ALTER TABLE PASSENGER ADD CHECKEDIN BOOLEAN DEFAULT FALSE")
            Con.commit()
    finally:
        CursorObject.close()
        Con.close()

app = Flask(__name__)


@app.route("/")
def Home():
    return render_template("index.html")


@app.route("/CheckIn", methods=["GET"])
def ShowItems():
    Con = ConnectServer()
    CursorObject = Con.cursor(dictionary=True)

    CursorObject.execute("""SELECT * FROM PASSENGER""")
    data = CursorObject.fetchall()
    for passenger in data:
        if passenger["TRAVELDATE"]:
            passenger["TRAVELDATE"] = str(passenger["TRAVELDATE"])
        if passenger["TRAVELTIME"]:
            total_seconds = int(passenger["TRAVELTIME"].total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            passenger["TRAVELTIME"] = (f"{hours:02d}:{minutes:02d}")
    CursorObject.close()
    Con.close()
    return jsonify(data)


@app.route("/CheckIn/<int:BookingNumber>", methods=["PUT"])
def CheckIn(BookingNumber):
    Con = ConnectServer()
    CursorObject = Con.cursor(dictionary=True)
    CursorObject.execute("""SELECT * FROM PASSENGER WHERE BookingNumber = %s""", (BookingNumber,))
    passenger = CursorObject.fetchone()
    if passenger is None:
        CursorObject.close()
        Con.close()
        return jsonify({"message": "Booking not found"}), 404

    if passenger["CHECKEDIN"] == 1:
        CursorObject.close()
        Con.close()
        return jsonify({"message": "Passenger is already checked in"}), 400
    CursorObject.execute("""UPDATE PASSENGER SET CHECKEDIN = TRUE WHERE BookingNumber = %s""", (BookingNumber,))
    Con.commit()
    CursorObject.close()
    Con.close()

    return jsonify({"message": "Check-in successful", "BookingNumber": BookingNumber})


@app.route("/CheckIn/<int:BookingNumber>", methods=["DELETE"])
def CancelCheckIn(BookingNumber):
    Con = ConnectServer()
    CursorObject = Con.cursor()
    CursorObject.execute("""UPDATE PASSENGER SET CHECKEDIN = FALSE WHERE BookingNumber = %s""", (BookingNumber,))
    Con.commit()
    CursorObject.close()
    Con.close()
    return jsonify({"message": "Check-in removed"})


if __name__ == "__main__":
    Status()
    app.run(host="0.0.0.0", port=5002, debug=False)