import json

from fastapi import FastAPI, Body, Query
from driver.main import app as driver_app, tables as driver_tables
from client.main import app as client_app, tables as client_tables
from fastapi_events.middleware import EventHandlerASGIMiddleware
from fastapi_events.handlers.local import local_handler
from fastapi_events.dispatcher import dispatch
from fastapi_events.typing import Event
from fastapi.middleware.cors import CORSMiddleware
from client.models.models import Commande, Trajet, Client
from driver.models.models import Driver
from utils.distance import calcule_distance, Coord
from fastapi.staticfiles import StaticFiles
from sqlalchemy import MetaData

from pydbantic import Database
from  fastapi_socketio import SocketManager
app = FastAPI()
app.add_middleware(EventHandlerASGIMiddleware,handlers=[local_handler])
# app.add_middleware(CORSMiddleware,allow_origins=[])
socket_manager = SocketManager(app)
@app.on_event("startup")
async def init_db():
    # pass
    print("initialisaztion de la bd")
    try:
        db = await Database.create(
            "sqlite:///./xeotor.db",
            tables=client_tables + driver_tables,
            redis_url="redis://localhost"
        )
    except Exception as e:
        print("erreur d'initialisationde la bd")
        print(e)
        print(e.args)


app.mount("/driver", driver_app)
app.mount("/client",client_app)
app.mount('/static', StaticFiles(directory="statics"), name="static")



@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.sio.on("connection")
async def on_connect(sid, *args, **kwargs):
    print("utli connec")



@local_handler.register(event_name="new_commande")
async def send_new_commande(event:Event):
    ev_name, payload = event
    print(payload)

    print("envoi de la commande aux drivers connectes")

    await socket_manager.emit("request_position", data=payload)




sid_list:dict = {}

@app.sio.on("position_driver")
async def handle_driver_position(sid, *args,**kwargs):
    print(f"{sid}")
    response_data: dict = args[0]
    if not sid_list.keys().__contains__(sid) :
        print("id driver :", response_data) #REMOVE
        # sid_list[sid] = response_data['id']
        # print(sid_list)
    print(response_data['commande'])
    commande = Commande.parse_raw(b=response_data['commande'])

    distance = calcule_distance(
            commande.trajet.depart[0],
            response_data['lat'],
            commande.trajet.depart[1],
            response_data['lng'])

    await socket_manager.emit("new_commande_send",data=commande.json())

@app.sio.on("driver_actual_position")
async def actual_position(sid, *args, **kwargs):
    print(f"argument reçu {args[0]}")
    data = args[0]
    lng =data["lng"]
    lat = data['lat']
    id=data['id']
    commande_id = data['id_commande']
    commande:Commande = await Commande.get(id=commande_id)
    if commande and commande.statut != "aborted" and commande.driver==id:
        print("envoi de la position au client")
        await socket_manager.emit(f"position_driver_{commande.client.id}",
                                  {"lng":lng, "lat":lat}
                                  )
    else:
        print(f"commande non envoyé commande _driver_id ={commande.driver.id}")

    # try:
    #     Coord.add( longitude=lng, latitude=lat, member=sid)
    # except Exception as e:
    #     print(e.args)

# A mettre dans les hander du client
@local_handler.register(event_name="commande_accepted")
async def handle_commande_accept(event:Event):
    ev_name, payload = event
    print("######################### commande recu dans dispacth #########")
    print(payload)


@app.sio.on("accept_commande")
async def socket_accept_commande(sid, *args, **kwargs):
    #lorsque le driver a accepté la commande
    data = args[0]
    print("commande accepteé par le driver")
    print(data)
    commande:Commande = await Commande.get(id=data['id_commande'])
    commande.driver = data['id_driver']
    await commande.update()
    print(commande)
    print(data['id_driver'])
    driver = await Driver.get(id=data['id_driver'])
    trajet = await Trajet.get(id=commande.trajet.id)
    print(f"commande_accepted_ {commande.json()}")
    await socket_manager.emit(f"commande_accepted_{data['id_client']}", {'commande': commande.json(), 'driver': driver.json(), 'trajet':trajet.json()})
    print("envoyé")
    dispatch("commande_accepted", data)



@app.post('/update_state')
async def update_driver_state(state:str=Body(...), id_commande:str=Body(...)):
    print('action du driver')
    commande = await Commande.get(id=id_commande)
    client_id = commande.client.id
    if state == "arrived":
        print('arriver arrivé')
        await socket_manager.emit(f"status_driver_{client_id}", {"data":"arrived"})
    if state == "begin":
        print('driver demare')
        await socket_manager.emit(f"status_driver_{client_id}", {"data": "begin"})
    if state == "end":
        print('driver end')
        await socket_manager.emit(f"status_driver_{client_id}", {"data":"end"})

@app.sio.on('driver_online')
async def socket_handle_position(sid,*args, **kwargs):
    print(args)
    data = args[0]
    data['sid'] = sid
    dispatch('driver_online',payload=data)

@app.post('/abort_commande')
async def handle_abord_commande(commande_id:str):
    print("annulation de la commande par le client")
    #dispatch("")
    commande = await Commande.get(id=commande_id)
    if commande:
        commande.statut = "aborted"
        await commande.update()

    if commande.driver:
        print(commande.driver)
        print(f"commande_abort_{commande.driver}")
        await socket_manager.emit(f"commande_abort_{commande.driver}")
    else:
        print("aucun driver sur la commande")
    return {"ok":"ok"}



