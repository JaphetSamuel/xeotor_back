from fastapi import FastAPI, Query, HTTPException, Depends, Header
from client.models.models import Client, Commande,  Payment, Trajet
from client.models.utils import get_trajet_info
from pydbantic import Database
from typing import  Optional, List
from fastapi_events.dispatcher import dispatch
from fastapi_events.middleware import EventHandlerASGIMiddleware
from fastapi_events.handlers.local import local_handler
from client.depends.auth_depends import check_client
from client.routes.commande_routes import route as commande_routes
from utils.distance import Coord
from client.depends.auth_depends import check_client

app = FastAPI()
app.include_router(commande_routes)

tables = [
            Client,
            Commande,
            Trajet,
            Payment
        ]


@app.post("/register")
async def register_client(client: Client):
    print("nouveau client")
    await client.insert()
    return client


@app.get('/all', response_model=list[Client])
async def get_all():
    dispatch("driver_online",{"val":True})
    return await Client.all()

@app.post('/')
async def get_client_by_id(client:Client = Depends(check_client)):
    return client





#point de depart
@app.post("/request_trajet")
async def request_trajet(dep_lng:float, dep_lat:float, des_lng:float, des_lat:float):

    polygone,distance,duration, dep,des  =  get_trajet_info(dep_lng,dep_lat,des_lng,des_lat)
    data =  {"polygone":polygone,
            "distance":distance,
            "duration":duration,
            "depart":dep,
            "destination":des
            }
    # création du trajet
    try:
        trajet = Trajet(
            polygone=polygone,
            total_distance=distance,
            total_duration=duration,
        )
        await trajet.insert()
        prix_share, prix_prive, prix_luxe = trajet.calcule_prix()

        print(type(prix_share))

        data["prix_prive"] = prix_prive
        data["prix_share"] = prix_share
        data["prix_luxe"] = prix_luxe
        data["trajet_id"] = trajet.id
    except TypeError as t:
        print("erreur de type", t.args)
    except Exception as e:
        print("erreur")
    return data

@app.post('/commande', tags=["commande"])
async def create_commande(trajet_id:str,flavour:str=Query(None), client:Client = Depends(check_client)):
    trajet = await Trajet.get(id=trajet_id)
    commande = Commande(trajet=trajet)
    commande.client = client
    await commande.set_prix()
    await commande.insert()

    #creation d'un objet coord
    #et enregistrement de la commande dans la base de donne redis

    #propagation de la nouvelle commande
    dispatch("new_commande",commande.json())
    return commande

@app.post("/trajet", response_model=Trajet, tags=["trajets"])
async def create_trajet(trajet:Trajet):
    trajet_db = await trajet.insert()
    return trajet

@app.get("/trajet", response_model=List[Trajet], tags=["trajets"])
async def get_all_trajet():
    return await Trajet.all()

