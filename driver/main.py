from fastapi import FastAPI,HTTPException,Header,Body, Depends, UploadFile, File
from fastapi.responses import HTMLResponse
from typing import List
from broadcaster import Broadcast
from fastapi_events.dispatcher import dispatch
from driver.models.models import Driver
from driver.depends.auth import check_driver, case_driver_exist
from fastapi_socketio import SocketManager
from fastapi_events.handlers.local import local_handler
from fastapi_events.typing import Event
from utils.distance import Coord
from client.models.models import Commande, Client

app =FastAPI()

socket_manager = SocketManager(app)

tables = [
    Driver
]

async def check_driver(driver_id:str = Header(...)):
    driver = await Driver.get(id=driver_id)
    if driver is None:
        raise HTTPException(401, detail="utilisazteur introuvable")
    return driver

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <button onclick="changer()" value="online"/> on </button>
        <button onclick="accept()"/> accepte commande </button>
        <span id="nc"> none </span> 
        
        <ul id='messages'>
        </ul>
        <script src="https://cdn.socket.io/4.4.1/socket.io.min.js" integrity="sha384-fKnu0iswBIqkjxrhQCTZ7qlLHOFEgNkRmK2vaO/LbTZSXdJfAu6ewRBdwHPhBo/H" crossorigin="anonymous"></script>
        <script src="/static/index.js"></script>
    </body>
</html>
"""

@app.get("/index")
async def view():
    return HTMLResponse(html)

@app.get("/")
async def driver_token(driver:Driver=Depends(check_driver)):
    return driver

@app.post("/create_driver", tags=["crud"], dependencies=[Depends(case_driver_exist)] )
async def create_driver(driver:Driver):
    await driver.insert()

    return await Driver.get(Driver.email==driver.email)
    #verifification des information
    #envoi de mail de confirmation



@app.get("/driver")
async def get_all_drivers():
    return await Driver.all()


#####################################################################################
#####################################################################################
#####################################################################################
@app.post("/mark_as_online")
async def mark_as_online(val:bool, driver: Driver = Depends(check_driver)):
    driver.is_online = val

    try:
        await driver.update()
        dispatch("driver_online",payload={"driver_id":driver.id})
        return True
    except Exception as e:
        print(e.args)
        return False

@local_handler.register(event_name="driver_online")
async def handle_driver_online(event:Event):
    ev_name, payload = event
    print(f"event reçu {ev_name}")
    Coord(payload['longitude'], payload['latitude'], payload['sid'],payload['driver_id'])



##########################################################################################
##########################################################################################
##########################################################################################





