from pymongo import MongoClient
from dotenv import load_dotenv
from handlers.weather_handler import WeatherHandler
import os
import time
import schedule

load_dotenv()

# MongoDB connection
try:
    client = MongoClient(
        os.getenv("MONGODB_URI"),
        tlsAllowInvalidCertificates=True
    )
    client.admin.command('ping')
    print("✓ MongoDB connection successful!")
except Exception as e:
    print(f"✗ MongoDB connection failed: {e}")
    raise

geo_db = client[os.getenv("MONGODB_DATABASE")]
drawn_shapes = geo_db.shapes
weather_info = WeatherHandler()


def get_coordinates_info(lat, lng):
    coordinates_info = weather_info.get_coordinates_info(lat=lat, long=lng)
    return coordinates_info.get("state_province", None)


def check_weather_advisory(lat, lng):
    coordinates_info = get_coordinates_info(lat, lng)
    panahon_data = weather_info.get_panahon_advisory(coordinates_info)
    data = [advisory for key, advisory in panahon_data.items() if advisory]
    print(f"data: {data}")
    if len(data) > 0:
        return data
    return False


# Hourly threshold:
# Yellow warning: 7.5 mm to 15 mm in one hour.
# Orange warning: 15 mm to 30 mm in one hour.
# Red warning: More than 30 mm in one hour.
# https://water.usgs.gov/edu/activity-howmuchrain-metric.html#:~:text=Slight%20rain:%20Less%20than%200.5,than%2050%20mm%20per%20hour.
def check_precipitation(lat, lng):
    current_weather = weather_info.get_current_forecast(lat, lng)
    return {'weather_condition': current_weather['condition']['text'], 'precipitation': current_weather['precip_mm']}



def fence_activation():
    try:
        print("Starting fence activation check...")
        for document in drawn_shapes.find():
            try:
                coordinates = document.get('geometry', {}).get('coordinates', [])
                shape_type = document.get('geometry', {}).get('type', None)

                if coordinates and len(coordinates) > 0:
                    shape_t = None
                    if shape_type == "Polygon":
                        shape_t = coordinates[0]
                    elif shape_type == "Point":
                        shape_t = [[coordinates[0], coordinates[1]]]

                    if shape_t and len(shape_t) > 0:
                        first_coordinate = shape_t[0]
                        if first_coordinate and len(first_coordinate) >= 2:
                            lng = first_coordinate[0]  # longitude
                            lat = first_coordinate[1]  # latitude

                            print(f"Checking shape {document.get('_id')} at coordinates: {lat}, {lng}")

                            # Check for weather advisory
                            advisory = check_weather_advisory(lat, lng)
                            current_weather = check_precipitation(lat, lng)
                            perci_level = current_weather.get('precipitation', 0.0)

                            # Update is_active inside properties based on advisory
                            if advisory or perci_level > 7.5:  # yellow rainfall warning
                                drawn_shapes.update_one(
                                    {'_id': document['_id']},
                                    {'$set': {'properties.is_active': True}}
                                )
                                print(f"✓ Activated fence {document.get('_id')} - Advisory found")
                            else:
                                # Deactivate fence if no advisory
                                drawn_shapes.update_one(
                                    {'_id': document['_id']},
                                    {'$set': {'properties.is_active': False}}
                                )
                                print(f"✗ Deactivated fence {document.get('_id')} - No advisory")

            except Exception as e:
                print(f"Error processing document {document.get('_id')}: {str(e)}")
                continue

        print("Fence activation check completed!")
    except Exception as e:
        print(f"Error in fence_activation: {str(e)}")


if __name__ == '__main__':
    print("Worker started - Running fence activation every minute (TESTING MODE)")

    # Schedule the job every minute for testing
    schedule.every(1).minutes.do(fence_activation)

    # Run immediately on startup
    fence_activation()

    # Keep the worker running
    while True:
        schedule.run_pending()
        time.sleep(10)  # Check every 10 seconds