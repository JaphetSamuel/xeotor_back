from math import radians, cos, sin, asin, sqrt

from redis import Redis

r = Redis(host="localhost", port=7777)

class Coord():

    def __init__(self, longitude:float, latitude:float, sid:str,id:str ):
        self._longitude = longitude
        self._latitude = latitude
        self.sid = sid
        self.id = id

        values = [longitude[0], latitude, sid]

        res = r.geoadd(name="coord",values=values, nx=True, ch=True)
        print(f"element enregistrer en db redis {res}")

    @classmethod
    def add(cls, longitude:float, latitude:float, member:str):

        values = [longitude[0], latitude, member]

        print(values)
        res = r.geoadd(name="coord",values=values, xx=True, ch=True)
        print("retour de GEOADD ",res)

    @classmethod
    def dist(cls, member1, member2):
        res = r.geodist(name="coord", place1=member1, place2=member2)
        print(res)






def calcule_distance(lat1, lat2, lon1, lon2):
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    c = 2 * asin(sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371

    # calculate the result
    return (c * r)


# # driver code
# lat1 = 53.32055555555556
# lat2 = 53.31861111111111
# lon1 = -1.7297222222222221
# lon2 = -1.6997222222222223
# print(distance(lat1, lat2, lon1, lon2), "K.M")