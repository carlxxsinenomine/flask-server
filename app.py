from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from dotenv import load_dotenv

from handlers.email_handler import EmailManager
from handlers.weather_handler import WeatherHandler
from threading import Thread
import traceback
import os
# RESTful API example
# @app.route('/articles', methods=['GET'])          # Get all articles
# @app.route('/articles', methods=['POST'])         # Create new article
# @app.route('/articles/<id>', methods=['GET'])     # Get specific article
# @app.route('/articles/<id>', methods=['PUT'])     # Update entire article
# @app.route('/articles/<id>', methods=['PATCH'])   # Update part of article
# @app.route('/articles/<id>', methods=['DELETE'])  # Delete article
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


def send_email_async(fence_name):
    """Send email in background thread"""
    try:
        email_manager = EmailManager()
        email_manager.create_message(f"You're inside {fence_name}")
        email_manager.send_alert_email()
        print(f"✓ Email sent successfully for {fence_name}")
    except Exception as e:
        print(f"✗ Email sending failed: {e}")
        traceback.print_exc()


@app.route('/log-alert-event', methods=['POST'])
def log_alert_event():
    try:
        data = request.json

        # Validate input
        if not data or 'userId' not in data or 'fenceName' not in data:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        # Save to database first
        document = {
            "user_id": data['userId'],
            "time_stamp": data.get('timestamp'),
            "fence_name": data['fenceName']
        }
        result = event_log.insert_one(document)

        # Send email in background thread (non-blocking)
        email_thread = Thread(
            target=send_email_async,
            args=(data['fenceName'],),
            daemon=True  # Thread will close when main program exits
        )
        email_thread.start()

        # Return immediately without waiting for email
        return jsonify({
            "success": True,
            "id": str(result.inserted_id),
            "message": "Alert logged, email being sent"
        }), 200

    except Exception as e:
        print(f"Error in log_alert_event: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Railway"""
    return jsonify({"status": "healthy"}), 200


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