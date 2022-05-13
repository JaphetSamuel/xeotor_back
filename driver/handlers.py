from fastapi_events.handlers.local import local_handler
from fastapi_events.typing import Event
from utils.connection_manager import ConnectionManager
from utils.distance import Coord



# manager = ConnectionManager()
#
# @local_handler.register(event_name="new_commande")
# async def test_event(event:Event):
#     event_name, payload = event
#     print("reponse côté driver")
#     await manager.broadcast("")


@local_handler.register(event_name="driver_online")
async def handle_driver_online(event:Event):
    ev_name, payload = event
    print(f"event reçu {ev_name}")
    Coord(payload['longitude'], payload['latitude'], payload['sid'],payload['driver_id'])

