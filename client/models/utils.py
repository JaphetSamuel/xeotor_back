from .models import Commande,  Payment, Trajet
import openrouteservice
from openrouteservice import convert



OPENROUTE_API_KEY = "5b3ce3597851110001cf624847c04846b3e44081a26b2fc5a8332ef8"


def get_trajet_info(ax,ay,bx,by):

    client = openrouteservice.Client(key=OPENROUTE_API_KEY)

    routes = client.directions(
        ((ax,ay),(bx,by)),
    )

    geometry = routes['routes'][0]['geometry']
    segments = routes['routes'][0]['segments'][0]
    bbox = routes['routes'][0]['bbox']
    decoded = convert.decode_polyline(geometry)

    depart: list[float] = [bbox[0],bbox[1]]
    destination: list[float] = [bbox[2],bbox[3]]
    polygone = decoded['coordinates']
    distance = segments['distance']
    duration = segments['duration']
    print(routes)
    print(distance)
    return polygone, distance, duration, depart,destination
