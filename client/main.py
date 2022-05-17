from fastapi import FastAPI, Query, HTTPException, Depends, Header, Body, Form, Request
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
    try:
        await client.insert()
    except Exception as e:
        print("erreur de d'enregstrement dans la bd")
        print(e.args)
    return client


@app.get('/all', response_model=list[Client])
async def get_all():
    dispatch("driver_online",{"val":True})
    return await Client.all()

@app.post('/')
async def get_client_by_id(client:Client = Depends(check_client)):
    return client



async def print_request(request:Request):
    print(request.base_url)
    print(await request.body())

#point de depart
@app.post("/requesttrajet", dependencies=[Depends(print_request)])
async def request_trajet(dep_lng:float = Body(...),
                         dep_lat:float = Body(...),
                         des_lng:float=Body(...),
                         des_lat:float=Body(...),
                         dep_name:str = Body(...),
                         des_name:str = Body(...)
                         ):

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
            depart = dep,
            destination = des,
            dep_name = dep_name,
            des_name = des_name
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
async def create_commande(trajet_id:str = Body(...),flavour:str=Body("share"), client:Client = Depends(check_client)):
    trajet = await Trajet.get(id=trajet_id)
    commande = Commande(trajet=trajet)
    commande.client = client
    commande.flavour = flavour
    await commande.set_prix()
    try :
        await commande.insert()
    except Exception as e:
        print("exeption ici")
        print(e.args)

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

@app.post("/cancelcommande")
async def handle_cancel_commande(id:str = Body(...)):
    commande = await Commande.exists().get(id=id)
    commande.statut = "canceled"
    dispatch("commande_canceled", payload=id)
    await commande.update()
    return True

