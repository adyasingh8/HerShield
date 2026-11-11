from sqlalchemy.engine import URL
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
from flask import session
from flask import jsonify
from datetime import datetime
import smtplib
from email.message import EmailMessage
import os
import secrets

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)


app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

database_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME")
)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url

# Configure SSL only when a certificate path is provided
ssl_ca = os.getenv("DB_SSL_CA")
connect_args = {}

if ssl_ca:
    ca_path = (
        ssl_ca if os.path.isabs(ssl_ca)
        else os.path.join(os.path.dirname(os.path.abspath(__file__)), ssl_ca)
    )

    connect_args = {
        "ssl": {
            "ca": ca_path
        }
    }

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": connect_args
}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class SOSAlert(db.Model):
    __tablename__ = "sos_alerts"

    alert_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    latitude = db.Column(db.Numeric(10, 7))
    longitude = db.Column(db.Numeric(10, 7))

    status = db.Column(db.String(30), default="Active")

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class LiveLocation(db.Model):
    __tablename__ = "live_locations"

    location_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    alert_id = db.Column(
        db.Integer,
        db.ForeignKey("sos_alerts.alert_id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    latitude = db.Column(db.Numeric(10, 7), nullable=False)
    longitude = db.Column(db.Numeric(10, 7), nullable=False)

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )    


class Journey(db.Model):

    __tablename__ = "journeys"

    journey_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    start_location = db.Column(
        db.String(255),
        nullable=False
    )

    destination = db.Column(
        db.String(255),
        nullable=False
    )

    share_token = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        default=lambda: secrets.token_urlsafe(32)
    )

    status = db.Column(
        db.String(20),
        default="Active",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )    


class JourneyLocation(db.Model):

    __tablename__ = "journey_locations"

    location_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    journey_id = db.Column(
        db.Integer,
        db.ForeignKey("journeys.journey_id"),
        nullable=False
    )

    latitude = db.Column(
        db.Numeric(10, 7),
        nullable=False
    )

    longitude = db.Column(
        db.Numeric(10, 7),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    
class EmergencyContact(db.Model):

    __tablename__ = "emergency_contacts"

    contact_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    phone = db.Column(
        db.String(15),
        nullable=False
    )

    relationship = db.Column(
        db.String(50),
        nullable=False
    )

    email = db.Column(db.String(120), nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)    

def send_emergency_email(to_email, latitude, longitude):

    sender_email = os.getenv("EMAIL_ADDRESS")
    app_password = os.getenv("EMAIL_APP_PASSWORD")

    if not sender_email or not app_password:
        print("Email credentials are missing.")
        return False

    maps_link = (
        f"https://www.google.com/maps?q={latitude},{longitude}"
    )

    msg = EmailMessage()
    msg["Subject"] = "EMERGENCY ALERT - HerShield"
    msg["From"] = sender_email
    msg["To"] = to_email

    msg.set_content(f"""
EMERGENCY ALERT FROM HERSHIELD

An emergency SOS alert has been triggered.

The user's current location is:

Latitude: {latitude}
Longitude: {longitude}

View the location on Google Maps:
{maps_link}

Please try to contact the user and provide appropriate assistance.

This is an automated emergency notification from HerShield.
""")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)

        print(f"Emergency email sent to {to_email}")
        return True

    except Exception as e:
        print("Email sending failed:", e)
        return False   


def send_journey_email(to_email, subject, message):

    sender_email = os.getenv("EMAIL_ADDRESS")
    app_password = os.getenv("EMAIL_APP_PASSWORD")

    if not sender_email or not app_password:
        print("Email credentials are missing.")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    msg.set_content(message)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)

        print("Journey email sent to", to_email)
        return True

    except Exception as e:
        print("Journey email failed:", e)
        return False    


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # Check whether email already exists
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email is already registered!")
            return redirect(url_for('register'))

        # Encrypt the password using hashing
        hashed_password = generate_password_hash(password)

        new_user = User(
            name=name,
            email=email,
            phone=phone,
            password_hash=hashed_password
        )

        try:
            db.session.add(new_user)
            db.session.commit()

            flash("Registration successful! Please login.")
            return redirect(url_for('login'))

        except Exception:
            db.session.rollback()
            flash("Registration failed. Please try again.")
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):

            session["user_id"] = user.user_id

            flash("Login successful!")

            return redirect(url_for("dashboard"))

        else:
            flash("Invalid email or password. Please try again.")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")



@app.route("/api/sos", methods=["POST"])
def trigger_sos():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Location data is missing."
        }), 400

    try:
        latitude = float(data.get("latitude"))
        longitude = float(data.get("longitude"))

        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValueError("Invalid coordinates")

    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid location coordinates."
        }), 400

    # Save SOS alert in MySQL
    new_alert = SOSAlert(
        user_id=session["user_id"],
        latitude=latitude,
        longitude=longitude
    )

    db.session.add(new_alert)
    db.session.commit()

    # Retrieve the user's emergency contacts
    contacts = EmergencyContact.query.filter_by(
        user_id=session["user_id"]
    ).all()

    email_sent = 0
    email_failed = 0

    # Send emergency emails
    for contact in contacts:
        if contact.email:
            result = send_emergency_email(
                contact.email,
                latitude,
                longitude
            )

            if result:
                email_sent += 1
            else:
                email_failed += 1

    return jsonify({
        "success": True,
        "message": "SOS alert recorded successfully.",
        "latitude": latitude,
        "longitude": longitude,
        "alert_id": new_alert.alert_id,
        "emails_submitted": email_sent,
        "emails_failed": email_failed
    }), 201




@app.route("/api/latest-sos", methods=["GET"])
def latest_sos():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    alert = SOSAlert.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        SOSAlert.alert_id.desc()
    ).first()

    if not alert:
        return jsonify({
            "success": False,
            "message": "No SOS location recorded yet."
        }), 404

    # Retrieve the latest live location for this SOS alert
    live_location = LiveLocation.query.filter_by(
        alert_id=alert.alert_id,
        user_id=session["user_id"]
    ).order_by(
        LiveLocation.updated_at.desc()
    ).first()

    # Use latest live coordinates if available
    if live_location:
        latitude = float(live_location.latitude)
        longitude = float(live_location.longitude)
    else:
        # Otherwise use the original SOS coordinates
        latitude = float(alert.latitude)
        longitude = float(alert.longitude)

    return jsonify({
        "success": True,
        "latitude": latitude,
        "longitude": longitude,
        "status": alert.status,
        "created_at": (
            alert.created_at.isoformat()
            if alert.created_at else None
        ),
        "location_updated_at": (
            live_location.updated_at.isoformat()
            if live_location and live_location.updated_at else None
        )
    }), 200




@app.route("/history")
def sos_history():

    if "user_id" not in session:
        return redirect(url_for("login"))

    alerts = SOSAlert.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        SOSAlert.created_at.desc()
    ).all()

    return render_template(
        "history.html",
        alerts=alerts
    )



@app.route("/api/live-location", methods=["POST"])
def update_live_location():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Location data is missing."
        }), 400

    try:
        alert_id = int(data.get("alert_id"))
        latitude = float(data.get("latitude"))
        longitude = float(data.get("longitude"))

        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValueError("Invalid coordinates")

    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid location data."
        }), 400

    alert = SOSAlert.query.filter_by(
        alert_id=alert_id,
        user_id=session["user_id"],
        status="Active"
    ).first()

    if not alert:
        return jsonify({
            "success": False,
            "message": "Active SOS alert not found."
        }), 404

    location = LiveLocation.query.filter_by(
        alert_id=alert_id,
        user_id=session["user_id"]
    ).first()

    if location:
        location.latitude = latitude
        location.longitude = longitude
    else:
        location = LiveLocation(
            alert_id=alert_id,
            user_id=session["user_id"],
            latitude=latitude,
            longitude=longitude
        )
        db.session.add(location)

    try:
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Live location updated successfully."
        }), 200

    except Exception as e:
        db.session.rollback()
        print("Live location error:", e)

        return jsonify({
            "success": False,
            "message": "Could not update live location."
        }), 500



@app.route("/api/stop-sos", methods=["POST"])
def stop_sos():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    data = request.get_json(silent=True) or {}

    try:
        alert_id = int(data.get("alert_id"))
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid alert ID."
        }), 400

    alert = SOSAlert.query.filter_by(
        alert_id=alert_id,
        user_id=session["user_id"],
        status="Active"
    ).first()

    if not alert:
        return jsonify({
            "success": False,
            "message": "Active SOS alert not found."
        }), 404

    try:
        alert.status = "Resolved"
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "SOS alert resolved successfully."
        }), 200

    except Exception as e:
        db.session.rollback()
        print("Stop SOS error:", e)

        return jsonify({
            "success": False,
            "message": "Unable to resolve SOS alert."
        }), 500


@app.route("/api/journeys/start", methods=["POST"])
def start_journey():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Journey details are missing."
        }), 400

    start_location = data.get("start_location", "").strip()
    destination = data.get("destination", "").strip()

    if not start_location or not destination:
        return jsonify({
            "success": False,
            "message": "Enter both locations."
        }), 400

    try:
        journey = Journey(
            user_id=session["user_id"],
            start_location=start_location,
            destination=destination,
            share_token=secrets.token_urlsafe(32),
            status="Active"
        )

        db.session.add(journey)
        db.session.commit()

        share_url = url_for(
            "track_journey",
            token=journey.share_token,
            _external=True
        )

        contacts = EmergencyContact.query.filter_by(
            user_id=session["user_id"]
        ).all()

        email_sent = 0

        for contact in contacts:

            if contact.email:

                message = f"""
HERSHIELD - SAFE JOURNEY NOTIFICATION

A woman using HerShield has started sharing her journey with you.

Starting Point: {start_location}

Destination: {destination}

Click the link below to view her latest location:

{share_url}

You can use this link while the journey is active.

HerShield Safe Journey Notification.
"""

                if send_journey_email(
                    contact.email,
                    "HerShield - Safe Journey Started",
                    message
                ):
                    email_sent += 1

        return jsonify({
            "success": True,
            "journey_id": journey.journey_id,
            "share_url": share_url,
            "email_sent": email_sent,
            "message": "Journey started successfully."
        }), 201

    except Exception as e:
        db.session.rollback()

        import traceback

        print("\n========== JOURNEY START ERROR ==========")
        traceback.print_exc()
        print("=========================================\n")

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route("/api/journeys/location", methods=["POST"])
def update_journey_location():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    data = request.get_json() or {}

    try:
        journey_id = int(data.get("journey_id"))
        latitude = float(data.get("latitude"))
        longitude = float(data.get("longitude"))

        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValueError("Invalid coordinates")

    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid location data."
        }), 400

    journey = Journey.query.filter_by(
        journey_id=journey_id,
        user_id=session["user_id"],
        status="Active"
    ).first()

    if not journey:
        return jsonify({
            "success": False,
            "message": "Active journey not found."
        }), 404

    location = JourneyLocation.query.filter_by(
        journey_id=journey_id
    ).first()

    if location:
        location.latitude = latitude
        location.longitude = longitude
    else:
        location = JourneyLocation(
            journey_id=journey_id,
            latitude=latitude,
            longitude=longitude
        )
        db.session.add(location)

    try:
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Journey location updated."
        }), 200

    except Exception as e:
        db.session.rollback()
        print("Journey location error:", e)

        return jsonify({
            "success": False,
            "message": "Could not update journey location."
        }), 500


@app.route("/api/journeys/end", methods=["POST"])
def end_journey():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    data = request.get_json() or {}

    try:
        journey_id = int(data.get("journey_id"))
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid journey ID."
        }), 400

    journey = Journey.query.filter_by(
        journey_id=journey_id,
        user_id=session["user_id"],
        status="Active"
    ).first()

    if not journey:
        return jsonify({
            "success": False,
            "message": "Active journey not found."
        }), 404

    journey.status = "Ended"

    try:
        db.session.commit()

        contacts = EmergencyContact.query.filter_by(
            user_id=session["user_id"]
        ).all()

        for contact in contacts:
            if contact.email:
                send_journey_email(
                    contact.email,
                    "HerShield - Journey Ended",
                    f"""
The HerShield Safe Journey has ended.

Starting Point: {journey.start_location}

Destination: {journey.destination}

Live location sharing has been stopped.

This is an automated notification from HerShield.
"""
                )

        return jsonify({
            "success": True,
            "message": "Journey ended successfully."
        }), 200

    except Exception as e:
        db.session.rollback()
        print("Journey ending error:", e)

        return jsonify({
            "success": False,
            "message": "Could not end journey."
        }), 500   


@app.route("/journey/track/<token>")
def track_journey(token):

    journey = Journey.query.filter_by(
        share_token=token,
        status="Active"
    ).first()

    if not journey:
        return "This journey has ended or the tracking link is invalid.", 404

    return render_template(
        "track_journey.html",
        token=token
    )


@app.route("/api/journeys/track/<token>")
def get_shared_journey_location(token):

    journey = Journey.query.filter_by(
        share_token=token,
        status="Active"
    ).first()

    if not journey:
        return jsonify({
            "success": False,
            "message": "Journey has ended."
        }), 404

    location = JourneyLocation.query.filter_by(
        journey_id=journey.journey_id
    ).first()

    if not location:
        return jsonify({
            "success": False,
            "message": "Waiting for the first GPS location."
        }), 404

    return jsonify({
        "success": True,
        "latitude": float(location.latitude),
        "longitude": float(location.longitude),
        "updated_at": (
            location.updated_at.isoformat()
            if location.updated_at else None
        )
    }), 200
    



@app.route("/contacts", methods=["GET", "POST"])
def contacts():

    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        relationship = request.form.get("relationship", "").strip()
        email = request.form.get("email", "").strip()

        if not name or not phone or not relationship or not email:
            flash("Please fill in all the fields.")
            return redirect(url_for("contacts"))

        if not phone.isdigit() or not 7 <= len(phone) <= 15:
            flash("Please enter a valid phone number.")
            return redirect(url_for("contacts"))

        new_contact = EmergencyContact(
            user_id=session["user_id"],
            name=name,
            phone=phone,
            relationship=relationship,
            email=email
        )

        db.session.add(new_contact)
        db.session.commit()

        flash("Emergency contact added successfully!")
        return redirect(url_for("contacts"))

    saved_contacts = EmergencyContact.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        EmergencyContact.contact_id.desc()
    ).all()

    return render_template(
        "contacts.html",
        contacts=saved_contacts
    )



@app.route("/contacts/edit/<int:contact_id>", methods=["GET", "POST"])
def edit_contact(contact_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    contact = EmergencyContact.query.filter_by(
        contact_id=contact_id,
        user_id=session["user_id"]
    ).first_or_404()

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        relationship = request.form.get("relationship", "").strip()

        if not name or not phone or not relationship:
            flash("Please fill in all the fields.")
            return redirect(
                url_for("edit_contact", contact_id=contact_id)
            )

        if not phone.isdigit() or not 7 <= len(phone) <= 15:
            flash("Please enter a valid phone number.")
            return redirect(
                url_for("edit_contact", contact_id=contact_id)
            )

        contact.name = name
        contact.phone = phone
        contact.relationship = relationship

        db.session.commit()

        flash("Contact updated successfully!")
        return redirect(url_for("contacts"))

    return render_template(
        "edit_contact.html",
        contact=contact
    )


@app.route("/contacts/delete/<int:contact_id>", methods=["POST"])
def delete_contact(contact_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    contact = EmergencyContact.query.filter_by(
        contact_id=contact_id,
        user_id=session["user_id"]
    ).first_or_404()

    db.session.delete(contact)
    db.session.commit()

    flash("Contact deleted successfully!")
    return redirect(url_for("contacts"))


@app.route("/safe-journey")
def safe_journey():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("safe_journey.html")



if __name__ == "__main__":

    with app.app_context():
        db.create_all
        
    app.run(debug=True)

   