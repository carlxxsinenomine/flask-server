from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from dotenv import load_dotenv

from handlers.email_handler import EmailManager
from handlers.weather_handler import WeatherHandler
from threading import Thread
from datetime import datetime, timedelta, timezone
import traceback
import os

load_dotenv()

app = Flask(__name__)
weather_info = WeatherHandler()

CORS(app)  # Enable CORS for browser requests

# Fixed MongoDB connection with TLS certificate validation bypass
try:
    client = MongoClient(
        os.getenv("MONGODB_URI"),
        tlsAllowInvalidCertificates=True
    )
    # Test the connection
    client.admin.command('ping')
    print("✓ MongoDB connection successful!")
except Exception as e:
    print(f"✗ MongoDB connection failed: {e}")
    raise

geo_db = client[os.getenv("MONGODB_DATABASE")]
user_trail = geo_db[os.getenv("MONGODB_COLLECTION")]
event_log = geo_db[os.getenv("EVENT_LOG")]
drawn_shapes = geo_db.shapes


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Flask Geofencing API",
        "status": "running",
        "endpoints": [
            "/save-tracking (POST)",
            "/log-alert-event (POST)",
            "/health (GET)"
        ]
    })


@app.route('/save-tracking', methods=['POST'])
def save_tracking():
    data = request.json
    document = {
        "type": data['type'],
        "properties": data['properties'],
        "geometry": data['geometry']
    }
    result = user_trail.insert_one(document)
    return jsonify({"success": True, "id": str(result.inserted_id)})


def send_email_async(fence_name, user_id):
    """Send email in background thread"""
    try:
        email_manager = EmailManager()
        email_manager.create_message(
            f"Alert: User {user_id} has entered the geofence '{fence_name}'.\n\n"
            f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
            f"Fence: {fence_name}"
        )

        success = email_manager.send_alert_email()
        if success:
            print(f"✓ Email sent successfully for fence '{fence_name}'")
        else:
            print(f"✗ Email failed to send for fence '{fence_name}'")

    except Exception as e:
        print(f"✗ Email sending failed: {e}")
        traceback.print_exc()


def should_send_email(user_id, fence_name, cooldown_minutes=5):
    """
    Check if we should send an email based on cooldown period.
    Prevents spam if user enters same fence multiple times quickly.
    """
    try:
        # Look for recent alerts from this user in this fence
        cooldown_time = datetime.now(timezone.utc) - timedelta(minutes=cooldown_minutes)

        recent_alert = event_log.find_one({
            "user_id": user_id,
            "fence_name": fence_name,
            "time_stamp": {"$gte": cooldown_time.isoformat()}
        })

        # If no recent alert found, we should send email
        return recent_alert is None

    except Exception as e:
        print(f"Error checking cooldown: {e}")
        # If error checking, send email anyway (fail-safe)
        return True


@app.route('/log-alert-event', methods=['POST'])
def log_alert_event():
    try:
        data = request.json

        # Validate input
        if not data or 'userId' not in data or 'fenceName' not in data:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        user_id = data['userId']
        fence_name = data['fenceName']
        timestamp = data.get('timestamp', datetime.now(timezone.utc).isoformat())

        print(f"📍 Alert received: user={user_id}, fence={fence_name}")

        # Save to database first
        document = {
            "user_id": user_id,
            "time_stamp": timestamp,
            "fence_name": fence_name
        }
        result = event_log.insert_one(document)

        # Get cooldown setting (set to 0 to disable for testing)
        cooldown_minutes = int(os.getenv("EMAIL_COOLDOWN_MINUTES", 5))

        # Check if we should send email (cooldown check)
        if cooldown_minutes == 0 or should_send_email(user_id, fence_name, cooldown_minutes):
            # Send email in background thread (non-blocking)
            email_thread = Thread(
                target=send_email_async,
                args=(fence_name, user_id),
                daemon=True  # Thread will close when main program exits
            )
            email_thread.start()
            message = "Alert logged, email being sent"
            print(f"📧 Starting email thread for {user_id} in {fence_name}")
        else:
            message = "Alert logged, email skipped (cooldown active)"
            print(f"⏸ Email skipped for {user_id} in {fence_name} (cooldown)")

        # Return immediately without waiting for email
        return jsonify({
            "success": True,
            "id": str(result.inserted_id),
            "message": message
        }), 200

    except Exception as e:
        print(f"Error in log_alert_event: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Railway"""
    try:
        # Test MongoDB connection
        client.admin.command('ping')
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


if __name__ == '__main__':
    try:
        # Use 0.0.0.0 to allow external connections (required for Railway)
        # Railway provides PORT env variable
        port = int(os.getenv("PORT", 5000))
        app.run(host="0.0.0.0", port=port)
    finally:
        # Ensure the MongoDB connection is closed properly
        client.close()
        print("MongoDB connection closed")