# tools.py
import os
from crewai.tools import tool
from graphh import GraphHopper
from dotenv import load_dotenv

load_dotenv()

# Initialize GraphHopper client with your API key
mapper = GraphHopper(api_key=os.getenv("GRAPHHOPPER_API_KEY"))

@tool("get_city_distance")
def get_city_distance(
    starting_address: str,
    destination_address: str,
    mode_of_transport: str = "car",  # car, bike, foot
    given_unit: str = "km"
) -> float:
    """
    Returns the distance between two addresses using GraphHopper API.

    Parameters:
    - starting_address: str, origin address
    - destination_address: str, destination address
    - mode_of_transport: str, vehicle type ('car', 'bike', 'foot')
    - given_unit: str, 'km' or 'miles'

    Returns:
    - float: distance between two locations in the requested unit
    - str: 'Distance not found' if geocoding or routing fails
    """
    try:
        # Convert addresses to lat/long
        origin = mapper.address_to_latlong(starting_address)
        destination = mapper.address_to_latlong(destination_address)
        print("Origin:", origin)
        print("Destination:", destination)

        if not origin or not destination:
            return "Distance not found"

        # Get the route using the selected vehicle
        route_data = mapper.route([origin, destination], vehicle=mode_of_transport)

        # Extract distance in meters from the first path
        distance_meters = route_data['paths'][0]['distance']

        # Convert to km or miles
        if given_unit.lower() == "km":
            distance = distance_meters / 1000
        elif given_unit.lower() == "miles":
            distance = (distance_meters / 1000) * 0.621371
        else:
            distance = distance_meters / 1000  # default km

        return round(distance, 2)

    except Exception as e:
        print("Distance calculation error:", e)
        return "Distance not found"