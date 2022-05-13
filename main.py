
from fastapi import FastAPI
from driver.main import app as driver_app, tables as driver_tables
from client.main import app as client_app, tables as client_tables
from fastapi_events.middleware import EventHandlerASGIMiddleware
from fastapi_events.handlers.local import local_handler
from fastapi_events.dispatcher import dispatch
from fastapi_events.typing import Event
from fastapi.middleware.cors import CORSMiddleware
from client.models.models import Commande
from utils.distance import calcule_distance, Coord
from fastapi.staticfiles import StaticFiles


from pydbantic import Database
from  fastapi_socketio import SocketManager
app = FastAPI()
app.add_middleware(EventHandlerASGIMiddleware,handlers=[local_handler])
# app.add_middleware(CORSMiddleware,allow_origins=[])
socket_manager = SocketManager(app)

@app.on_event("startup")
async def init_db():
    db = await Database.create(
        "sqlite:///./xeotor.db",
        tables=client_tables + driver_tables,
        redis_url="redis://localhost"
    )


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
    print("envoi de la commande aux drivers connectes")
    await socket_manager.emit("request_position", data=payload)




sid_list:dict = {}

@app.sio.on("position_driver")
async def handle_driver_position(sid, *args,**kwargs):
    print(f"{sid}")
    response_data: dict = args[0]
    if not sid_list.keys().__contains__(sid) :
        print("id driver :", response_data['id']) #REMOVE
        sid_list[sid] = response_data['id']
        print(sid_list)
    print(response_data['commande'])
    commande = Commande.parse_raw(b=response_data['commande'])

    distance = calcule_distance(
            commande.trajet.depart[0],
            response_data['lat'],
            commande.trajet.depart[1],
            response_data['lng'])

    await socket_manager.emit("new_commande_send",{"commande":commande.json(), "distance":distance})

@app.sio.on("driver_actual_position")
async def actual_position(sid, *args, **kwargs):
    print(f"argument reçu {args[0]}")
    data = args[0]
    lng:float =data["lng"],
    lat = data['lat']
    id=data['id']
    Coord.add( longitude=lng, latitude=lat, member=sid)

@app.sio.on("accept_commande")
async def socket_accept_commande(sid, *args, **kwargs):
    #lorsque le driver a accepté la commande
    data = args[0]
    print(args)
    print("commande accepteé par le driver")
    dispatch(f"commande_accepted", data)


@app.sio.on('driver_online')
async def socket_handle_position(sid,*args, **kwargs):
    print(args)
    data = args[0]
    data['sid'] = sid
    dispatch('driver_online',payload=data)



